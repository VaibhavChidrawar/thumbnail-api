from fastapi import FastAPI

app = FastAPI(
    title="Thumbnail API",
    description="Long-running thumbnail generation API using RQ",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}
