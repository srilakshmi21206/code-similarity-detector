from fastapi import FastAPI
from pydantic import BaseModel
from app.similarity.comparator import compute_similarity
from app.routes.upload import router as upload_router

app = FastAPI(title="Code Similarity Detector")

app.include_router(upload_router)


class CompareRequest(BaseModel):
    code1: str
    code2: str


@app.get("/")
def read_root():
    return {"message": "Code Similarity Detector API is running"}


@app.post("/compare")
def compare_code(request: CompareRequest):
    """
    Compares two pieces of Python code and returns similarity scores.
    """
    result = compute_similarity(request.code1, request.code2)
    return result