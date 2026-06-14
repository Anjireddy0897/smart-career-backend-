import React, { useEffect, useRef, useState } from "react";

export default function ChatAssistant({ apiBaseUrl = "http://127.0.0.1:5001" }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Ask me anything about careers or how the app works.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedMessage = message.trim();
    if (!trimmedMessage || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setMessages((current) => [...current, { role: "user", text: trimmedMessage }]);
    setMessage("");

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: trimmedMessage }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || "Failed to get a chat response.");
      }

      setMessages((current) => [...current, { role: "assistant", text: data.reply || "No response returned." }]);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      style={{
        maxWidth: 760,
        margin: "0 auto",
        padding: 20,
        borderRadius: 20,
        background: "linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",
        border: "1px solid #e2e8f0",
        boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
      }}
    >
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ margin: 0, fontSize: 22 }}>Career Chat</h3>
        <p style={{ margin: "6px 0 0", color: "#64748b" }}>Connected to the Flask backend on port 5001.</p>
      </div>

      <div
        style={{
          minHeight: 220,
          maxHeight: 320,
          overflowY: "auto",
          padding: 16,
          borderRadius: 16,
          background: "white",
          border: "1px solid #e2e8f0",
          display: "grid",
          gap: 12,
          marginBottom: 16,
        }}
      >
        {messages.map((item, index) => (
          <div
            key={`${item.role}-${index}`}
            style={{
              justifySelf: item.role === "user" ? "end" : "start",
              maxWidth: "85%",
              padding: "12px 14px",
              borderRadius: 16,
              background: item.role === "user" ? "#2563eb" : "#e2e8f0",
              color: item.role === "user" ? "white" : "#0f172a",
              whiteSpace: "pre-wrap",
              lineHeight: 1.5,
            }}
          >
            {item.text}
          </div>
        ))}
        {loading && (
          <div style={{ justifySelf: "start", padding: "12px 14px", borderRadius: 16, background: "#e2e8f0", color: "#0f172a" }}>
            Thinking...
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about careers, the assessment, or integration questions"
          rows={3}
          style={{
            width: "100%",
            resize: "vertical",
            padding: 14,
            borderRadius: 14,
            border: "1px solid #cbd5e1",
            fontFamily: "inherit",
            fontSize: 15,
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            justifySelf: "start",
            padding: "12px 20px",
            borderRadius: 999,
            border: "none",
            background: loading ? "#94a3b8" : "linear-gradient(90deg, #2563eb, #7c3aed)",
            color: "white",
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Sending..." : "Send Message"}
        </button>
      </form>

      {error ? (
        <div style={{ marginTop: 14, color: "#b91c1c", fontWeight: 600 }}>
          {error}
        </div>
      ) : null}
    </section>
  );
}