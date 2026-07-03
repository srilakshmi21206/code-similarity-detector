from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.similarity.comparator import compute_similarity
from app.routes.upload import router as upload_router
from app.database import create_tables, get_db, Comparison

app = FastAPI(title="Code Similarity Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://code-similarity-detector-six.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)

# Create tables on startup
@app.on_event("startup")
def startup():
    create_tables()


class CompareRequest(BaseModel):
    code1: str
    code2: str


@app.get("/")
def read_root():
    return {"message": "Code Similarity Detector API is running"}


@app.post("/compare")
def compare_code(request: CompareRequest, db: Session = Depends(get_db)):
    result = compute_similarity(request.code1, request.code2)

    if "error" not in result:
        # Save to database
        comparison = Comparison(
            file1="snippet_1",
            file2="snippet_2",
            string_similarity=result["string_similarity"],
            token_similarity=result["token_similarity"],
            combined_score=result["combined_score"],
            flagged=str(result["combined_score"] >= 80).lower()
        )
        db.add(comparison)
        db.commit()

    return result


@app.get("/history")
def get_history(db: Session = Depends(get_db), limit: int = 20):
    """Returns the last N comparisons stored in the database."""
    comparisons = db.query(Comparison).order_by(
        Comparison.created_at.desc()
    ).limit(limit).all()

    return {
        "total": len(comparisons),
        "comparisons": [
            {
                "id": c.id,
                "file1": c.file1,
                "file2": c.file2,
                "string_similarity": c.string_similarity,
                "token_similarity": c.token_similarity,
                "combined_score": c.combined_score,
                "flagged": c.flagged,
                "created_at": c.created_at.isoformat()
            }
            for c in comparisons
        ]
    }