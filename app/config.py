import os

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

# Redis URL genartaion
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Storage paths
DATA_DIR = os.getenv("DATA_DIR", "/app/storage")

ORIGINALS_DIR = f"{DATA_DIR}/originals"
THUMBNAILS_DIR = f"{DATA_DIR}/thumbnails"