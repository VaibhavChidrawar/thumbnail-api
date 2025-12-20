import os
import logging
import time

from PIL import Image
from redis import Redis
from app.logging_config import setup_logging
from app.config import REDIS_URL, THUMBNAILS_DIR

setup_logging()
logger = logging.getLogger(__name__)

redis_conn = Redis.from_url(REDIS_URL)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)


def generate_thumbnail(job_id: str, original_path: str):
    job_key = f"job:{job_id}"
    thumbnail_path = f"{THUMBNAILS_DIR}/{job_id}.png"

    try:
        started_at = time.time()
        redis_conn.hset(job_key, mapping={
            "status": "processing",
            "started_at": started_at
        })

        logger.info(f"Job started job_id={job_id} started_at={started_at}")

        # Simulate long-running job
        time.sleep(30)

        # Open image
        with Image.open(original_path) as img:
            img.thumbnail((100, 100))
            img.save(thumbnail_path, "PNG")

        finished_at = time.time()
        processing_time_ms = int((finished_at - started_at) * 1000)

        redis_conn.hset(job_key, mapping={
            "status": "succeeded",
            "finished_at": finished_at,
            "processing_time_ms": processing_time_ms
        })

        logger.info(f"Job succeeded job_id={job_id} processing_time_ms={processing_time_ms}")

        return thumbnail_path

    except Exception as e:
        finished_at = time.time()
        redis_conn.hset(job_key, mapping={
            "status": "failed",
            "finished_at": finished_at,
            "error": str(e)
        })

        logger.exception(f"Job failed job_id={job_id}")
        raise
