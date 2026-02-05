from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from backend.job_manager import create_job, update_job, get_job
import tempfile
import uuid
import json
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

from backend.rag_pipeline import (
    run_complete_ingestion_pipeline,
    generate_final_answer
)
from backend import state

app = FastAPI(title="Multimodal RAG API")

def background_ingest(job_id: str, pdf_path: str, filename: str):

    def progress_callback(payload):
        step = payload.get("step")

        if step == 1:
            update_job(job_id, step=1, progress=15,
                       message="Partitioning document")

        elif step == 2:
            total = payload.get("total_chunks", 0)
            update_job(job_id, step=2, progress=35,
                       message=f"Chunking completed: {total} chunks")

        elif step == 3:
            cur = payload.get("current", 0)
            total = payload.get("total", 1)
            progress = 35 + int((cur / total) * 50)

            update_job(job_id, step=3, progress=progress,
                       message=f"Embedding chunk {cur}/{total}")

        elif step == 4:
            update_job(job_id, step=4, progress=95,
                       message="Building vector database")

    try:
        persist_dir = f"dbv2/chroma_db/{job_id}"

        db = run_complete_ingestion_pipeline(
            pdf_path,
            persist_directory=persist_dir,
            progress_callback=progress_callback
        )

        from backend import state
        state.db = db
        state.active_doc_name = filename

        update_job(job_id,
                   status="completed",
                   progress=100,
                   message="Ingestion completed")

    except Exception as e:
        update_job(job_id,
                   status="failed",
                   message=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest_pdf(background_tasks: BackgroundTasks,
                     file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    # Create job
    job_id = create_job()

    # Run ingestion in background
    background_tasks.add_task(
        background_ingest,
        job_id,
        pdf_path,
        file.filename
    )

    return {
        "job_id": job_id,
        "message": "Ingestion started"
    }

@app.get("/ingest/status/{job_id}")
def ingestion_status(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

@app.post("/query")
async def query_document(req: QueryRequest):
    question = req.question

    if state.db is None:
        raise HTTPException(status_code=400, detail="No document ingested")

    retriever = state.db.as_retriever(search_kwargs={"k": 3})
    chunks = retriever.invoke(question)

    answer = generate_final_answer(chunks, question)

    sources = []
    for i, chunk in enumerate(chunks):
        meta = json.loads(chunk.metadata.get("original_content", "{}"))
        sources.append({
            "chunk_id": i + 1,
            "document": state.active_doc_name,
            "text": meta.get("raw_text", "")[:500],
            "images": meta.get("images_base64", [])
        })

    return {
        "document": state.active_doc_name,
        "question": question,
        "answer": answer,
        "sources": sources
    }
