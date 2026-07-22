import React, { useRef, useMemo } from "react";
import * as THREE from "three";
import { Canvas, useFrame } from "@react-three/fiber";
import { useAlfred } from "./store.js";

// Purple/yellow futuristic palette. Each status re-tints the whole rig.
const STATE = {
  idle: { tint: "#ffffff", ring: "#facc15", ring2: "#a855f7", speed: 1.0, scale: 1.0 },
  listening: { tint: "#fde047", ring: "#fde047", ring2: "#c084fc", speed: 1.8, scale: 1.08 },
  thinking: { tint: "#c084fc", ring: "#fde047", ring2: "#c084fc", speed: 3.0, scale: 1.05 },
  speaking: { tint: "#fff2a8", ring: "#a855f7", ring2: "#fde047", speed: 2.4, scale: 1.1 },
  error: { tint: "#ef4444", ring: "#f59e0b", ring2: "#ef4444", speed: 0.6, scale: 0.94 },
};

// Build a glowing point-cloud sphere (Fibonacci distribution) with a
// purple->yellow gradient baked into vertex colors.
function useSpherePoints(count, radius, jitter) {
  return useMemo(() => {
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const purple = new THREE.Color("#7c3aed");
    const yellow = new THREE.Color("#facc15");
    const golden = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2;
      const r = Math.sqrt(Math.max(0, 1 - y * y));
      const theta = i * golden;
      const rad = radius + (Math.random() - 0.5) * jitter;
      pos[i * 3] = Math.cos(theta) * r * rad;
      pos[i * 3 + 1] = y * rad;
      pos[i * 3 + 2] = Math.sin(theta) * r * rad;
      const c = purple.clone().lerp(yellow, Math.pow((y + 1) / 2, 1.5) * (0.4 + Math.random() * 0.6));
      col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
    }
    return { pos, col };
  }, [count, radius, jitter]);
}

function PointLayer({ count, radius, jitter, size, dir = 1 }) {
  const ref = useRef();
  const { pos, col } = useSpherePoints(count, radius, jitter);
  const status = useAlfred((s) => s.status);
  const cfg = STATE[status] || STATE.idle;

  useFrame((state, dt) => {
    if (!ref.current) return;
    ref.current.rotation.y += dt * 0.12 * dir;
    ref.current.rotation.x += dt * 0.05 * dir;
    const t = state.clock.elapsedTime;
    const breathe = 1 + Math.sin(t * cfg.speed) * 0.04;
    const cur = ref.current.scale.x;
    const target = cfg.scale * breathe;
    ref.current.scale.setScalar(cur + (target - cur) * Math.min(1, dt * 5));
    ref.current.material.color.lerp(new THREE.Color(cfg.tint), Math.min(1, dt * 3));
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={pos.length / 3} array={pos} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={col.length / 3} array={col} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={size}
        vertexColors
        transparent
        opacity={0.95}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

function Ring({ radius, thickness, colorKey, spin }) {
  const ref = useRef();
  const status = useAlfred((s) => s.status);
  const cfg = STATE[status] || STATE.idle;
  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime;
    ref.current.rotation.z = t * spin;
    ref.current.rotation.x = Math.PI / 2.4;
    ref.current.material.color.set(cfg[colorKey]);
    ref.current.material.emissive.set(cfg[colorKey]);
  });
  return (
    <mesh ref={ref}>
      <torusGeometry args={[radius, thickness, 16, 140]} />
      <meshStandardMaterial emissiveIntensity={1.4} toneMapped={false} />
    </mesh>
  );
}

function Rig() {
  return (
    <group>
      {/* layered particle core */}
      <PointLayer count={2600} radius={1.0} jitter={0.06} size={0.03} dir={1} />
      <PointLayer count={1500} radius={1.28} jitter={0.25} size={0.022} dir={-1} />
      <PointLayer count={700} radius={1.7} jitter={0.5} size={0.018} dir={1} />
      {/* HUD rings */}
      <Ring radius={1.85} thickness={0.014} colorKey="ring" spin={0.6} />
      <Ring radius={2.15} thickness={0.008} colorKey="ring2" spin={-0.9} />
    </group>
  );
}

// CSS-only orb for lite mode (weak hardware) — dotted core + rings, no WebGL.
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
      camera={{ position: [0, 0, 5.2], fov: 45 }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
    >
      <ambientLight intensity={0.4} />
      <pointLight position={[4, 4, 5]} intensity={1.2} color="#fde047" />
      <pointLight position={[-4, -2, -2]} intensity={0.8} color="#a855f7" />
      <Rig />
    </Canvas>
  );
}
