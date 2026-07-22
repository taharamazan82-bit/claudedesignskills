// Thin client to the Alfred backend. The browser never sees API keys — the
// backend holds them and calls the Python tools.

export async function sendChat(prompt, system) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, system }),
  });
  if (!res.ok) {
    return { ok: false, error: "backend_unreachable", detail: `HTTP ${res.status}` };
  }
  return res.json();
}

export async function health() {
  try {
    const res = await fetch("/api/health");
    return res.ok;
  } catch {
    return false;
  }
}
