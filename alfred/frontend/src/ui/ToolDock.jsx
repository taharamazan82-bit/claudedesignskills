import React from "react";

// Animated tool dock. Tools are placeholders for now; each future module wires
// its capability here (research, video, system control, voice…).
const TOOLS = [
  { id: "chat", label: "Sohbet", icon: "💬", ready: true },
  { id: "voice", label: "Ses", icon: "🎙️", ready: false },
  { id: "research", label: "Araştır", icon: "🔎", ready: false },
  { id: "video", label: "Video", icon: "🎬", ready: false },
  { id: "system", label: "Sistem", icon: "🖥️", ready: false },
  { id: "youtube", label: "YouTube", icon: "▶️", ready: false },
];

export default function ToolDock() {
  return (
    <div className="dock" role="toolbar" aria-label="Alfred araçları">
      {TOOLS.map((t, i) => (
        <button
          key={t.id}
          className={`tool ${t.ready ? "ready" : "soon"}`}
          style={{ animationDelay: `${i * 60}ms` }}
          title={t.ready ? t.label : `${t.label} (yakında)`}
          disabled={!t.ready}
        >
          <span className="tool-icon">{t.icon}</span>
          <span className="tool-label">{t.label}</span>
        </button>
      ))}
    </div>
  );
}
