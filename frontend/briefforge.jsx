"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8007";

export default function BriefForge() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [briefResult, setBriefResult] = useState(null);
  const [markdownResult, setMarkdownResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [isGeneratingMd, setIsGeneratingMd] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("extract");
  const [copiedMessageKey, setCopiedMessageKey] = useState("");

  async function runRequest(path, body) {
    console.info(`[BriefForge] Request start: ${path}`, body);
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const details = await response.text();
      console.error(`[BriefForge] Request failed: ${path}`, { status: response.status, details });
      throw new Error(`Request failed (${response.status}): ${details}`);
    }
    const data = await response.json();
    console.info(`[BriefForge] Request success: ${path}`, data);
    return data;
  }

  async function handleSendChat() {
    console.log("[BriefForge] handleSendChat:start", {
      inputLength: input.trim().length,
      historyLength: chatHistory.length,
    });
    setLoading(true);
    setIsSendingChat(true);
    setError("");
    try {
      const data = await runRequest("/chat", {
        message: input,
        history: chatHistory,
      });
      setChatHistory((prev) => [
        ...prev,
        { role: "user", content: input },
        { role: "assistant", content: data.response },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Send Chat failed.");
    } finally {
      setLoading(false);
      setIsSendingChat(false);
      console.log("[BriefForge] handleSendChat:end", {
        loadingEnded: true,
      });
    }
  }

  async function handleExtract() {
    setLoading(true);
    setError("");
    try {
      const data = await runRequest("/extract-brief", { text: input });
      setBriefResult(data.brief);
      setActiveTab("extract");
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
    setIsGeneratingMd(true);
    setError("");
    try {
      const data = await runRequest("/generate-md", { brief: briefResult });
      setMarkdownResult(data.markdown);
      setActiveTab("markdown");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generate MD failed.");
    } finally {
      setLoading(false);
      setIsGeneratingMd(false);
    }
  }

  function handleNewBrief() {
    setInput("");
    setChatHistory([]);
    setBriefResult(null);
    setMarkdownResult("");
    setError("");
    setActiveTab("extract");
  }

  async function handleCopyMessage(messageKey, content) {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageKey(messageKey);
      setTimeout(() => {
        setCopiedMessageKey((prev) => (prev === messageKey ? "" : prev));
      }, 2000);
    } catch {
      setError("Clipboard copy failed.");
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0b0f19",
        color: "#e5e7eb",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        padding: "24px 16px",
      }}
    >
      <div style={{ maxWidth: 1120, margin: "0 auto" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 8,
          }}
        >
          <h1 style={{ margin: 0, fontSize: 30, color: "#f9fafb" }}>BriefForge</h1>
          <button
            disabled={loading}
            onClick={handleNewBrief}
            style={{
              border: "1px solid #374151",
              background: "#111827",
              color: "#e5e7eb",
              borderRadius: 8,
              padding: "10px 14px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            New Brief
          </button>
        </div>
        <p style={{ marginTop: 0, color: "#9ca3af" }}>Sheet metal engineering briefing agent</p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.1fr 1fr",
            gap: 16,
          }}
        >
          <section
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 12,
              padding: 16,
              minHeight: 620,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: 12, fontSize: 18 }}>Conversation</h2>

            <div
              style={{
                flex: 1,
                overflowY: "auto",
                border: "1px solid #1f2937",
                borderRadius: 10,
                padding: 12,
                background: "#0f172a",
                marginBottom: 12,
              }}
            >
              {chatHistory.length === 0 ? (
                <p style={{ color: "#6b7280", margin: 0 }}>
                  No messages yet. Send a prompt to start the conversation.
                </p>
              ) : (
                chatHistory.map((msg, idx) => {
                  const isUser = msg.role === "user";
                  return (
                    <div
                      key={`${msg.role}-${idx}`}
                      style={{
                        display: "flex",
                        justifyContent: isUser ? "flex-end" : "flex-start",
                        marginBottom: 10,
                      }}
                    >
                      <div
                        style={{
                          position: "relative",
                          maxWidth: "78%",
                          whiteSpace: isUser ? "pre-wrap" : "normal",
                          lineHeight: 1.45,
                          padding: "10px 12px",
                          borderRadius: 12,
                          background: isUser ? "#2563eb" : "#1f2937",
                          color: "#f9fafb",
                          border: isUser ? "1px solid #3b82f6" : "1px solid #374151",
                        }}
                      >
                        {!isUser ? (
                          <button
                            onClick={() => handleCopyMessage(`${msg.role}-${idx}`, msg.content)}
                            style={copyButtonStyle}
                          >
                            {copiedMessageKey === `${msg.role}-${idx}` ? "Copied!" : "Copy"}
                          </button>
                        ) : null}
                        {isUser ? (
                          msg.content
                        ) : (
                          <div style={assistantBubbleMarkdownStyle}>
                            <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                              {msg.content}
                            </ReactMarkdown>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            <textarea
              rows={6}
              style={{
                width: "100%",
                padding: 12,
                borderRadius: 10,
                border: "1px solid #374151",
                background: "#0f172a",
                color: "#e5e7eb",
                resize: "vertical",
                marginBottom: 12,
              }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="S235, S355, Al6061, DX51D, Al5083, S304 desteklenir"
            />

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button
                disabled={loading || !input.trim()}
                onClick={handleSendChat}
                style={actionButtonStyle}
              >
                {isSendingChat ? "Sending..." : "Send Chat"}
              </button>
              <button
                disabled={loading}
                onClick={handleExtract}
                style={actionButtonStyle}
              >
                Extract Brief
              </button>
              <button
                disabled={loading}
                onClick={handleGenerateMarkdown}
                style={actionButtonStyle}
              >
                {isGeneratingMd ? "Generating..." : "Generate MD"}
              </button>
            </div>
            {error ? <p style={{ color: "#f87171", marginBottom: 0 }}>{error}</p> : null}
          </section>

          <section
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 12,
              padding: 16,
              minHeight: 620,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
              <button
                onClick={() => setActiveTab("extract")}
                style={tabStyle(activeTab === "extract")}
              >
                Extract Brief
              </button>
              <button
                onClick={() => setActiveTab("markdown")}
                style={tabStyle(activeTab === "markdown")}
              >
                Generated MD
              </button>
            </div>

            <div
              style={{
                flex: 1,
                overflowY: "auto",
                border: "1px solid #1f2937",
                borderRadius: 10,
                padding: 12,
                background: "#0f172a",
              }}
            >
              {activeTab === "extract" ? (
                briefResult ? (
                  <pre style={{ margin: 0, color: "#d1d5db", lineHeight: 1.45 }}>
                    {JSON.stringify(briefResult, null, 2)}
                  </pre>
                ) : (
                  <p style={{ margin: 0, color: "#6b7280" }}>
                    Extracted brief will appear here as JSON.
                  </p>
                )
              ) : markdownResult ? (
                <div style={markdownContainerStyle}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                    {markdownResult}
                  </ReactMarkdown>
                </div>
              ) : (
                <p style={{ margin: 0, color: "#6b7280" }}>
                  Generated markdown will render here with headings, tables, and formatting.
                </p>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

const actionButtonStyle = {
  border: "1px solid #374151",
  background: "#1f2937",
  color: "#f9fafb",
  borderRadius: 8,
  padding: "10px 12px",
  cursor: "pointer",
  fontWeight: 600,
};

const tabStyle = (active) => ({
  border: active ? "1px solid #3b82f6" : "1px solid #374151",
  background: active ? "#1e3a8a" : "#111827",
  color: "#f9fafb",
  borderRadius: 8,
  padding: "8px 12px",
  cursor: "pointer",
  fontWeight: 600,
});

const markdownContainerStyle = {
  color: "#e5e7eb",
  lineHeight: 1.6,
};

const assistantBubbleMarkdownStyle = {
  color: "#e5e7eb",
  lineHeight: 1.5,
  paddingTop: 24,
};

const copyButtonStyle = {
  position: "absolute",
  top: 8,
  right: 8,
  border: "1px solid #4b5563",
  background: "#0b1220",
  color: "#e5e7eb",
  borderRadius: 6,
  padding: "2px 8px",
  fontSize: 12,
  cursor: "pointer",
};

const markdownComponents = {
  h1: (props) => <h1 style={{ fontSize: 28, color: "#f9fafb", marginBottom: 12 }} {...props} />,
  h2: (props) => <h2 style={{ fontSize: 22, color: "#f9fafb", marginBottom: 10 }} {...props} />,
  h3: (props) => <h3 style={{ fontSize: 18, color: "#f9fafb", marginBottom: 8 }} {...props} />,
  p: (props) => <p style={{ margin: "8px 0", color: "#d1d5db" }} {...props} />,
  strong: (props) => <strong style={{ color: "#ffffff" }} {...props} />,
  table: (props) => (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        border: "1px solid #374151",
        margin: "12px 0",
      }}
      {...props}
    />
  ),
  th: (props) => (
    <th
      style={{
        border: "1px solid #374151",
        background: "#1f2937",
        color: "#f9fafb",
        padding: "8px 10px",
        textAlign: "left",
      }}
      {...props}
    />
  ),
  td: (props) => (
    <td
      style={{
        border: "1px solid #374151",
        color: "#d1d5db",
        padding: "8px 10px",
      }}
      {...props}
    />
  ),
  code: (props) => (
    <code
      style={{
        background: "#111827",
        border: "1px solid #374151",
        borderRadius: 6,
        padding: "1px 5px",
      }}
      {...props}
    />
  ),
};
