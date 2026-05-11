import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from src.mf_faq.orchestrator.reasoning import ReasoningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="HDFC Mutual Fund FAQ Assistant API",
    description="Backend API for the facts-only mutual fund assistant.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Reasoning Engine
engine = ReasoningEngine()

# Request/Response Models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    source: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "ready"}

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Primary endpoint for the FAQ assistant.
    Takes a natural language query and returns a factual answer + source.
    """
    logger.info(f"Received query: {request.query}")
    try:
        result = engine.generate_answer(request.query)
        return QueryResponse(
            answer=result["answer"],
            source=result["source"]
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
