import zipfile
import io
from itertools import combinations
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.similarity.comparator import compute_similarity

router = APIRouter()


@router.post("/upload-compare")
async def upload_compare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    if not file1.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail=f"{file1.filename} is not a Python file")
    if not file2.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail=f"{file2.filename} is not a Python file")

    content1 = await file1.read()
    content2 = await file2.read()

    try:
        source1 = content1.decode("utf-8")
        source2 = content2.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file")

    if not source1.strip() or not source2.strip():
        raise HTTPException(status_code=400, detail="One or both files are empty")

    result = compute_similarity(source1, source2)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {"file1": file1.filename, "file2": file2.filename, **result}


@router.post("/batch-compare")
async def batch_compare(zip_file: UploadFile = File(...), threshold: float = 80.0):
    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")

    content = await zip_file.read()

    try:
        zip_bytes = io.BytesIO(content)
        with zipfile.ZipFile(zip_bytes) as z:
            py_files = [name for name in z.namelist() if name.endswith(".py") and not name.startswith("__MACOSX")]

            if len(py_files) < 2:
                raise HTTPException(status_code=400, detail="Zip must contain at least 2 Python files")

            sources = {}
            for name in py_files:
                with z.open(name) as f:
                    try:
                        sources[name] = f.read().decode("utf-8")
                    except UnicodeDecodeError:
                        continue

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file")

    results = []
    filenames = list(sources.keys())

    for name1, name2 in combinations(filenames, 2):
        comparison = compute_similarity(sources[name1], sources[name2])
        if "error" in comparison:
            continue
        results.append({
            "file1": name1,
            "file2": name2,
            **comparison,
            "flagged": comparison["combined_score"] >= threshold
        })

    results.sort(key=lambda x: x["combined_score"], reverse=True)
    flagged_pairs = [r for r in results if r["flagged"]]

    return {
        "total_files": len(filenames),
        "total_comparisons": len(results),
        "threshold_used": threshold,
        "flagged_count": len(flagged_pairs),
        "flagged_pairs": flagged_pairs,
        "all_results": results
    }