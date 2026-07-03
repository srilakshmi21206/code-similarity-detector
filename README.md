# 🔍 Code Similarity Detector

A Python plagiarism detection tool that uses **Abstract Syntax Tree (AST) analysis** to detect structurally similar code — even when variable names, function names, or formatting have been changed.

Built with **FastAPI** (backend) and **React** (frontend).

---

## 🚀 Features

- **AST-based comparison** — detects plagiarism even after variable renaming
- **Two similarity metrics** — string-based and token-based scores, averaged into a combined score
- **Single file comparison** — upload two `.py` files and get instant similarity scores
- **Batch comparison** — upload a ZIP of multiple `.py` files, get a full pairwise similarity matrix
- **Configurable threshold** — flag pairs above a custom similarity percentage (default: 80%)
- **Clean React UI** — color-coded results table with flagged/OK status per pair

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| AST Parsing | Python `ast` module |
| Similarity | `difflib.SequenceMatcher` |
| Frontend | React |
| API Docs | Swagger UI (auto-generated) |

---

## 📁 Project Structure

```
code-similarity-detector/
├── app/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── parser/
│   │   └── ast_parser.py    # AST parsing + variable normalization
│   ├── similarity/
│   │   └── comparator.py    # Similarity scoring engine
│   └── routes/
│       └── upload.py        # File upload + batch compare endpoints
├── frontend/                # React UI
├── tests/                   # Unit tests
└── requirements.txt
```

---

## ⚙️ How It Works

1. **Parse** — source code is parsed into an Abstract Syntax Tree
2. **Normalize** — all variable/function names replaced with placeholders (`VAR1`, `VAR2`...)
3. **Compare** — two normalized trees compared using string + token similarity
4. **Score** — both scores averaged into a combined similarity percentage
5. **Flag** — pairs above the threshold marked as likely plagiarism

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/compare` | Compare two code snippets (raw text) |
| POST | `/upload-compare` | Compare two `.py` files |
| POST | `/batch-compare` | Compare all files in a `.zip` |

Full interactive docs at `http://localhost:8000/docs`

---

## 🏃 Running Locally

**Backend:**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` for the UI, `http://localhost:8000/docs` for the API.

---

## 📊 Example Results

| File 1 | File 2 | Combined Score | Status |
|--------|--------|---------------|--------|
| student1.py | student2.py | 100% | 🚨 Flagged |
| student1.py | student3.py | 84.17% | 🚨 Flagged |
| student2.py | student3.py | 84.17% | 🚨 Flagged |
| student4.py | student1.py | 65.45% | ✅ OK |

## 🌐 Live Demo
- **Frontend:** https://code-similarity-detector-six.vercel.app
- **API:** https://code-similarity-detector.onrender.com
- **API Docs:** https://code-similarity-detector.onrender.com/docs

## ⚠️ Known Limitations

This tool uses a simplified normalization strategy, which has a couple of known tradeoffs:

- **No scope-awareness:** Variable names are assigned placeholders (`VAR1`, `VAR2`...) in the order they're first encountered across the *entire file*, not per function scope. Two functions with identical logic but variables introduced in a different order could score slightly lower than a scope-aware comparison would give.
- **Docstrings and string literals affect scoring:** Since one of the two similarity metrics compares the full normalized AST dump (including string literal content), two functions with identical logic but different docstrings or comments will show as slightly less similar than a pure logic-only comparison would show. The token-based metric is less affected by this, since it compares node *types* rather than their contents.

These are intentional simplifications for a lightweight tool rather than a production-grade plagiarism detection system — a more advanced version would use per-scope symbol tables and strip docstring/comment nodes before comparison.

## 🔮 Future Improvements

- Support for multiple languages via `tree-sitter`
- Database layer to store past comparisons
- Active learning loop — user corrections improve accuracy
- GitHub scanning mode — check against public repos
