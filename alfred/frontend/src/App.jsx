import React, { useEffect, useState } from "react";
import Avatar from "./Avatar.jsx";
import ChatPanel from "./ui/ChatPanel.jsx";
import ToolDock from "./ui/ToolDock.jsx";
import { useAlfred } from "./store.js";
import { health } from "./api.js";

const STATUS_LABEL = {
  idle: "hazır",
  listening: "dinliyor",
  thinking: "düşünüyor",
  speaking: "konuşuyor",
  error: "hata",
};

export default function App() {
  const { status, provider, liteMode, toggleLite } = useAlfred();
  const [backendUp, setBackendUp] = useState(null);

  useEffect(() => {
    health().then(setBackendUp);
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo-dot" /> Alfred
        </div>
        <div className="status-cluster">
          <span className={`pill status-${status}`}>{STATUS_LABEL[status]}</span>
          {provider && <span className="pill provider">{provider}</span>}
          <span className={`pill ${backendUp ? "ok" : "warn"}`}>
            {backendUp === null ? "…" : backendUp ? "backend ✓" : "backend yok"}
          </span>
          <button className="lite-toggle" onClick={toggleLite}>
            {liteMode ? "Lite ⚡" : "3D"}
          </button>
        </div>
      </header>

      <main className="stage">
        <div className="avatar-wrap">
          <Avatar />
        </div>
        <ChatPanel />
      </main>

      <footer className="footer">
        <ToolDock />
      </footer>
    </div>
  );
}
