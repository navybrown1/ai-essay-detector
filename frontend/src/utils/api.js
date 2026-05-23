const API_BASE = "/api";

export async function analyzeText(text, title, filename, authorId) {
  const form = new FormData();
  form.append("text", text);
  form.append("title", title || "Untitled");
  form.append("filename", filename || "pasted_text");
  if (authorId) form.append("author_id", authorId);
  const res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
  return res.json();
}

export async function analyzeFile(file, title, authorId) {
  const form = new FormData();
  form.append("file", file);
  form.append("title", title || file.name);
  form.append("filename", file.name);
  if (authorId) form.append("author_id", authorId);
  const res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
  return res.json();
}

export async function getHistory(limit = 20) {
  const res = await fetch(`${API_BASE}/history?limit=${limit}`);
  return res.json();
}

export async function getScan(id) {
  const res = await fetch(`${API_BASE}/scan/${id}`);
  if (!res.ok) throw new Error("Scan not found");
  return res.json();
}

export async function deleteScan(id) {
  await fetch(`${API_BASE}/scan/${id}`, { method: "DELETE" });
}

export async function downloadReport(id) {
  const res = await fetch(`${API_BASE}/report/${id}`);
  if (!res.ok) throw new Error("Report not available");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `essay_report_${id}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function compareScans(ids) {
  const res = await fetch(`${API_BASE}/compare?ids=${ids.join(",")}`);
  return res.json();
}

// ---- AI-Powered Endpoints ---- //

export async function aiAnalyze(text, apiKey) {
  const res = await fetch(`${API_BASE}/ai-analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, api_key: apiKey || undefined }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "AI analysis failed");
  return res.json();
}

export async function aiImprove(text, highlightedSections, apiKey) {
  const res = await fetch(`${API_BASE}/ai-improve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      highlighted_sections: highlightedSections,
      api_key: apiKey || undefined,
    }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "AI improvement failed");
  return res.json();
}

export async function aiGenerateReport(scanId, data, apiKey) {
  const body = { ...data, api_key: apiKey || undefined };
  const res = await fetch(`${API_BASE}/ai-report/${scanId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("AI report generation failed");
  return res.json();
}
