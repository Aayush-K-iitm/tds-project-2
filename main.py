from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent
from dotenv import load_dotenv
import uvicorn
import os
import time
import uuid

# -----------------------------------------------------
# Load environment variables
# -----------------------------------------------------
load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")

if SECRET is None:
    raise RuntimeError("Environment variable SECRET is missing!")

# -----------------------------------------------------
# Create FastAPI app
# -----------------------------------------------------
app = FastAPI(
    title="Solver API",
    description="Background-processing API for running agent tasks.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


# -----------------------------------------------------
# Health Check
# -----------------------------------------------------
@app.get("/healthz")
def healthz():
    """Simple liveness check."""
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - START_TIME)
    }


# -----------------------------------------------------
# Solve Endpoint
# -----------------------------------------------------
@app.post("/solve")
async def solve(request: Request, background_tasks: BackgroundTasks):
    # Parse JSON safely
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="JSON must be an object")

    url = data.get("url")
    secret = data.get("secret")

    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url'")
    if not secret:
        raise HTTPException(status_code=400, detail="Missing 'secret'")

    # Validate secret
    if secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    # Create request ID for logging
    request_id = str(uuid.uuid4())
    print(f"[{request_id}] Secret verified. Starting background task for URL: {url}")

    # Schedule the agent
    background_tasks.add_task(run_agent, url)

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "request_id": request_id,
            "message": "Task scheduled in background"
        }
    )


# -----------------------------------------------------
# Uvicorn entrypoint
# -----------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860,
        reload=False  # Set True only during development
    )
