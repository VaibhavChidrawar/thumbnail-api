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
        logger.info(f"Starting thumbnail generation for job {job_id}")
        redis_conn.hset(job_key, "status", "processing")

        # Simulate long-running job
        time.sleep(30)

        # Open image
        with Image.open(original_path) as img:
            img.thumbnail((100, 100))
            img.save(thumbnail_path, "PNG")

        redis_conn.hset(job_key, "status", "succeeded")
        logger.info(f"Thumbnail generated successfully for job {job_id}")

        return thumbnail_path

    except Exception as e:
        logger.exception(f"Failed to process job {job_id}")
        redis_conn.hset(job_key, "status", "failed")
        redis_conn.hset(job_key, "error", str(e))
        raise
