from fastapi import FastAPI
from prometheus_client import generate_latest

from app.routers import tasks
from app.middleware import metrics_middleware

app = FastAPI(title="Task Tracker API")

app.middleware("http")(metrics_middleware)

app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    from starlette.responses import Response
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )