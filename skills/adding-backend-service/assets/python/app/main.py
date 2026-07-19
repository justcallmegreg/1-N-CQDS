# main.py — FastAPI app. Stateless: no module-level mutable state beyond the
# engine (a connection pool, not app state). Health is liveness; ready checks DB.
from fastapi import FastAPI
from sqlalchemy import text
from .db import engine
from .routes import router

app = FastAPI(title="1-N-CQDS service")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/ready")
def ready():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready"}
