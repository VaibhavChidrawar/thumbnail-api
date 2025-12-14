import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

DATA_DIR = os.getenv("DATA_DIR", "./app/storage")
ORIGINALS_DIR = f"{DATA_DIR}/originals"
THUMBNAILS_DIR = f"{DATA_DIR}/thumbnails"