import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: 40,
          fontFamily: "system-ui, sans-serif",
          textAlign: "center",
          color: "#1a1a2e",
        }}>
          <h2 style={{ color: "#e63946", marginBottom: 16 }}>Something went wrong</h2>
          <p style={{ marginBottom: 24, color: "#555" }}>
            The app encountered an error while loading. Try refreshing the page.
          </p>
          <pre style={{
            background: "#f4f5f9",
            padding: 16,
            borderRadius: 8,
            textAlign: "left",
            overflow: "auto",
            fontSize: "0.85rem",
            color: "#721c24",
            border: "1px solid #f8d7da",
          }}>
            {this.state.error?.toString?.() || "Unknown error"}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: 24,
              padding: "10px 24px",
              background: "#4361ee",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
