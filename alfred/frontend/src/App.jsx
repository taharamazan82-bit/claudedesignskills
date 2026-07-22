import React, { useEffect, useState } from "react";
import Avatar from "./Avatar.jsx";
import ChatPanel from "./ui/ChatPanel.jsx";
import ToolDock from "./ui/ToolDock.jsx";
import { useAlfred } from "./store.js";
import { health } from "./api.js";

const STATUS_LABEL = {
  idle: "HAZIR",
  listening: "DİNLİYOR",
  thinking: "DÜŞÜNÜYOR",
  speaking: "KONUŞUYOR",
  error: "HATA",
};

// HUD corner brackets around a panel.
function Corners() {
  return (
    <>
      <span className="corner tl" />
      <span className="corner tr" />
      <span className="corner bl" />
      <span className="corner br" />
    </>
  );
}

function Background() {
  // Decorative animated layers. Pure CSS so lite hardware still copes.
  const dots = Array.from({ length: 18 });
  return (
    <div className="bg" aria-hidden="true">
      <div className="bg-grid" />
      <div className="bg-glow bg-glow-1" />
      <div className="bg-glow bg-glow-2" />
      <div className="bg-particles">
        {dots.map((_, i) => (
          <span key={i} style={{ "--i": i }} />
        ))}
      </div>
      <div className="bg-scan" />
    </div>
  );
}

export default function App() {
  const { status, provider, liteMode, toggleLite } = useAlfred();
  const [backendUp, setBackendUp] = useState(null);

  useEffect(() => {
    health().then(setBackendUp);
  }, []);

  return (
    <div className="app">
      <Background />

      <header className="topbar">
        <div className="brand">
          <span className="logo-dot" />
          <span className="brand-name">ALFRED</span>
          <span className="brand-sub">// virtual assistant</span>
        </div>
        <div className="status-cluster">
          <span className={`pill status-${status}`}>
            <span className="pip" /> {STATUS_LABEL[status]}
          </span>
          {provider && <span className="pill provider">◇ {provider}</span>}
          <span className={`pill ${backendUp ? "ok" : "warn"}`}>
            {backendUp === null ? "…" : backendUp ? "BACKEND ●" : "BACKEND ○"}
          </span>
          <button className="lite-toggle" onClick={toggleLite}>
            {liteMode ? "LITE ⚡" : "3D ◈"}
          </button>
        </div>
      </header>

      <main className="stage">
        <section className="panel avatar-wrap">
          <Corners />
          <div className="panel-tag">// ALFRED CORE</div>
          <Avatar />
        </section>
        <section className="panel chat-panel">
          <Corners />
          <div className="panel-tag">// CHAT</div>
          <ChatPanel />
        </section>
      </main>

      <footer className="footer">
        <ToolDock />
      </footer>
    </div>
  );
}
