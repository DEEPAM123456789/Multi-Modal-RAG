from typing import Dict
import uuid

# In-memory job storage
jobs: Dict[str, dict] = {}

def create_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "step": 0,
        "progress": 0,
        "message": "Starting..."
    }
    return job_id

def update_job(job_id, step=None, progress=None, message=None, status=None):
    job = jobs.get(job_id)
    if not job:
        return

    if step is not None:
        job["step"] = step
    if progress is not None:
        job["progress"] = progress
    if message is not None:
        job["message"] = message
    if status is not None:
        job["status"] = status

def get_job(job_id):
    return jobs.get(job_id)
