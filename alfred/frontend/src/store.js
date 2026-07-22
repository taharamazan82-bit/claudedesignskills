import { create } from "zustand";

// Alfred's UI state machine. `status` drives the avatar animation:
// idle -> listening -> thinking -> speaking -> idle  (error on failure).
export const useAlfred = create((set, get) => ({
  status: "idle", // idle | listening | thinking | speaking | error
  provider: null, // which LLM provider answered last (transparency)
  messages: [], // { role: "user"|"alfred", text }
  liteMode: detectLiteMode(),

  setStatus: (status) => set({ status }),
  setProvider: (provider) => set({ provider }),
  toggleLite: () => set((s) => ({ liteMode: !s.liteMode })),
  addMessage: (role, text) =>
    set((s) => ({ messages: [...s.messages, { role, text }] })),
}));

// Lite mode = weak hardware / reduced motion. Same machine that can't run big
// LLMs also renders this UI, so default to lite when signals point that way.
// Override with ?mode=3d or ?mode=lite in the URL.
function detectLiteMode() {
  if (typeof window === "undefined") return false;
  const forced = new URLSearchParams(window.location.search).get("mode");
  if (forced === "3d") return false;
  if (forced === "lite") return true;
  const reduced = window.matchMedia?.(
    "(prefers-reduced-motion: reduce)"
  )?.matches;
  const fewCores = (navigator.hardwareConcurrency || 8) <= 4;
  const lowMem = navigator.deviceMemory && navigator.deviceMemory <= 4;
  return Boolean(reduced || fewCores || lowMem);
}
