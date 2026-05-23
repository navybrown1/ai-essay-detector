import React from "react";

export default function InputPanel({
  onAnalyze, onFileUpload, loading,
  showAiSettings, setShowAiSettings,
  aiApiKey, setAiApiKey,
}) {
  const [text, setText] = React.useState("");
  const [title, setTitle] = React.useState("");
  const [authorId, setAuthorId] = React.useState("");
  const [fileName, setFileName] = React.useState(null);
  const [fileContent, setFileContent] = React.useState(null);
  const fileRef = React.useRef();

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFileName(f.name);
      setFileContent(f);
    }
  };

  const handleSubmit = () => {
    if (fileContent) {
      onFileUpload(fileContent, title || fileContent.name, authorId || null);
      return;
    }
    if (text.trim().length < 10) return;
    onAnalyze(text, title || "Untitled", "pasted_text", authorId || null);
  };

  const handleClear = () => {
    setText("");
    setTitle("");
    setAuthorId("");
    setFileName(null);
    setFileContent(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="card input-panel">
      <h3 className="card-title">Input Essay</h3>

      <div className="file-upload-area">
        <label className="file-upload-label">
          {fileName ? "Change File" : "+ Upload File"}
          <input
            type="file"
            accept=".txt,.docx,.pdf"
            onChange={handleFileChange}
            ref={fileRef}
            disabled={loading}
          />
        </label>
        {fileName && <span className="file-name">{fileName}</span>}
        {fileName && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setFileName(null);
              setFileContent(null);
              if (fileRef.current) fileRef.current.value = "";
            }}
          >
            Remove
          </button>
        )}
      </div>

      {!fileName && (
        <textarea
          placeholder="Paste your essay here (or upload a file above)..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={loading}
        />
      )}

      <div className="input-meta">
        <input
          placeholder="Essay title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={loading}
        />
        <input
          placeholder="Author ID (optional, for comparison)"
          value={authorId}
          onChange={(e) => setAuthorId(e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="ai-settings-toggle" onClick={() => setShowAiSettings(!showAiSettings)}>
        <span>{showAiSettings ? "▾" : "▸"}</span>
        <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>
          AI Enhancement (DeepSeek V4 Flash via OpenRouter)
        </span>
      </div>

      {showAiSettings && (
        <div className="ai-settings-panel">
          <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: 4, display: "block" }}>
            OpenRouter API Key (stored locally, never sent to our server)
          </label>
          <input
            type="password"
            placeholder="sk-or-v1-..."
            value={aiApiKey}
            onChange={(e) => setAiApiKey(e.target.value)}
            style={{ fontFamily: "monospace", fontSize: "0.8rem" }}
          />
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 4 }}>
            Get a key at{" "}
            <a href="https://openrouter.ai/keys" target="_blank" rel="noreferrer">
              openrouter.ai/keys
            </a>
            . Enables second-opinion analysis, writing suggestions, and AI-powered reports.
          </p>
        </div>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading || (!text.trim() && !fileContent)}
        >
          {loading ? "Analyzing..." : "Analyze Essay"}
        </button>
        <button className="btn btn-secondary" onClick={handleClear} disabled={loading}>
          Clear
        </button>
      </div>
    </div>
  );
}
