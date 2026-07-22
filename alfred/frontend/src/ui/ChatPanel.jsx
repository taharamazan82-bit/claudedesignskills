import React, { useState } from "react";
import { useAlfred } from "../store.js";
import { sendChat } from "../api.js";

export default function ChatPanel() {
  const { messages, addMessage, setStatus, setProvider } = useAlfred();
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    const prompt = text.trim();
    if (!prompt || busy) return;
    setText("");
    setBusy(true);
    addMessage("user", prompt);
    setStatus("thinking");

    const res = await sendChat(prompt, "Sen Alfred'sin, yardımcı bir sanal asistan.");

    if (res.ok) {
      setProvider(res.provider || null);
      setStatus("speaking");
      addMessage("alfred", res.text);
      setTimeout(() => setStatus("idle"), 900);
    } else {
      setStatus("error");
      addMessage(
        "alfred",
        `Bir sorun oldu (${res.error}). ${res.detail || ""} — .env içindeki Groq anahtarını ve backend'in çalıştığını kontrol et.`
      );
      setTimeout(() => setStatus("idle"), 1600);
    }
    setBusy(false);
  }

  return (
    <div className="chat">
      <div className="chat-log">
        {messages.length === 0 && (
          <p className="hint">Alfred'e bir şey yaz… (örn. "Bugün ne yapabilirsin?")</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg msg-${m.role}`}>
            <span className="who">{m.role === "user" ? "Sen" : "Alfred"}</span>
            <span className="text">{m.text}</span>
          </div>
        ))}
      </div>
      <form className="chat-input" onSubmit={submit}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Mesaj yaz…"
          aria-label="Alfred'e mesaj"
        />
        <button type="submit" disabled={busy}>
          {busy ? "…" : "Gönder"}
        </button>
      </form>
    </div>
  );
}
