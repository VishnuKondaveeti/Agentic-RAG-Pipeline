import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from backend.core.ingestion import ingest_documents, DOCS_DIR
from backend.core.agent import AgenticRAG
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Global Agent
agent = None

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global agent
    print("Initializing AgenticRAG... This may take a moment.")
    try:
        agent = AgenticRAG()
        print("AgenticRAG initialized successfully.")
    except Exception as e:
        print(f"Error initializing AgenticRAG: {e}")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"status": "Agentic RAG Backend is running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document to the data directory and trigger ingestion."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(DOCS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Trigger ingestion (this is synchronous for simplicity, consider background tasks for large files)
    ingest_documents()
    
    return {"filename": file.filename, "status": "Uploaded and Ingested successfully"}

@app.post("/query")
async def query_agent(request: QueryRequest):
    """Query the agentic RAG pipeline."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized. Check API keys.")
    
    try:
        response = agent.run(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
