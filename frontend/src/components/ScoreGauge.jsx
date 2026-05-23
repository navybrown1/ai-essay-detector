import React from "react";

export default function ScoreGauge({ label, value, type }) {
  const pct = Math.round(value * 100);

  const getColor = () => {
    if (pct > 60) return type === "ai" ? "var(--ai-color)" : type === "human" ? "var(--human-color)" : "var(--mixed-color)";
    if (pct > 35) return "var(--warning)";
    return "var(--text-muted)";
  };

  return (
    <div className={`gauge ${type}`}>
      <div className="gauge-value">{pct}%</div>
      <div
        style={{
          height: 6,
          background: "var(--border)",
          borderRadius: 3,
          margin: "8px 0",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: getColor(),
            borderRadius: 3,
            transition: "width 0.8s ease",
          }}
        />
      </div>
      <div className="gauge-label">{label}</div>
    </div>
  );
}
