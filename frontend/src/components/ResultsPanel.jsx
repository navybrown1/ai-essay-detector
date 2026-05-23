import React from "react";
import ScoreGauge from "./ScoreGauge";
import CategoryBreakdown from "./CategoryBreakdown";
import HighlightedText from "./HighlightedText";
import { downloadReport, aiAnalyze, aiImprove, aiGenerateReport } from "../utils/api";

export default function ResultsPanel({
  result, onNewAnalysis,
  aiApiKey, aiAnalysis, setAiAnalysis,
  aiImprovements, setAiImprovements,
  aiReport, setAiReport,
  aiLoading, setAiLoading,
}) {
  if (!result) return null;

  const {
    id,
    ai_score,
    human_score,
    mixed_score,
    confidence,
    category_breakdown,
    highlighted_sections,
    sentence_analysis,
    paragraph_analysis,
    summary,
    disclaimer,
  } = result;

  const runAiAnalysis = async () => {
    setAiLoading(true);
    const essayText = result.summary + "\n\n" + (result.highlighted_sections?.map(h => h.snippet).join("\n") || "Analysis complete based on heuristic scores.");
    try {
      const [opinion, improvements] = await Promise.all([
        aiAnalyze(essayText, aiApiKey),
        aiImprove(essayText, result.highlighted_sections || [], aiApiKey),
      ]);
      setAiAnalysis(opinion);
      setAiImprovements(improvements);
    } catch (e) {
      setAiAnalysis({ error: e.message });
    } finally {
      setAiLoading(false);
    }
  };

  const runAiReport = async () => {
    setAiLoading(true);
    try {
      const res = await aiGenerateReport(id, {
        text: result.summary,
        ai_score,
        human_score,
        mixed_score,
        confidence,
        category_breakdown,
        highlighted_sections: highlighted_sections || [],
        summary,
      }, aiApiKey);
      setAiReport(res.report);
    } catch (e) {
      setAiReport("Error generating AI report: " + e.message);
    } finally {
      setAiLoading(false);
    }
  };

  const hasAiAnalysis = aiAnalysis && !aiAnalysis.error;
  const hasAiSuggestions = aiImprovements && aiImprovements.suggestions?.length > 0;

  return (
    <div>
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10, marginBottom: 16 }}>
          <h3 className="card-title" style={{ margin: 0 }}>Analysis Results</h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <span className={`confidence-badge confidence-${confidence}`}>
              {confidence} Confidence
            </span>
            <button className="btn btn-secondary btn-sm" onClick={() => downloadReport(id)}>
              Export PDF
            </button>
            <button className="btn btn-primary btn-sm" onClick={onNewAnalysis}>
              New Analysis
            </button>
          </div>
        </div>

        <div className="score-gauges">
          <ScoreGauge label="AI-Likelihood" value={ai_score} type="ai" />
          <ScoreGauge label="Human-Likelihood" value={human_score} type="human" />
          <ScoreGauge label="Mixed Writing" value={mixed_score} type="mixed" />
        </div>

        <div className="summary-box">{summary}</div>

        <div className="disclaimer-box">
          <strong>Disclaimer:</strong> {disclaimer}
        </div>

        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>
          Word count: {result.word_count || "N/A"}
        </p>

        {aiApiKey && !hasAiAnalysis && !aiLoading && (
          <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
            <button className="btn btn-accent btn-sm" onClick={runAiAnalysis}>
              Run DeepSeek Analysis
            </button>
          </div>
        )}

        {aiApiKey && hasAiAnalysis && !aiReport && !aiLoading && (
          <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
            <button className="btn btn-accent btn-sm" onClick={runAiReport}>
              Generate AI-Powered Report
            </button>
          </div>
        )}

        {aiLoading && (
          <div className="loading-spinner" style={{ marginTop: 12 }}>
            <div className="spinner" />
            <span>Consulting DeepSeek V4 Flash...</span>
          </div>
        )}
      </div>

      {aiAnalysis && aiAnalysis.error && (
        <div className="card" style={{ borderLeft: "4px solid var(--warning)" }}>
          <h3 className="card-title">DeepSeek Analysis</h3>
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            {aiAnalysis.error}
          </p>
        </div>
      )}

      {hasAiAnalysis && (
        <div className="card">
          <h3 className="card-title">DeepSeek V4 Flash — Second Opinion</h3>

          <div className="ai-opinion-gauges" style={{ display: "flex", gap: 16, marginBottom: 16 }}>
            <div className="ai-gauge">
              <span className="ai-gauge-label">AI Likelihood</span>
              <span className="ai-gauge-value" style={{
                color: aiAnalysis.ai_likelihood > 0.6 ? "var(--ai-color)" : "var(--human-color)",
              }}>
                {aiAnalysis.ai_likelihood != null ? `${(aiAnalysis.ai_likelihood * 100).toFixed(0)}%` : "N/A"}
              </span>
            </div>
            <div className="ai-gauge">
              <span className="ai-gauge-label">Confidence</span>
              <span className={`confidence-badge confidence-${aiAnalysis.confidence || "Low"}`}>
                {aiAnalysis.confidence || "N/A"}
              </span>
            </div>
          </div>

          <div className="verdict-box" style={{
            background: "var(--bg)",
            padding: 12,
            borderRadius: "var(--radius-sm)",
            marginBottom: 12,
            fontStyle: "italic",
            fontSize: "0.9rem",
            borderLeft: "4px solid var(--accent)",
          }}>
            {aiAnalysis.verdict}
          </div>

          <div className="ai-reasoning" style={{ fontSize: "0.85rem", lineHeight: 1.6, color: "var(--text)", marginBottom: 12 }}>
            {aiAnalysis.reasoning}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: "0.85rem" }}>
            {aiAnalysis.strengths?.length > 0 && (
              <div>
                <strong style={{ color: "var(--human-color)" }}>Human-like features</strong>
                <ul style={{ margin: "4px 0 0", paddingLeft: 16, lineHeight: 1.7 }}>
                  {aiAnalysis.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
            {aiAnalysis.weaknesses?.length > 0 && (
              <div>
                <strong style={{ color: "var(--ai-color)" }}>AI-like features</strong>
                <ul style={{ margin: "4px 0 0", paddingLeft: 16, lineHeight: 1.7 }}>
                  {aiAnalysis.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {hasAiSuggestions && (
        <div className="card">
          <h3 className="card-title">Writing Improvement Suggestions</h3>
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: 12 }}>
            DeepSeek V4 Flash suggests these rewrites to make flagged sections sound more natural:
          </p>

          {aiImprovements.suggestions.map((s, i) => (
            <div key={i} className="improvement-item" style={{
              marginBottom: 16,
              padding: 12,
              background: "var(--bg)",
              borderRadius: "var(--radius-sm)",
              borderLeft: "4px solid var(--accent)",
            }}>
              <div style={{ fontSize: "0.82rem", marginBottom: 6 }}>
                <strong>Issue:</strong> {s.issue}
              </div>
              <div className="original-text" style={{
                fontSize: "0.82rem",
                marginBottom: 8,
                padding: 8,
                background: "rgba(230, 57, 70, 0.06)",
                borderRadius: "var(--radius-sm)",
                borderLeft: "3px solid var(--ai-color)",
              }}>
                <span style={{ fontWeight: 600, fontSize: "0.75rem", textTransform: "uppercase", color: "var(--ai-color)" }}>Original:</span><br />
                <em>{s.original_snippet}</em>
              </div>
              <div className="rewritten-text" style={{
                fontSize: "0.82rem",
                marginBottom: 8,
                padding: 8,
                background: "rgba(46, 196, 182, 0.06)",
                borderRadius: "var(--radius-sm)",
                borderLeft: "3px solid var(--human-color)",
              }}>
                <span style={{ fontWeight: 600, fontSize: "0.75rem", textTransform: "uppercase", color: "var(--human-color)" }}>Suggested:</span><br />
                {s.rewritten}
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                {s.explanation}
              </div>
            </div>
          ))}

          {aiImprovements.general_tips?.length > 0 && (
            <div style={{ marginTop: 16, padding: 12, background: "var(--bg)", borderRadius: "var(--radius-sm)" }}>
              <strong style={{ fontSize: "0.85rem" }}>General tips:</strong>
              <ul style={{ fontSize: "0.82rem", margin: "4px 0 0", paddingLeft: 16, lineHeight: 1.7 }}>
                {aiImprovements.general_tips.map((tip, i) => <li key={i}>{tip}</li>)}
              </ul>
              {aiImprovements.overall_style_shift && (
                <p style={{ fontSize: "0.82rem", marginTop: 8, fontStyle: "italic", color: "var(--text-secondary)" }}>
                  {aiImprovements.overall_style_shift}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {aiReport && (
        <div className="card">
          <h3 className="card-title">AI-Powered Report</h3>
          <div style={{ fontSize: "0.85rem", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
            {aiReport}
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="card-title">Category Breakdown</h3>
        <CategoryBreakdown categories={category_breakdown} />
      </div>

      {highlighted_sections && highlighted_sections.length > 0 && (
        <div className="card">
          <h3 className="card-title">
            Highlighted Sections ({highlighted_sections.length} found)
          </h3>
          <HighlightedText sections={highlighted_sections} />
        </div>
      )}

      {sentence_analysis && sentence_analysis.length > 0 && (
        <div className="card">
          <h3 className="card-title">Sentence-Level Analysis</h3>
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: 12 }}>
            Each sentence scored for AI-like patterns (higher = more AI-like).
            This is a rough heuristic, not a precise measure.
          </p>
          <div className="sentence-list">
            {sentence_analysis.map((s, i) => (
              <div
                key={i}
                className="sentence-item"
                style={{
                  background:
                    s.ai_score > 0.6
                      ? "rgba(230, 57, 70, 0.08)"
                      : s.ai_score < 0.3
                      ? "rgba(46, 196, 182, 0.08)"
                      : "transparent",
                }}
              >
                <span className="s-index">{s.index}</span>
                <span className="s-text">{s.text}</span>
                <span
                  className="s-score"
                  style={{
                    color:
                      s.ai_score > 0.6
                        ? "var(--ai-color)"
                        : s.ai_score < 0.3
                        ? "var(--human-color)"
                        : "var(--text-secondary)",
                  }}
                >
                  {s.ai_score.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {paragraph_analysis && paragraph_analysis.length > 0 && (
        <div className="card">
          <h3 className="card-title">Paragraph-Level Analysis</h3>
          <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.7 }}>
            {paragraph_analysis.map((p, i) => (
              <div key={i} style={{ marginBottom: 8, padding: 8, background: "var(--bg)", borderRadius: "var(--radius-sm)" }}>
                <strong>Paragraph {p.index + 1}:</strong> {p.word_count} words,
                {p.sentence_count} sentences &mdash; depth: <em>{p.depth}</em>,
                syntax: <em>{p.syntax}</em>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
