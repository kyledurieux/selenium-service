import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from my_script import run_task

API_TOKEN = os.getenv("API_TOKEN", "CHANGE_ME_123")

app = FastAPI(title="Selenium Runner")

@app.get("/healthz")
def healthz():
    # lightweight liveness check for load balancers/monitors
    return {"status": "ok"}

class RunRequest(BaseModel):
    url: str

@app.post("/run")
def run(req: RunRequest, authorization: str | None = Header(None)):
    # simple auth check
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        result = run_task(req.url)
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import logging

# Basic file logging setup (creates app.log in the container)
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response
