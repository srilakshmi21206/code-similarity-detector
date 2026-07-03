import zipfile
import io
from itertools import combinations
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.similarity.comparator import compute_similarity
from app.database import get_db, Comparison

router = APIRouter()

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB per file
MAX_ZIP_SIZE = 5 * 1024 * 1024   # 5MB for zip


@router.post("/upload-compare")
async def upload_compare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    if not file1.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail=f"{file1.filename} is not a Python file")
    if not file2.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail=f"{file2.filename} is not a Python file")

    content1 = await file1.read()
    content2 = await file2.read()

    if len(content1) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"{file1.filename} exceeds 1MB limit")
    if len(content2) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"{file2.filename} exceeds 1MB limit")

    if len(content1) == 0:
        raise HTTPException(status_code=400, detail=f"{file1.filename} is empty")
    if len(content2) == 0:
        raise HTTPException(status_code=400, detail=f"{file2.filename} is empty")

    try:
        source1 = content1.decode("utf-8")
        source2 = content2.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file — ensure it is a valid UTF-8 text file")

    if not source1.strip() or not source2.strip():
        raise HTTPException(status_code=400, detail="One or both files contain only whitespace")

    result = compute_similarity(source1, source2)

    if "error" in result:
        raise HTTPException(status_code=400, detail=f"Syntax error in code: {result['error']}")

    # Save to database
    db = next(get_db())
    comparison = Comparison(
        file1=file1.filename,
        file2=file2.filename,
        string_similarity=result["string_similarity"],
        token_similarity=result["token_similarity"],
        combined_score=result["combined_score"],
        flagged=str(result["combined_score"] >= 80).lower()
    )
    db.add(comparison)
    db.commit()
    db.close()

    return {
        "file1": file1.filename,
        "file2": file2.filename,
        **result
    }


@router.post("/batch-compare")
async def batch_compare(zip_file: UploadFile = File(...), threshold: float = 80.0):
    if not 0 <= threshold <= 100:
        raise HTTPException(status_code=400, detail="Threshold must be between 0 and 100")

    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")

    content = await zip_file.read()

    if len(content) > MAX_ZIP_SIZE:
        raise HTTPException(status_code=400, detail="ZIP file exceeds 5MB limit")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="ZIP file is empty")

    try:
        zip_bytes = io.BytesIO(content)
        with zipfile.ZipFile(zip_bytes) as z:
            for name in z.namelist():
                if name.startswith("/") or ".." in name:
                    raise HTTPException(status_code=400, detail="Invalid file path in ZIP")

            py_files = [
                name for name in z.namelist()
                if name.endswith(".py") and not name.startswith("__MACOSX")
            ]

            if len(py_files) == 0:
                raise HTTPException(status_code=400, detail="No Python files found in ZIP")
            if len(py_files) < 2:
                raise HTTPException(status_code=400, detail="ZIP must contain at least 2 Python files")
            if len(py_files) > 20:
                raise HTTPException(status_code=400, detail="ZIP contains too many files — maximum 20 Python files allowed")

            sources = {}
            skipped = []
            for name in py_files:
                with z.open(name) as f:
                    file_content = f.read()
                    if len(file_content) > MAX_FILE_SIZE:
                        skipped.append(f"{name} (exceeds 1MB)")
                        continue
                    try:
                        decoded = file_content.decode("utf-8")
                        if decoded.strip():
                            sources[name] = decoded
                        else:
                            skipped.append(f"{name} (empty)")
                    except UnicodeDecodeError:
                        skipped.append(f"{name} (unreadable encoding)")

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted ZIP file")

    if len(sources) < 2:
        raise HTTPException(status_code=400, detail="Not enough valid Python files to compare")

    results = []
    filenames = list(sources.keys())
    syntax_errors = []

    for name1, name2 in combinations(filenames, 2):
        comparison = compute_similarity(sources[name1], sources[name2])
        if "error" in comparison:
            syntax_errors.append(f"{name1} or {name2}: {comparison['error']}")
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
        "all_results": results,
        "skipped_files": skipped,
        "syntax_errors": syntax_errors
    }
@router.post("/multilang-compare")
async def multilang_compare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Compare two code files of any supported language (Python, Java, C++).
    Both files must be the same language.
    """
    from app.parser.multi_lang_parser import get_language, compute_multilang_similarity

    lang1 = get_language(file1.filename)
    lang2 = get_language(file2.filename)

    if not lang1:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file1.filename}. Supported: .py, .java, .cpp")
    if not lang2:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file2.filename}. Supported: .py, .java, .cpp")
    if lang1 != lang2:
        raise HTTPException(status_code=400, detail=f"Files must be the same language — got {lang1} and {lang2}")

    content1 = await file1.read()
    content2 = await file2.read()

    if len(content1) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"{file1.filename} exceeds 1MB limit")
    if len(content2) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"{file2.filename} exceeds 1MB limit")

    try:
        source1 = content1.decode("utf-8")
        source2 = content2.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file")

    result = compute_multilang_similarity(source1, source2, lang1)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "file1": file1.filename,
        "file2": file2.filename,
        **result
    }