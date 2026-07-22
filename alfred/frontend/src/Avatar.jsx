import React, { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { MeshDistortMaterial, Float } from "@react-three/drei";
import { useAlfred } from "./store.js";

// Purple/yellow futuristic palette. Each status re-tints the whole rig.
const STATE = {
  idle: { core: "#a855f7", ring: "#facc15", distort: 0.3, speed: 1.4, scale: 1.0 },
  listening: { core: "#facc15", ring: "#c084fc", distort: 0.45, speed: 2.6, scale: 1.07 },
  thinking: { core: "#c084fc", ring: "#fde047", distort: 0.62, speed: 4.2, scale: 1.04 },
  speaking: { core: "#fde047", ring: "#a855f7", distort: 0.5, speed: 3.2, scale: 1.09 },
  error: { core: "#ef4444", ring: "#f59e0b", distort: 0.22, speed: 0.7, scale: 0.95 },
};

function Rig() {
  const blob = useRef();
  const ringA = useRef();
  const ringB = useRef();
  const status = useAlfred((s) => s.status);
  const cfg = STATE[status] || STATE.idle;

  useFrame((state, dt) => {
    const t = state.clock.elapsedTime;
    if (blob.current) {
      blob.current.rotation.y += dt * 0.3;
      const cur = blob.current.scale.x;
      const next = cur + (cfg.scale - cur) * Math.min(1, dt * 4);
      blob.current.scale.setScalar(next);
    }
    if (ringA.current) {
      ringA.current.rotation.z = t * 0.6;
      ringA.current.rotation.x = Math.PI / 2.4;
    }
    if (ringB.current) {
      ringB.current.rotation.z = -t * 0.9;
      ringB.current.rotation.x = Math.PI / 3;
      ringB.current.rotation.y = t * 0.3;
    }
  });

  return (
    <group>
      <Float speed={cfg.speed} rotationIntensity={0.35} floatIntensity={0.5}>
        <mesh ref={blob}>
          <icosahedronGeometry args={[1.05, 16]} />
          <MeshDistortMaterial
            color={cfg.core}
            emissive={cfg.core}
            emissiveIntensity={0.35}
            distort={cfg.distort}
            speed={cfg.speed}
            roughness={0.2}
            metalness={0.6}
          />
        </mesh>
      </Float>
      {/* HUD rings */}
      <mesh ref={ringA}>
        <torusGeometry args={[1.7, 0.015, 16, 120]} />
        <meshStandardMaterial color={cfg.ring} emissive={cfg.ring} emissiveIntensity={1.4} />
      </mesh>
      <mesh ref={ringB}>
        <torusGeometry args={[2.05, 0.008, 16, 120]} />
        <meshStandardMaterial color={cfg.core} emissive={cfg.core} emissiveIntensity={1.1} />
      </mesh>
    </group>
  );
}

// CSS-only orb for lite mode (weak hardware) — rings drawn in CSS, no WebGL cost.
function LiteOrb() {
  const status = useAlfred((s) => s.status);
  return (
    <div className={`lite-rig lite-${status}`} aria-hidden="true">
      <span className="lite-ring lite-ring-a" />
      <span className="lite-ring lite-ring-b" />
      <span className="lite-core" />
    </div>
  );
}

export default function Avatar() {
  const lite = useAlfred((s) => s.liteMode);
  if (lite) return <LiteOrb />;

  return (
    <Canvas
      dpr={[1, 1.5]}
      camera={{ position: [0, 0, 5], fov: 45 }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
    >
      <ambientLight intensity={0.5} />
      <pointLight position={[4, 4, 5]} intensity={1.4} color="#fde047" />
      <pointLight position={[-4, -2, -2]} intensity={0.9} color="#a855f7" />
      <Rig />
    </Canvas>
  );
}
