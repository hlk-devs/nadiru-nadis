import { useState, useEffect, useRef, useCallback } from "react";

const ENGINE = "http://localhost:8765";

// ─── API Layer ───────────────────────────────────────────
async function apiConnect() {
  const res = await fetch(`${ENGINE}/connect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "nadi-dashboard", description: "Web dashboard", default_priority: "balanced" }),
  });
  return res.json();
}

async function apiGenerate(nadiId, prompt, priority, messages) {
  const payload = { nadi_id: nadiId, prompt, priority };
  if (messages?.length) payload.messages = messages;
  const res = await fetch(`${ENGINE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

async function apiQuery(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${ENGINE}/query?${qs}`);
  return res.json();
}

async function apiHealth() {
  const res = await fetch(`${ENGINE}/health`);
  return res.json();
}

// ─── Utilities ───────────────────────────────────────────
function formatCost(c) {
  if (c === 0) return "free";
  if (c < 0.001) return `$${c.toFixed(6)}`;
  if (c < 0.01) return `$${c.toFixed(4)}`;
  return `$${c.toFixed(3)}`;
}

function formatLatency(ms) {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60000) return "just now";
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  return `${Math.floor(diff / 3600000)}h ago`;
}

// ─── Markdown-lite renderer ──────────────────────────────
function renderContent(text) {
  if (!text) return null;
  const blocks = text.split(/```(\w*)\n?([\s\S]*?)```/g);
  const result = [];
  for (let i = 0; i < blocks.length; i++) {
    if (i % 3 === 0) {
      // Regular text
      const lines = blocks[i].split("\n").filter(Boolean);
      lines.forEach((line, j) => {
        if (line.startsWith("### ")) {
          result.push(<h4 key={`${i}-${j}`} style={{ fontSize: 13, fontWeight: 600, letterSpacing: "0.02em", textTransform: "uppercase", color: "var(--text-tertiary)", margin: "16px 0 6px" }}>{line.slice(4)}</h4>);
        } else if (line.startsWith("## ")) {
          result.push(<h3 key={`${i}-${j}`} style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", margin: "18px 0 8px" }}>{line.slice(3)}</h3>);
        } else if (line.startsWith("# ")) {
          result.push(<h2 key={`${i}-${j}`} style={{ fontSize: 17, fontWeight: 600, color: "var(--text-primary)", margin: "20px 0 10px" }}>{line.slice(2)}</h2>);
        } else if (line.startsWith("- ") || line.startsWith("* ")) {
          result.push(<div key={`${i}-${j}`} style={{ paddingLeft: 16, position: "relative", margin: "3px 0" }}><span style={{ position: "absolute", left: 4, color: "var(--text-tertiary)" }}>·</span>{renderInline(line.slice(2))}</div>);
        } else if (/^\d+\.\s/.test(line)) {
          const num = line.match(/^(\d+)\.\s/)[1];
          result.push(<div key={`${i}-${j}`} style={{ paddingLeft: 20, position: "relative", margin: "3px 0" }}><span style={{ position: "absolute", left: 0, color: "var(--text-tertiary)", fontSize: 12 }}>{num}.</span>{renderInline(line.replace(/^\d+\.\s/, ""))}</div>);
        } else {
          result.push(<p key={`${i}-${j}`} style={{ margin: "6px 0", lineHeight: 1.6 }}>{renderInline(line)}</p>);
        }
      });
    } else if (i % 3 === 1) {
      // Language tag — skip
    } else {
      // Code block
      result.push(
        <pre key={`code-${i}`} style={{
          background: "var(--surface-code)",
          borderRadius: 8,
          padding: "14px 16px",
          fontSize: 12.5,
          lineHeight: 1.55,
          overflowX: "auto",
          margin: "10px 0",
          border: "1px solid var(--border-subtle)",
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          color: "var(--text-code)",
        }}>
          <code>{blocks[i]}</code>
        </pre>
      );
    }
  }
  return result;
}

function renderInline(text) {
  // Bold, inline code, italic
  const parts = text.split(/(\*\*.*?\*\*|`[^`]+`|_.*?_)/g);
  return parts.map((p, i) => {
    if (p.startsWith("**") && p.endsWith("**")) return <strong key={i} style={{ fontWeight: 600 }}>{p.slice(2, -2)}</strong>;
    if (p.startsWith("`") && p.endsWith("`")) return <code key={i} style={{ background: "var(--surface-code)", padding: "1px 5px", borderRadius: 4, fontSize: "0.9em", fontFamily: "'JetBrains Mono', monospace", color: "var(--accent)" }}>{p.slice(1, -1)}</code>;
    if (p.startsWith("_") && p.endsWith("_") && p.length > 2) return <em key={i}>{p.slice(1, -1)}</em>;
    return p;
  });
}

// ─── Components ──────────────────────────────────────────

function RoutingPill({ provider, model, cost, latency, reason, onClick }) {
  const isLocal = provider === "ollama";
  return (
    <div onClick={onClick} style={{
      display: "inline-flex", alignItems: "center", gap: 8,
      padding: "5px 12px", borderRadius: 20,
      background: isLocal ? "var(--surface-local)" : "var(--surface-cloud)",
      border: `1px solid ${isLocal ? "var(--border-local)" : "var(--border-cloud)"}`,
      fontSize: 11.5, color: "var(--text-secondary)",
      cursor: "pointer", transition: "all 0.2s ease",
      marginTop: 6, maxWidth: "100%",
    }}>
      <span style={{ fontWeight: 600, color: isLocal ? "var(--accent-local)" : "var(--accent-cloud)" }}>
        {provider}/{model?.split("-").slice(0, 3).join("-")}
      </span>
      <span style={{ opacity: 0.5 }}>·</span>
      <span>{formatCost(cost)}</span>
      <span style={{ opacity: 0.5 }}>·</span>
      <span>{formatLatency(latency)}</span>
    </div>
  );
}

function CostTicker({ total, local, delegated }) {
  return (
    <div style={{
      display: "flex", gap: 20, fontSize: 12,
      color: "var(--text-tertiary)", padding: "0 4px",
    }}>
      <span><strong style={{ color: "var(--text-secondary)", fontWeight: 600 }}>{formatCost(total)}</strong> total</span>
      <span><strong style={{ color: "var(--accent-local)", fontWeight: 600 }}>{local}</strong> local</span>
      <span><strong style={{ color: "var(--accent-cloud)", fontWeight: 600 }}>{delegated}</strong> delegated</span>
    </div>
  );
}

function PrioritySelector({ value, onChange }) {
  const opts = ["cost", "balanced", "quality"];
  return (
    <div style={{ display: "flex", gap: 2, background: "var(--surface-inset)", borderRadius: 8, padding: 2 }}>
      {opts.map(o => (
        <button key={o} onClick={() => onChange(o)} style={{
          padding: "5px 14px", borderRadius: 6, border: "none",
          fontSize: 11.5, fontWeight: value === o ? 600 : 400,
          background: value === o ? "var(--surface-primary)" : "transparent",
          color: value === o ? "var(--text-primary)" : "var(--text-tertiary)",
          cursor: "pointer", transition: "all 0.15s ease",
          boxShadow: value === o ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
        }}>{o}</button>
      ))}
    </div>
  );
}

function InsightsPanel({ interactions, isOpen, onClose }) {
  if (!isOpen) return null;

  const totalCost = interactions.reduce((s, i) => s + (i.cost_estimate || 0), 0);
  const localCount = interactions.filter(i => i.provider === "ollama").length;
  const providerMap = {};
  interactions.forEach(i => {
    const key = `${i.provider}/${i.model}`;
    if (!providerMap[key]) providerMap[key] = { count: 0, cost: 0 };
    providerMap[key].count++;
    providerMap[key].cost += i.cost_estimate || 0;
  });
  const sorted = Object.entries(providerMap).sort((a, b) => b[1].count - a[1].count);

  return (
    <div style={{
      position: "fixed", top: 0, right: 0, bottom: 0, width: 340,
      background: "var(--surface-panel)", borderLeft: "1px solid var(--border-subtle)",
      zIndex: 100, display: "flex", flexDirection: "column",
      animation: "slideIn 0.25s ease",
    }}>
      <div style={{ padding: "20px 20px 14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 13, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase", color: "var(--text-tertiary)" }}>Session Insights</span>
        <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 18, color: "var(--text-tertiary)", cursor: "pointer", padding: 4 }}>×</button>
      </div>

      <div style={{ padding: "0 20px 20px", flex: 1, overflowY: "auto" }}>
        {/* Summary */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 24 }}>
          <div style={{ background: "var(--surface-inset)", borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text-primary)" }}>{formatCost(totalCost)}</div>
            <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 2 }}>total spend</div>
          </div>
          <div style={{ background: "var(--surface-inset)", borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text-primary)" }}>{interactions.length}</div>
            <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 2 }}>interactions</div>
          </div>
          <div style={{ background: "var(--surface-inset)", borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: "var(--accent-local)" }}>{localCount}</div>
            <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 2 }}>handled locally</div>
          </div>
          <div style={{ background: "var(--surface-inset)", borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: "var(--accent-cloud)" }}>{interactions.length - localCount}</div>
            <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 2 }}>delegated</div>
          </div>
        </div>

        {/* Model breakdown */}
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase", color: "var(--text-tertiary)", marginBottom: 10 }}>Model Usage</div>
        {sorted.map(([key, data]) => {
          const pct = Math.round((data.count / interactions.length) * 100);
          return (
            <div key={key} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>{key.split("/").pop()}</span>
                <span style={{ color: "var(--text-tertiary)" }}>{data.count}× · {formatCost(data.cost)}</span>
              </div>
              <div style={{ height: 4, background: "var(--surface-inset)", borderRadius: 2, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${pct}%`, background: key.includes("ollama") ? "var(--accent-local)" : "var(--accent-cloud)", borderRadius: 2, transition: "width 0.5s ease" }} />
              </div>
            </div>
          );
        })}

        {/* Recent routing */}
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase", color: "var(--text-tertiary)", marginTop: 24, marginBottom: 10 }}>Routing Feed</div>
        {interactions.slice(0, 20).map((ix, idx) => (
          <div key={idx} style={{
            padding: "8px 0", borderBottom: "1px solid var(--border-subtle)",
            fontSize: 11.5, lineHeight: 1.5,
          }}>
            <div style={{ color: "var(--text-secondary)", fontWeight: 500 }}>
              {ix.prompt?.slice(0, 50)}{ix.prompt?.length > 50 ? "..." : ""}
            </div>
            <div style={{ color: "var(--text-tertiary)", marginTop: 2 }}>
              {ix.provider}/{ix.model?.split("-").slice(0, 3).join("-")} · {formatCost(ix.cost_estimate)} · {ix.routing_reason?.slice(0, 60)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main App ────────────────────────────────────────────
export default function NadiruDashboard() {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [nadiId, setNadiId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [priority, setPriority] = useState("balanced");
  const [showInsights, setShowInsights] = useState(false);
  const [interactions, setInteractions] = useState([]);
  const [health, setHealth] = useState(null);
  const [expandedRouting, setExpandedRouting] = useState(null);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Connect on mount
  useEffect(() => {
    (async () => {
      try {
        const h = await apiHealth();
        setHealth(h);
        const conn = await apiConnect();
        setNadiId(conn.nadi_id);
        setConnected(true);
      } catch (e) {
        setError("Cannot connect to Nadiru engine. Is it running on localhost:8765?");
      }
    })();
  }, []);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Refresh interactions periodically
  useEffect(() => {
    if (!nadiId) return;
    const load = async () => {
      try {
        const q = await apiQuery({ nadi_id: nadiId, limit: 100 });
        setInteractions(q.interactions || []);
      } catch {}
    };
    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, [nadiId]);

  const send = useCallback(async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const result = await apiGenerate(nadiId, userMsg, priority, history);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: result.content,
        routing: {
          provider: result.provider,
          model: result.model,
          cost: result.cost_estimate,
          latency: result.latency_ms,
          reason: result.routing_reason,
          requestId: result.request_id,
        },
      }]);
      setHistory(prev => [
        ...prev,
        { role: "user", content: userMsg },
        { role: "assistant", content: result.content },
      ].slice(-40));
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: "Error: " + e.message, error: true }]);
    }
    setLoading(false);
    inputRef.current?.focus();
  }, [input, loading, nadiId, priority, history]);

  const totalCost = interactions.reduce((s, i) => s + (i.cost_estimate || 0), 0);
  const localCount = interactions.filter(i => i.provider === "ollama").length;
  const delegatedCount = interactions.length - localCount;

  if (error) {
    return (
      <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 16, fontFamily: "var(--font-body)" }}>
        <div style={{ fontSize: 40, opacity: 0.15 }}>⚡</div>
        <div style={{ fontSize: 15, color: "var(--text-secondary)", maxWidth: 400, textAlign: "center", lineHeight: 1.6 }}>{error}</div>
        <button onClick={() => window.location.reload()} style={{
          padding: "8px 20px", borderRadius: 8, border: "1px solid var(--border-subtle)",
          background: "var(--surface-primary)", color: "var(--text-secondary)",
          fontSize: 13, cursor: "pointer",
        }}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "var(--bg)", fontFamily: "var(--font-body)", color: "var(--text-primary)" }}>
      <style>{`
        :root {
          --bg: #0a0a0b;
          --surface-primary: #141416;
          --surface-inset: #1a1a1e;
          --surface-panel: #111113;
          --surface-code: #0d0d0f;
          --surface-local: rgba(52, 211, 153, 0.06);
          --surface-cloud: rgba(99, 149, 255, 0.06);
          --border-subtle: rgba(255, 255, 255, 0.06);
          --border-local: rgba(52, 211, 153, 0.15);
          --border-cloud: rgba(99, 149, 255, 0.15);
          --text-primary: #e8e8ed;
          --text-secondary: #a0a0ab;
          --text-tertiary: #5c5c66;
          --text-code: #c4c4cc;
          --accent: #7c8aff;
          --accent-local: #34d399;
          --accent-cloud: #6395ff;
          --font-body: 'DM Sans', -apple-system, system-ui, sans-serif;
          --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        }
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: var(--bg); }
        
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
        
        .msg-enter { animation: fadeUp 0.3s ease; }
        
        input::placeholder { color: var(--text-tertiary); }
        input:focus { outline: none; }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }
      `}</style>

      {/* ─── Header ─────────────────────────────────────── */}
      <div style={{
        padding: "14px 24px", display: "flex", alignItems: "center",
        justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)",
        background: "var(--surface-primary)", flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--text-primary)" }}>
            nadiru
          </div>
          {connected && health && (
            <div style={{ fontSize: 11, color: "var(--text-tertiary)", display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent-local)" }} />
              {health.conductor_model}
            </div>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <CostTicker total={totalCost} local={localCount} delegated={delegatedCount} />
          <PrioritySelector value={priority} onChange={setPriority} />
          <button onClick={() => setShowInsights(!showInsights)} style={{
            background: showInsights ? "var(--accent)" : "var(--surface-inset)",
            color: showInsights ? "#000" : "var(--text-tertiary)",
            border: "none", borderRadius: 8, padding: "6px 12px",
            fontSize: 11.5, fontWeight: 500, cursor: "pointer", transition: "all 0.15s",
          }}>
            Insights
          </button>
        </div>
      </div>

      {/* ─── Chat Area ──────────────────────────────────── */}
      <div style={{
        flex: 1, overflowY: "auto", padding: "24px 0",
        marginRight: showInsights ? 340 : 0, transition: "margin 0.25s ease",
      }}>
        <div style={{ maxWidth: 720, margin: "0 auto", padding: "0 24px" }}>
          {messages.length === 0 && (
            <div style={{
              display: "flex", flexDirection: "column", alignItems: "center",
              justifyContent: "center", height: "50vh", gap: 12, opacity: 0.4,
            }}>
              <div style={{ fontSize: 32 }}>⚡</div>
              <div style={{ fontSize: 14, color: "var(--text-tertiary)" }}>
                Start a conversation. The Conductor routes intelligently.
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className="msg-enter" style={{
              marginBottom: msg.role === "user" ? 8 : 24,
            }}>
              {msg.role === "user" ? (
                <div style={{
                  fontSize: 14.5, lineHeight: 1.6, color: "var(--text-primary)",
                  fontWeight: 500, paddingTop: 16,
                  borderTop: idx > 0 ? "1px solid var(--border-subtle)" : "none",
                }}>
                  {msg.content}
                </div>
              ) : (
                <div>
                  <div style={{
                    fontSize: 14, lineHeight: 1.7, color: "var(--text-secondary)",
                    ...(msg.error ? { color: "#f87171" } : {}),
                  }}>
                    {renderContent(msg.content)}
                  </div>
                  {msg.routing && (
                    <div>
                      <RoutingPill
                        {...msg.routing}
                        onClick={() => setExpandedRouting(expandedRouting === idx ? null : idx)}
                      />
                      {expandedRouting === idx && (
                        <div style={{
                          marginTop: 6, padding: "10px 14px", borderRadius: 8,
                          background: "var(--surface-inset)", fontSize: 12,
                          color: "var(--text-tertiary)", lineHeight: 1.6,
                          animation: "fadeUp 0.2s ease",
                        }}>
                          <div><strong style={{ color: "var(--text-secondary)" }}>Model:</strong> {msg.routing.provider}/{msg.routing.model}</div>
                          <div><strong style={{ color: "var(--text-secondary)" }}>Cost:</strong> {formatCost(msg.routing.cost)}</div>
                          <div><strong style={{ color: "var(--text-secondary)" }}>Latency:</strong> {formatLatency(msg.routing.latency)}</div>
                          <div><strong style={{ color: "var(--text-secondary)" }}>Reason:</strong> {msg.routing.reason}</div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: "flex", gap: 4, padding: "12px 0" }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: "var(--accent)", animation: `pulse 1.2s ease infinite ${i * 0.2}s`,
                }} />
              ))}
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>

      {/* ─── Input ──────────────────────────────────────── */}
      <div style={{
        padding: "16px 24px 20px", borderTop: "1px solid var(--border-subtle)",
        background: "var(--surface-primary)", flexShrink: 0,
        marginRight: showInsights ? 340 : 0, transition: "margin 0.25s ease",
      }}>
        <div style={{ maxWidth: 720, margin: "0 auto", position: "relative" }}>
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
            placeholder="Message Nadiru..."
            disabled={!connected || loading}
            style={{
              width: "100%", padding: "14px 18px", paddingRight: 60,
              borderRadius: 12, border: "1px solid var(--border-subtle)",
              background: "var(--surface-inset)", color: "var(--text-primary)",
              fontSize: 14, fontFamily: "var(--font-body)",
              transition: "border-color 0.15s",
            }}
            onFocus={e => e.target.style.borderColor = "rgba(124,138,255,0.3)"}
            onBlur={e => e.target.style.borderColor = "var(--border-subtle)"}
          />
          <button
            onClick={send}
            disabled={!input.trim() || loading}
            style={{
              position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)",
              width: 36, height: 36, borderRadius: 8,
              background: input.trim() ? "var(--accent)" : "var(--surface-inset)",
              border: "none", cursor: input.trim() ? "pointer" : "default",
              display: "flex", alignItems: "center", justifyContent: "center",
              transition: "all 0.15s",
            }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ opacity: input.trim() ? 1 : 0.3 }}>
              <path d="M3 13L13 8L3 3V7L9 8L3 9V13Z" fill={input.trim() ? "#000" : "var(--text-tertiary)"} />
            </svg>
          </button>
        </div>
      </div>

      {/* ─── Insights Panel ─────────────────────────────── */}
      <InsightsPanel
        interactions={interactions}
        isOpen={showInsights}
        onClose={() => setShowInsights(false)}
      />
    </div>
  );
}
