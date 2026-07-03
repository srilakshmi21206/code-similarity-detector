import { useState } from "react";

const API = "https://code-similarity-detector.onrender.com";

function App() {
  const [tab, setTab] = useState("compare");

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 800, margin: "40px auto", padding: "0 20px" }}>
      <h1 style={{ color: "#2563eb" }}>🔍 Code Similarity Detector</h1>
      <p style={{ color: "#666" }}>Detect plagiarism in Python code using AST-based structural analysis</p>

      <div style={{ display: "flex", gap: 10, marginBottom: 30 }}>
        <button
          onClick={() => setTab("compare")}
          style={{
            padding: "10px 20px", cursor: "pointer", borderRadius: 6, border: "none",
            background: tab === "compare" ? "#2563eb" : "#e5e7eb", color: tab === "compare" ? "white" : "black"
          }}>
          Compare Two Files
        </button>
        <button
          onClick={() => setTab("batch")}
          style={{
            padding: "10px 20px", cursor: "pointer", borderRadius: 6, border: "none",
            background: tab === "batch" ? "#2563eb" : "#e5e7eb", color: tab === "batch" ? "white" : "black"
          }}>
          Batch Compare (ZIP)
        </button>
      </div>

      {tab === "compare" ? <CompareTab /> : <BatchTab />}
    </div>
  );
}

function CompareTab() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (!file1 || !file2) return alert("Please select both files");
    setLoading(true); setError(null); setResult(null);

    const formData = new FormData();
    formData.append("file1", file1);
    formData.append("file2", file2);

    try {
      const res = await fetch(`${API}/upload-compare`, { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => score >= 80 ? "#dc2626" : score >= 50 ? "#f59e0b" : "#16a34a";

  return (
    <div>
      <h2>Compare Two Python Files</h2>
      <div style={{ display: "flex", gap: 20, marginBottom: 20, flexWrap: "wrap" }}>
        <div>
          <label style={{ display: "block", marginBottom: 6, fontWeight: "bold" }}>File 1</label>
          <input type="file" accept=".py" onChange={e => setFile1(e.target.files[0])} />
        </div>
        <div>
          <label style={{ display: "block", marginBottom: 6, fontWeight: "bold" }}>File 2</label>
          <input type="file" accept=".py" onChange={e => setFile2(e.target.files[0])} />
        </div>
      </div>

      <button
        onClick={handleCompare}
        disabled={loading}
        style={{ padding: "10px 24px", background: "#2563eb", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 16 }}>
        {loading ? "Analyzing..." : "Compare"}
      </button>

      {error && <p style={{ color: "red", marginTop: 16 }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: 30, padding: 24, background: "#f9fafb", borderRadius: 8, border: "1px solid #e5e7eb" }}>
          <h3>Results: {result.file1} vs {result.file2}</h3>
          <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
            {[
              { label: "String Similarity", value: result.string_similarity },
              { label: "Token Similarity", value: result.token_similarity },
              { label: "Combined Score", value: result.combined_score },
            ].map(({ label, value }) => (
              <div key={label} style={{ textAlign: "center", padding: 20, background: "white", borderRadius: 8, border: "1px solid #e5e7eb", minWidth: 150 }}>
                <div style={{ fontSize: 36, fontWeight: "bold", color: scoreColor(value) }}>{value}%</div>
                <div style={{ color: "#666", marginTop: 4 }}>{label}</div>
              </div>
            ))}
          </div>
          {result.combined_score >= 80 && (
            <div style={{ marginTop: 16, padding: 12, background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 6, color: "#dc2626" }}>
              ⚠️ High similarity detected — possible plagiarism
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function BatchTab() {
  const [zipFile, setZipFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleBatch = async () => {
    if (!zipFile) return alert("Please select a zip file");
    setLoading(true); setError(null); setResult(null);

    const formData = new FormData();
    formData.append("zip_file", zipFile);

    try {
      const res = await fetch(`${API}/batch-compare`, { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => score >= 80 ? "#dc2626" : score >= 50 ? "#f59e0b" : "#16a34a";

  return (
    <div>
      <h2>Batch Compare Python Files</h2>
      <p style={{ color: "#666" }}>Upload a ZIP containing multiple .py files — every pair will be compared</p>

      <div style={{ marginBottom: 20 }}>
        <label style={{ display: "block", marginBottom: 6, fontWeight: "bold" }}>ZIP File</label>
        <input type="file" accept=".zip" onChange={e => setZipFile(e.target.files[0])} />
      </div>

      <button
        onClick={handleBatch}
        disabled={loading}
        style={{ padding: "10px 24px", background: "#2563eb", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 16 }}>
        {loading ? "Analyzing..." : "Run Batch Analysis"}
      </button>

      {error && <p style={{ color: "red", marginTop: 16 }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: 30 }}>
          <div style={{ display: "flex", gap: 16, marginBottom: 24, flexWrap: "wrap" }}>
            {[
              { label: "Total Files", value: result.total_files },
              { label: "Comparisons", value: result.total_comparisons },
              { label: "Flagged Pairs", value: result.flagged_count },
            ].map(({ label, value }) => (
              <div key={label} style={{ textAlign: "center", padding: 16, background: "#f9fafb", borderRadius: 8, border: "1px solid #e5e7eb", minWidth: 120 }}>
                <div style={{ fontSize: 28, fontWeight: "bold", color: "#2563eb" }}>{value}</div>
                <div style={{ color: "#666", marginTop: 4 }}>{label}</div>
              </div>
            ))}
          </div>

          <h3>All Comparisons</h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f3f4f6" }}>
                {["File 1", "File 2", "String %", "Token %", "Combined %", "Status"].map(h => (
                  <th key={h} style={{ padding: "10px 12px", textAlign: "left", border: "1px solid #e5e7eb" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.all_results.map((r, i) => (
                <tr key={i} style={{ background: r.flagged ? "#fef2f2" : "white" }}>
                  <td style={{ padding: "10px 12px", border: "1px solid #e5e7eb" }}>{r.file1}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e5e7eb" }}>{r.file2}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e5e7eb", color: scoreColor(r.string_similarity) }}>{r.string_similarity}%</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e5e7eb", color: scoreColor(r.token_similarity) }}>{r.token_similarity}%</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e5e7eb", fontWeight: "bold", color: scoreColor(r.combined_score) }}>{r.combined_score}%</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e5e7eb" }}>
                    {r.flagged ? "🚨 Flagged" : "✅ OK"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;