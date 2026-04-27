import React, { useState } from "react";

const API_BASE_URL = "http://localhost:8000";

export default function BriefForge() {
  const [input, setInput] = useState("");
  const [chatResult, setChatResult] = useState("");
  const [briefResult, setBriefResult] = useState(null);
  const [markdownResult, setMarkdownResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runRequest(path, body) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const details = await response.text();
      throw new Error(`Request failed (${response.status}): ${details}`);
    }
    return response.json();
  }

  async function handleChat() {
    setLoading(true);
    setError("");
    try {
      const data = await runRequest("/chat", { message: input });
      setChatResult(data.response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleExtract() {
    setLoading(true);
    setError("");
    try {
      const data = await runRequest("/extract-brief", { text: input });
      setBriefResult(data.brief);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateMarkdown() {
    if (!briefResult) {
      setError("No brief available. Run extract first.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const data = await runRequest("/generate-md", { brief: briefResult });
      setMarkdownResult(data.markdown);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 960, margin: "24px auto", fontFamily: "sans-serif" }}>
      <h1>BriefForge</h1>
      <p>Sheet metal engineering briefing agent</p>

      <textarea
        rows={8}
        style={{ width: "100%", padding: 12 }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Paste product requirements, customer notes, or rough brief..."
      />

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button disabled={loading || !input.trim()} onClick={handleChat}>
          /chat
        </button>
        <button disabled={loading || !input.trim()} onClick={handleExtract}>
          /extract-brief
        </button>
        <button disabled={loading || !briefResult} onClick={handleGenerateMarkdown}>
          /generate-md
        </button>
      </div>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      {chatResult ? (
        <section>
          <h2>Chat Response</h2>
          <pre>{chatResult}</pre>
        </section>
      ) : null}

      {briefResult ? (
        <section>
          <h2>Extracted Brief JSON</h2>
          <pre>{JSON.stringify(briefResult, null, 2)}</pre>
        </section>
      ) : null}

      {markdownResult ? (
        <section>
          <h2>Generated Markdown</h2>
          <pre>{markdownResult}</pre>
        </section>
      ) : null}
    </div>
  );
}
