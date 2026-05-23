import React from "react";
import { deleteScan } from "../utils/api";

export default function HistoryPanel({ history, onViewScan, refreshHistory }) {
  const handleDelete = async (id) => {
    try {
      await deleteScan(id);
      refreshHistory();
    } catch {
      /* silent */
    }
  };

  if (!history || history.length === 0) {
    return (
      <div className="card" style={{ textAlign: "center", padding: 40 }}>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          No scan history yet. Run an analysis to see results here.
        </p>
      </div>
    );
  }

  return (
    <div className="card" style={{ overflowX: "auto" }}>
      <h3 className="card-title">Scan History</h3>
      <table className="history-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>File</th>
            <th>Date</th>
            <th>Words</th>
            <th>AI</th>
            <th>Human</th>
            <th>Mixed</th>
            <th>Confidence</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {history.map((item) => (
            <tr key={item.id}>
              <td style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {item.title || "Untitled"}
              </td>
              <td style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                {item.filename || "pasted_text"}
              </td>
              <td style={{ fontSize: "0.8rem", whiteSpace: "nowrap" }}>
                {new Date(item.created_at).toLocaleDateString()}
              </td>
              <td>{item.word_count}</td>
              <td className="score-cell" style={{ color: "var(--ai-color)" }}>
                {(item.ai_score * 100).toFixed(0)}%
              </td>
              <td className="score-cell" style={{ color: "var(--human-color)" }}>
                {(item.human_score * 100).toFixed(0)}%
              </td>
              <td className="score-cell" style={{ color: "var(--mixed-color)" }}>
                {(item.mixed_score * 100).toFixed(0)}%
              </td>
              <td>
                <span className={`confidence-badge confidence-${item.confidence}`}>
                  {item.confidence}
                </span>
              </td>
              <td>
                <div style={{ display: "flex", gap: 4 }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => onViewScan(item.id)}>
                    View
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(item.id)}>
                    Del
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
