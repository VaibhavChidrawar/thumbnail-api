from fastapi import FastAPI
from app.routers import jobs
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Thumbnail API",
    description="Long-running thumbnail generation API using RQ",
    version="1.0.0",
)

app.include_router(jobs.router)

@app.get("/health")
def health():
    return {"status": "ok"}
