import uuid
import os
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from redis import Redis
from rq import Queue
from fastapi.responses import FileResponse
from app.config import THUMBNAILS_DIR
from app.config import ORIGINALS_DIR, REDIS_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("thumbnails", connection=redis_conn)

os.makedirs(ORIGINALS_DIR, exist_ok=True)

@router.post("/")
def submit_job(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    job_id = str(uuid.uuid4())
    original_path = f"{ORIGINALS_DIR}/{job_id}.png"

    with open(original_path, "wb") as f:
        f.write(file.file.read())

    # enqueue job (worker implementation later)
    job = queue.enqueue(
        "app.workers.tasks.generate_thumbnail",
        job_id,
        original_path
    )

    redis_conn.hset(f"job:{job_id}", mapping={
        "status": "queued",
        "rq_job_id": job.id
    })
    redis_conn.sadd("jobs", job_id)

    logger.info(f"Job submitted job_id={job_id} filename={file.filename} content_type={file.content_type}")

    return {"job_id": job_id, "status": "queued"}


@router.get("/{job_id}")
def job_status(job_id: str):
    job_key = f"job:{job_id}"
    if not redis_conn.exists(job_key):
        raise HTTPException(status_code=404, detail="Job not found")

    status = redis_conn.hget(job_key, "status").decode()
    logger.info(f"Job status requested job_id={job_id} status={status}")

    return {"job_id": job_id, "status": status}


@router.get("/")
def list_jobs():
    jobs = redis_conn.smembers("jobs")
    result = []

    for job_id in jobs:
        job_id = job_id.decode()
        status = redis_conn.hget(f"job:{job_id}", "status").decode()
        result.append({"job_id": job_id, "status": status})

    return result

@router.get("/{job_id}/thumbnail")
def get_thumbnail(job_id: str):
    job_key = f"job:{job_id}"

    if not redis_conn.exists(job_key):
        raise HTTPException(status_code=404, detail="Job not found")

    status = redis_conn.hget(job_key, "status").decode()
    if status != "succeeded":
        raise HTTPException(
            status_code=400,
            detail=f"Thumbnail not available. Job status: {status}"
        )

    thumbnail_path = f"{THUMBNAILS_DIR}/{job_id}.png"

    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=500, detail="Thumbnail file missing")

    logger.info(f"Thumbnail requested job_id={job_id}")

    return FileResponse(
        thumbnail_path,
        media_type="image/png",
        filename=f"{job_id}.png"
    )


@router.get("/{job_id}/debug")
def debug_job(job_id: str):
    job_key = f"job:{job_id}"

    if not redis_conn.exists(job_key):
        raise HTTPException(status_code=404, detail="Job not found")

    data = redis_conn.hgetall(job_key)
    return {k.decode(): v.decode() for k, v in data.items()}
