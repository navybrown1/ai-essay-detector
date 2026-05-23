import React, { useState, useEffect } from "react";

const API_BASE = "/api";

export default function ColdStartGuard({ children }) {
  const [status, setStatus] = useState("checking"); // checking | ready | error
  const [dots, setDots] = useState("");

  useEffect(() => {
    const dotInterval = setInterval(() => {
      setDots((d) => (d.length >= 3 ? "" : d + "."));
    }, 500);
    return () => clearInterval(dotInterval);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`, { method: "GET" });
        if (!cancelled) {
          if (res.ok) {
            setStatus("ready");
          } else {
            setStatus("error");
          }
        }
      } catch {
        if (!cancelled) setStatus("error");
      }
    };
    checkHealth();
    return () => { cancelled = true; };
  }, []);

  if (status === "ready") return children;

  return (
    <div className="app-container" style={{ textAlign: "center", paddingTop: 80 }}>
      <div className="spinner" style={{ margin: "0 auto 24px", width: 48, height: 48, borderWidth: 4 }} />
      <h2 style={{ fontSize: "1.2rem", marginBottom: 12, color: "var(--text)" }}>
        {status === "checking" ? `Warming up server${dots}` : "Server unreachable"}
      </h2>
      <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", maxWidth: 400, margin: "0 auto", lineHeight: 1.6 }}>
        {status === "checking"
          ? "The backend is starting (cold start). This usually takes 5–10 seconds on the first load."
          : "Could not reach the backend. Please refresh the page or try again later."}
      </p>
      {status === "error" && (
        <button
          className="btn btn-primary"
          style={{ marginTop: 24 }}
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      )}
    </div>
  );
}
