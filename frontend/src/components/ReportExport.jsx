import React from "react";

export default function ReportExport({ scanId, onClose }) {
  const [exporting, setExporting] = React.useState(false);
  const [exported, setExported] = React.useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const { downloadReport } = await import("../utils/api");
      await downloadReport(scanId);
      setExported(true);
    } catch {
      /* silent */
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3 className="card-title">Export Report</h3>
      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: 12 }}>
        Download a PDF report with full analysis, scores, highlighted sections, and disclaimer.
      </p>
      <div style={{ display: "flex", gap: 10 }}>
        <button className="btn btn-primary btn-sm" onClick={handleExport} disabled={exporting}>
          {exporting ? "Generating PDF..." : exported ? "Download Again" : "Export PDF Report"}
        </button>
        {onClose && (
          <button className="btn btn-secondary btn-sm" onClick={onClose}>
            Close
          </button>
        )}
      </div>
    </div>
  );
}
