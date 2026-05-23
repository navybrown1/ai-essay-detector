import React, { useState, useEffect, useCallback } from "react";
import Dashboard from "./components/Dashboard";
import InputPanel from "./components/InputPanel";
import ResultsPanel from "./components/ResultsPanel";
import HistoryPanel from "./components/HistoryPanel";
import ColdStartGuard from "./components/ColdStartGuard";
import { analyzeText, analyzeFile, getHistory, getScan } from "./utils/api";

function safeGet(key, fallback = "") {
  try {
    return localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

function safeSet(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* ignore quota/restriction errors */
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState("analyze");
  const [theme, setTheme] = useState(() => safeGet("theme", "light"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [currentScanId, setCurrentScanId] = useState(null);

  const [showAiSettings, setShowAiSettings] = useState(() => {
    return safeGet("showAiSettings") === "true";
  });
  const [aiApiKey, setAiApiKey] = useState(() => safeGet("openrouterApiKey", ""));
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiImprovements, setAiImprovements] = useState(null);
  const [aiReport, setAiReport] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    safeSet("showAiSettings", showAiSettings);
  }, [showAiSettings]);

  useEffect(() => {
    safeSet("openrouterApiKey", aiApiKey);
  }, [aiApiKey]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    safeSet("theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "light" ? "dark" : "light"));

  const refreshHistory = useCallback(async () => {
    try {
      const h = await getHistory();
      setHistory(h);
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    if (activeTab === "history") refreshHistory();
  }, [activeTab, refreshHistory]);

  const handleAnalyze = async (text, title, filename, authorId) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setAiAnalysis(null);
    setAiImprovements(null);
    setAiReport(null);
    try {
      const res = await analyzeText(text, title, filename, authorId);
      setResult(res);
      setCurrentScanId(res.id);
      setActiveTab("results");
      refreshHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file, title, authorId) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setAiAnalysis(null);
    setAiImprovements(null);
    setAiReport(null);
    try {
      const res = await analyzeFile(file, title, authorId);
      setResult(res);
      setCurrentScanId(res.id);
      setActiveTab("results");
      refreshHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewScan = async (id) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setAiAnalysis(null);
    setAiImprovements(null);
    setAiReport(null);
    try {
      const res = await getScan(id);
      setResult(res);
      setCurrentScanId(res.id);
      setActiveTab("results");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setResult(null);
    setCurrentScanId(null);
    setError(null);
    setAiAnalysis(null);
    setAiImprovements(null);
    setAiReport(null);
    setActiveTab("analyze");
  };

  return (
    <ColdStartGuard>
    <div className="app-container">
      <header className="app-header">
        <h1>
          <span>AI</span> Essay Detector
        </h1>
        <div className="header-actions">
          {aiApiKey && (
            <span className="ai-badge">DeepSeek Ready</span>
          )}
          <span
            className="theme-toggle"
            onClick={toggleTheme}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === "Enter" && toggleTheme()}
          >
            {theme === "light" ? "Dark" : "Light"}
          </span>
        </div>
      </header>

      <div className="tab-bar">
        {[
          ["analyze", "Analyze"],
          ["results", "Results"],
          ["history", "History"],
        ].map(([key, label]) => (
          <button
            key={key}
            className={`tab-btn ${activeTab === key ? "active" : ""}`}
            onClick={() => {
              if (key === "history") refreshHistory();
              setActiveTab(key);
            }}
            disabled={key === "results" && !result}
          >
            {label}
          </button>
        ))}
      </div>

      {activeTab === "analyze" && (
        <Dashboard
          onAnalyze={handleAnalyze}
          onFileUpload={handleFileUpload}
          loading={loading}
          error={error}
          showAiSettings={showAiSettings}
          setShowAiSettings={setShowAiSettings}
          aiApiKey={aiApiKey}
          setAiApiKey={setAiApiKey}
        />
      )}

      {activeTab === "results" && result && (
        <ResultsPanel
          result={result}
          onNewAnalysis={handleNewAnalysis}
          aiApiKey={aiApiKey}
          aiAnalysis={aiAnalysis}
          setAiAnalysis={setAiAnalysis}
          aiImprovements={aiImprovements}
          setAiImprovements={setAiImprovements}
          aiReport={aiReport}
          setAiReport={setAiReport}
          aiLoading={aiLoading}
          setAiLoading={setAiLoading}
        />
      )}

      {activeTab === "history" && (
        <HistoryPanel
          history={history}
          onViewScan={handleViewScan}
          refreshHistory={refreshHistory}
        />
      )}
    </div>
    </ColdStartGuard>
  );
}
