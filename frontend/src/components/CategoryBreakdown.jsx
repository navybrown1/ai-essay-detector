import React from "react";

const CATEGORY_LABELS = {
  predictability: "Language Predictability",
  sentence_variation: "Sentence Variation",
  paragraph_rhythm: "Paragraph Rhythm",
  repetitive_phrasing: "Repetitive Phrasing",
  generic_filler: "Generic Filler",
  transition_patterns: "Transition Patterns",
  evidence_specificity: "Evidence Specificity",
  personal_voice: "Personal Voice",
  natural_imperfection: "Natural Imperfection",
  citation_behavior: "Citation Behavior",
  readability_profile: "Readability Profile",
  topic_depth: "Topic Depth",
  structural_symmetry: "Structural Symmetry",
  lexical_diversity: "Lexical Diversity",
};

export default function CategoryBreakdown({ categories }) {
  if (!categories || Object.keys(categories).length === 0) {
    return (
      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
        No category data available.
      </p>
    );
  }

  const entries = Object.entries(categories).sort((a, b) => b[1].score - a[1].score);

  return (
    <div className="category-grid">
      {entries.map(([key, val]) => {
        const score = typeof val === "object" ? val.score : val;
        const interpretation =
          typeof val === "object" ? val.interpretation || "" : "";
        const pct = Math.round(score * 100);
        const label = CATEGORY_LABELS[key] || key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

        const barColor =
          pct > 60
            ? "var(--ai-color)"
            : pct > 35
            ? "var(--warning)"
            : "var(--human-color)";

        return (
          <div key={key} className="category-item" title={interpretation}>
            <span className="category-name">{label}</span>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div className="category-bar">
                <div
                  className="category-fill"
                  style={{ width: `${pct}%`, background: barColor }}
                />
              </div>
              <span
                style={{
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  color: barColor,
                  minWidth: 32,
                  textAlign: "right",
                }}
              >
                {pct}%
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
