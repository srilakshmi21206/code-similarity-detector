# 🔍 Code Similarity Detector

A code plagiarism detection tool that uses **Abstract Syntax Tree (AST) analysis** to detect structurally similar code — even when variable names, function names, or formatting have been changed.

Built with **FastAPI** (backend) and **React** (frontend).

---

## 🌐 Live Demo
- **Frontend:** https://code-similarity-detector-six.vercel.app
- **API:** https://code-similarity-detector.onrender.com
- **API Docs:** https://code-similarity-detector.onrender.com/docs

---

## 🚀 Features

- **AST-based comparison** — detects plagiarism even after variable renaming
- **Multi-language support** — compare Python, Java, and C++ files using tree-sitter
- **Two similarity metrics** — string-based and token-based scores, averaged into a combined score
- **Single file comparison** — upload two files and get instant similarity scores
- **Batch comparison** — upload a ZIP of multiple `.py` files, get a full pairwise similarity matrix
- **Configurable threshold** — flag pairs above a custom similarity percentage (default: 80%)
- **Comparison history** — all comparisons stored in SQLite database, accessible via `/history`
- **Input validation** — file size limits, empty file detection, zip security checks
- **Clean React UI** — color-coded results table with flagged/OK status per pair

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| AST Parsing | Python `ast` module (Python), tree-sitter (Java, C++) |
| Similarity | `difflib.SequenceMatcher` |
| Database | SQLite + SQLAlchemy |
| Frontend | React |
| API Docs | Swagger UI (auto-generated) |
| Deployment | Render (backend) + Vercel (frontend) |

---

## 📁 Project Structure

```
code-similarity-detector/
├── app/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── database.py          # SQLite database models + session
│   ├── parser/
│   │   ├── ast_parser.py    # AST parsing + variable normalization (Python)
│   │   └── multi_lang_parser.py  # tree-sitter parser (Java, C++)
│   ├── similarity/
│   │   └── comparator.py    # Similarity scoring engine
│   └── routes/
│       └── upload.py        # All file upload endpoints
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
6. **Store** — results saved to SQLite database for history tracking

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/history` | Get past comparison results from database |
| POST | `/compare` | Compare two code snippets (raw text) |
| POST | `/upload-compare` | Compare two `.py` files |
| POST | `/batch-compare` | Compare all files in a `.zip` |
| POST | `/multilang-compare` | Compare Java or C++ files |

Full interactive docs at `https://code-similarity-detector.onrender.com/docs`

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

**Python batch comparison of 4 student submissions:**

| File 1 | File 2 | Combined Score | Status |
|--------|--------|---------------|--------|
| student1.py | student2.py | 100% | 🚨 Flagged |
| student1.py | student3.py | 84.17% | 🚨 Flagged |
| student2.py | student3.py | 84.17% | 🚨 Flagged |
| student4.py | student1.py | 65.45% | ✅ OK |

**Java file comparison:**

| File 1 | File 2 | Combined Score | Status |
|--------|--------|---------------|--------|
| Test1.java | Test2.java | 94.07% | 🚨 Flagged |

---

## ⚠️ Known Limitations

- **Structural similarity only** — detects copied structure but cannot detect paraphrased logic (e.g. rewriting a loop as recursion)
- **Free tier sleep** — backend on Render free tier spins down after 15 minutes of inactivity; first request may take 30-50 seconds to wake up
- **File size limits** — maximum 1MB per file, 5MB per ZIP, 20 files per batch
- **No persistent storage on server** — SQLite database resets on Render redeploy (use PostgreSQL for production)
- **No scope-awareness** — variable placeholders assigned in order of first encounter across the file, not per function scope

---

## 🔮 Future Improvements

- **AI-powered explanations** — integrate an LLM (Claude/Groq) to explain *why* two files are similar in natural language, suggest how to rewrite flagged code, and summarize key differences
- **GitHub scanning mode** — check student submissions against public GitHub repositories to detect copied code from the internet
- **Active learning loop** — user corrections improve future scoring accuracy
- **PostgreSQL** — replace SQLite with PostgreSQL for persistent production storage that survives redeployment
- **JavaScript/TypeScript support** — extend tree-sitter integration to support frontend code comparison
- **Rate limiting + authentication** — add API keys and request limits for production use

---

## 👤 Author

**SRILAKSHMI.K**
- GitHub: [@srilakshmi21206](https://github.com/srilakshmi21206)
- LinkedIn: [lakshmisri02](https://linkedin.com/in/lakshmisri02)
