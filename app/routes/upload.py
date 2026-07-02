from fastapi import APIRouter, UploadFile, File, HTTPException
from app.similarity.comparator import compute_similarity

router = APIRouter()


@router.post("/upload-compare")
async def upload_compare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Accepts two .py files, compares them, and returns similarity scores.
    """
    # Validate file extensions
    if not file1.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail=f"{file1.filename} is not a Python file")
    if not file2.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail=f"{file2.filename} is not a Python file")

    # Read file contents
    content1 = await file1.read()
    content2 = await file2.read()

    try:
        source1 = content1.decode("utf-8")
        source2 = content2.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file — ensure it's a valid text file")

    if not source1.strip() or not source2.strip():
        raise HTTPException(status_code=400, detail="One or both files are empty")

    result = compute_similarity(source1, source2)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "file1": file1.filename,
        "file2": file2.filename,
        **result
    }