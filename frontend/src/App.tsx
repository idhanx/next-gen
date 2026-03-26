import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "";

type Entry = {
  id: number;
  timestamp: string;
  src_ip: string;
  dst_ip: string;
  protocol: string;
  pred_label: number;
  true_label: number;
  result: string;
  attack_type: string;
  confidence: number;
  correct: boolean;
};

type Stats = {
  total: number; attacks: number; normal: number;
  correct: number; accuracy: number; dataset_size: number;
};

export default function App() {
  const [log, setLog] = useState<Entry[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, attacks: 0, normal: 0, correct: 0, accuracy: 0, dataset_size: 0 });
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const poll = async () => {
      try {
        const res = await fetch(`${API}/feed`);
        const data = await res.json();
        setLog(data.log);
        setStats(data.stats);
        setConnected(true);
      } catch { setConnected(false); }
    };
    poll();
    const id = setInterval(poll, 1500);
    return () => clearInterval(id);
  }, []);

  const attackRate = stats.total > 0 ? ((stats.attacks / stats.total) * 100).toFixed(1) : "0.0";

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "1.5rem 1rem", fontFamily: "system-ui, sans-serif", background: "#0f172a", minHeight: "100vh", color: "#e2e8f0" }}>

      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700 }}>🛡️ Network Threat Monitor</h1>
          <p style={{ color: "#64748b", fontSize: "0.82rem" }}>
            Replaying real NSL-KDD intrusion detection dataset · {stats.dataset_size.toLocaleString()} records
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem" }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: connected ? "#22c55e" : "#ef4444" }} />
          {connected ? "Live" : "Disconnected"}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
        <StatCard label="Analyzed" value={stats.total} color="#3b82f6" icon="📊" />
        <StatCard label="Normal" value={stats.normal} color="#22c55e" icon="✅" />
        <StatCard label="Attacks" value={stats.attacks} color="#ef4444" icon="🚨" />
        <StatCard label="Model Accuracy" value={`${stats.accuracy}%`} color="#a855f7" icon="🎯" />
      </div>

      {/* Attack rate bar */}
      <div style={{ background: "#1e293b", borderRadius: 10, padding: "1rem", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem", fontSize: "0.85rem" }}>
          <span>Attack Rate</span>
          <span style={{ color: Number(attackRate) > 50 ? "#ef4444" : "#22c55e", fontWeight: 700 }}>{attackRate}%</span>
        </div>
        <div style={{ background: "#0f172a", borderRadius: 999, height: 10, overflow: "hidden" }}>
          <div style={{
            height: "100%", borderRadius: 999, width: `${attackRate}%`,
            background: Number(attackRate) > 50 ? "#ef4444" : "#f59e0b",
            transition: "width 0.5s ease",
          }} />
        </div>
      </div>

      {/* Live feed */}
      <div style={{ background: "#1e293b", borderRadius: 10, overflow: "hidden" }}>
        <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #334155", fontSize: "0.85rem", fontWeight: 600, color: "#94a3b8" }}>
          Live Traffic Feed — Real NSL-KDD Records
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
            <thead>
              <tr style={{ background: "#0f172a", color: "#64748b" }}>
                {["Time", "Src IP", "Dst IP", "Proto", "Prediction", "Attack Type", "Confidence", "Correct?"].map(h => (
                  <th key={h} style={{ padding: "0.6rem 0.75rem", textAlign: "left", fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {log.length === 0 ? (
                <tr><td colSpan={8} style={{ padding: "2rem", textAlign: "center", color: "#475569" }}>Loading real traffic data...</td></tr>
              ) : log.map((e, i) => (
                <tr key={e.id} style={{ borderTop: "1px solid #0f172a", background: i % 2 === 0 ? "#1e293b" : "#162032" }}>
                  <td style={{ padding: "0.5rem 0.75rem", color: "#64748b" }}>{e.timestamp}</td>
                  <td style={{ padding: "0.5rem 0.75rem", fontFamily: "monospace", fontSize: "0.75rem" }}>{e.src_ip}</td>
                  <td style={{ padding: "0.5rem 0.75rem", fontFamily: "monospace", fontSize: "0.75rem" }}>{e.dst_ip}</td>
                  <td style={{ padding: "0.5rem 0.75rem" }}>
                    <span style={{ background: "#0f172a", padding: "2px 6px", borderRadius: 4, fontSize: "0.72rem" }}>{e.protocol}</span>
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem" }}>
                    <span style={{
                      padding: "2px 10px", borderRadius: 999, fontSize: "0.72rem", fontWeight: 600,
                      background: e.pred_label === 1 ? "#450a0a" : "#052e16",
                      color: e.pred_label === 1 ? "#f87171" : "#4ade80",
                    }}>
                      {e.pred_label === 1 ? "🚨 Attack" : "✅ Normal"}
                    </span>
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem", color: e.attack_type !== "-" ? "#fb923c" : "#475569" }}>
                    {e.attack_type}
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem", color: e.pred_label === 1 ? "#f87171" : "#4ade80" }}>
                    {e.confidence}%
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem" }}>
                    <span style={{ color: e.correct ? "#4ade80" : "#f87171", fontWeight: 600 }}>
                      {e.correct ? "✓" : "✗"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color, icon }: { label: string; value: number | string; color: string; icon: string }) {
  return (
    <div style={{ background: "#1e293b", borderRadius: 10, padding: "1rem", borderLeft: `3px solid ${color}` }}>
      <div style={{ fontSize: "1.4rem", marginBottom: "0.25rem" }}>{icon}</div>
      <div style={{ fontSize: "1.5rem", fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: "0.78rem", color: "#64748b" }}>{label}</div>
    </div>
  );
}
