import React from "react";

export default function HighlightedText({ sections }) {
  if (!sections || sections.length === 0) {
    return (
      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
        No sections were flagged for AI-like patterns.
      </p>
    );
  }

  return (
    <div>
      <p
        style={{
          fontSize: "0.82rem",
          color: "var(--text-secondary)",
          marginBottom: 12,
        }}
      >
        The following paragraphs showed patterns commonly associated with AI-generated text.
        This does not mean these sections <em>are</em> AI-generated &mdash; only that their
        linguistic features match AI-writing profiles.
      </p>
      {sections.map((item, i) => (
        <div key={i} className="highlight-item">
          <div className="highlight-reason">
            {item.reasons.join(" \u00b7 ")}
          </div>
          <div className="highlight-snippet">
            &ldquo;{item.snippet.length > 280
              ? item.snippet.slice(0, 280) + "\u2026"
              : item.snippet}
            &rdquo;
          </div>
          <div
            style={{
              marginTop: 6,
              fontSize: "0.78rem",
              color: "var(--text-muted)",
            }}
          >
            Paragraph {item.paragraph_index + 1}
          </div>
        </div>
      ))}
    </div>
  );
}
