import streamlit as st
import tempfile
import time
import json
import uuid
import gc
import os
import requests

# BACKEND_URL = "http://127.0.0.1:8000"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# from rag_pipeline import (
#     run_complete_ingestion_pipeline,
#     generate_final_answer
# )

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Multimodal PDF RAG Chatbot",
    layout="wide"
)

st.title("📄 Multimodal RAG Chatbot")
st.markdown(
    "Upload PDFs and chat with them like ChatGPT — grounded in text, tables, and images."
)

# ---------------- SESSION STATE ---------------- #

if "databases" not in st.session_state:
    st.session_state.databases = {}   # pdf_name -> db

if "active_pdf" not in st.session_state:
    st.session_state.active_pdf = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- CACHE-WRAPPED INGESTION ---------------- #
# 🔥 CRITICAL FOR WINDOWS + CHROMA STABILITY

# @st.cache_resource(show_spinner=False)
# def ingest_pdf(pdf_path, persist_directory, _progress_callback):
#     return run_complete_ingestion_pipeline(
#         pdf_path,
#         progress_callback=_progress_callback,
#         persist_directory=persist_directory
#     )

# ---------------- SIDEBAR ---------------- #

with st.sidebar:
    st.header("📥 Document Ingestion")

    uploaded_pdf = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )

    ingest_btn = st.button("🚀 Run Ingestion Pipeline", type="primary")

    if st.session_state.databases:
        st.subheader("📚 Loaded PDFs")
        st.session_state.active_pdf = st.radio(
            "Select active document:",
            list(st.session_state.databases.keys()),
            index=0
        )

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []

# ---------------- INGESTION WITH STEP-WISE PROGRESS ---------------- #

if ingest_btn:
    if not uploaded_pdf:
        st.warning("Please upload a PDF first.")
    else:
        start_time = time.time()

        with st.status("🚀 Starting ingestion pipeline...", expanded=True) as status:
            progress_bar = st.progress(0)

            # placeholders to avoid piling
            step1_ph = status.empty()
            step2_ph = status.empty()
            step3_ph = status.empty()
            step4_ph = status.empty()

            def progress_callback(payload):
                step = payload.get("step")

                if step == 1:
                    step1_ph.write(
                        "🔹 **Step 1/4**: Partitioning document (text, tables, images)"
                    )
                    progress_bar.progress(0.15)

                elif step == 2:
                    total = payload.get("total_chunks", 0)
                    step2_ph.write(
                        f"🔹 **Step 2/4**: Chunking document — **{total} chunks created**"
                    )
                    progress_bar.progress(0.35)

                elif step == 3:
                    cur = payload.get("current", 0)
                    total = payload.get("total", 1)
                    step3_ph.write(
                        f"🔹 **Step 3/4**: Generating AI summaries & embeddings "
                        f"(chunk {cur}/{total})"
                    )
                    progress_bar.progress(0.35 + (cur / total) * 0.5)

                elif step == 4:
                    step4_ph.write(
                        "🔹 **Step 4/4**: Creating vector store "
                        "(computing embeddings, building index, saving to disk)"
                    )
                    progress_bar.progress(0.95)

                elif step == 5:
                    step3_ph.write("")
                    progress_bar.progress(1.0)

            try:
                # Save uploaded PDF to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_pdf.read())
                    pdf_path = tmp.name

                # 🔥 Per-PDF isolated persist directory (NO deletion)
                persist_dir = f"dbv2/chroma_db/{uuid.uuid4()}"

                # release UI references (safe)
                st.session_state.active_pdf = None
                st.session_state.chat_history = []
                gc.collect()

                # 🔥 Cached ingestion (Windows-safe)
                ## db = ingest_pdf(
                ##     pdf_path,
                ##     persist_dir,
                ##     progress_callback
                ## )

                elapsed = int(time.time() - start_time)

                status.update(
                    label=f"✅ Document ingested",
                    state="complete"
                )

                # st.session_state.databases = {}
                # st.session_state.databases[uploaded_pdf.name] = db
                # st.session_state.active_pdf = uploaded_pdf.name

                files = {
                    "file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")
                }

                response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                data = response.json()
                job_id = data["job_id"]

                progress_bar = st.progress(0)
                status_text = st.empty()

                while True:
                    status = requests.get(f"{BACKEND_URL}/ingest/status/{job_id}").json()

                    progress_bar.progress(status["progress"])
                    status_text.write(status["message"])

                    if status["status"] == "completed":
                        st.success("✅ Document ingested!")
                        st.session_state.active_pdf = uploaded_pdf.name
                        break

                    if status["status"] == "failed":
                        st.error(status["message"])
                        break

                    time.sleep(1)

            except Exception as e:
                status.update(label="❌ Ingestion failed", state="error")
                st.error(e)

# ---------------- CHAT UI ---------------- #

st.divider()
st.header("💬 Chat with your document")

# render full chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- CHAT INPUT ---------------- #

user_query = st.chat_input("Ask a question about the document...")

if user_query:
    if not st.session_state.active_pdf:
        st.warning("Please ingest a document first.")
    else:
        # store user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_query}
        )

        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                payload = {"question": user_query}

                response = requests.post(
                    f"{BACKEND_URL}/query",
                    json=payload
                )

                if response.status_code != 200:
                    st.error(response.text)
                else:
                    data = response.json()
                    answer = data["answer"]
                    sources = data.get("sources", [])

                    st.write(answer)

                    # -------- SOURCES / CITATIONS -------- #
                    if sources:
                        with st.expander("📌 Sources & Retrieved Chunks"):
                            for src in sources:
                                st.markdown(
                                    f"**Chunk {src['chunk_id']} — {src['document']}**"
                                )

                                if src["text"]:
                                    st.write(src["text"] + "...")

                                for img_b64 in src.get("images", []):
                                    st.image(
                                        f"data:image/jpeg;base64,{img_b64}",
                                        use_container_width=True
                                    )

                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer}
                    )


                    
