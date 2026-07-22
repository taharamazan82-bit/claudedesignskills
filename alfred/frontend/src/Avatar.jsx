import React, { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { MeshDistortMaterial, Float } from "@react-three/drei";
import { useAlfred } from "./store.js";

// Per-status look: color + how agitated the blob is.
const STATE = {
  idle: { color: "#4b6bfb", distort: 0.28, speed: 1.2, scale: 1.0 },
  listening: { color: "#22d3ee", distort: 0.42, speed: 2.4, scale: 1.06 },
  thinking: { color: "#a855f7", distort: 0.6, speed: 4.0, scale: 1.03 },
  speaking: { color: "#34d399", distort: 0.5, speed: 3.0, scale: 1.08 },
  error: { color: "#ef4444", distort: 0.2, speed: 0.6, scale: 0.96 },
};

function Blob() {
  const mesh = useRef();
  const status = useAlfred((s) => s.status);
  const cfg = STATE[status] || STATE.idle;

  useFrame((_, dt) => {
    if (!mesh.current) return;
    mesh.current.rotation.y += dt * 0.25;
    // ease scale toward the target for the current state
    const target = cfg.scale;
    const cur = mesh.current.scale.x;
    const next = cur + (target - cur) * Math.min(1, dt * 4);
    mesh.current.scale.setScalar(next);
  });

  return (
    <Float speed={cfg.speed} rotationIntensity={0.4} floatIntensity={0.6}>
      <mesh ref={mesh}>
        <icosahedronGeometry args={[1.1, 12]} />
        <MeshDistortMaterial
          color={cfg.color}
          distort={cfg.distort}
          speed={cfg.speed}
          roughness={0.25}
          metalness={0.4}
        />
      </mesh>
    </Float>
  );
}

// CSS-only orb for lite mode (weak hardware / reduced motion) — no WebGL cost.
function LiteOrb() {
  const status = useAlfred((s) => s.status);
  return <div className={`lite-orb lite-${status}`} aria-hidden="true" />;
}

export default function Avatar() {
  const lite = useAlfred((s) => s.liteMode);
  if (lite) return <LiteOrb />;

  return (
    <Canvas
      dpr={[1, 1.5]} // capped DPR for weaker GPUs
      camera={{ position: [0, 0, 4], fov: 45 }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
    >
      <ambientLight intensity={0.6} />
      <pointLight position={[4, 4, 4]} intensity={1.2} />
      <pointLight position={[-4, -2, -2]} intensity={0.5} color="#6d28d9" />
      <Blob />
    </Canvas>
  );
}
