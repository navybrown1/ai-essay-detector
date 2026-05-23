import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import ErrorBoundary from "./components/ErrorBoundary";
import "./styles/globals.css";

const rootEl = document.getElementById("root");
if (!rootEl) {
  document.body.innerHTML = `
    <div style="padding:40px;text-align:center;font-family:system-ui,sans-serif;">
      <h2 style="color:#e63946">Root element not found</h2>
      <p>The app could not mount because the #root element is missing from index.html.</p>
    </div>
  `;
} else {
  try {
    ReactDOM.createRoot(rootEl).render(
      <React.StrictMode>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </React.StrictMode>
    );
  } catch (e) {
    console.error("Failed to render React app:", e);
    rootEl.innerHTML = `
      <div style="padding:40px;text-align:center;font-family:system-ui,sans-serif;">
        <h2 style="color:#e63946">App failed to load</h2>
        <pre style="background:#f4f5f9;padding:16px;border-radius:8px;text-align:left;overflow:auto;">${e.message}</pre>
        <button onclick="window.location.reload()" style="margin-top:24px;padding:10px 24px;background:#4361ee;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;">Reload</button>
      </div>
    `;
  }
}
