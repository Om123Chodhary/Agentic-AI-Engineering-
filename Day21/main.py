from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from schemas import ChatRequest, ChatResponse
from agent import run_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Research AI Application...")
    yield
    print("Shutting down Research AI Application...")

app = FastAPI(
    title="Research AI Agent",
    version="1.0.0",
    lifespan=lifespan
)

# 1. Frontend ko serve karne ke liye static files mount karein
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 2. Home Page Endpoint
@app.get("/")
async def home():
    # Jab user root URL kholenge, toh index.html dikhao
    return FileResponse("frontend/index.html")

# 3. Health Check (Jo humne Day 20 mein seekha)
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model =ChatResponse)
async def chat(request:ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code = 400,
            detail="Message Cannot Be Empty."
        )
    try:
        result = await run_agent(request.message)
        return ChatResponse(response=result)
    except Exception as exc:
        raise HTTPException(
            status_code = 500,
            detail ="Agent Execution Failed."
        ) from exc
