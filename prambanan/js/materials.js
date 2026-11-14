/**
 * Procedural Andesite, Weathered Stone, Moss, Carved Relief & Landscape Materials
 * Zero external texture dependencies — crisp CanvasTexture generation.
 */
import * as THREE from "three";

function makeStoneCanvasTexture({ baseRgb, variation = 26, joints = true, moss = 0.0, relief = false, size = 256 }) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = `rgb(${baseRgb[0]},${baseRgb[1]},${baseRgb[2]})`;
  ctx.fillRect(0, 0, size, size);

  // Volcanic andesite grain & weathering speckles
  let seed = baseRgb[0] * 13 + baseRgb[1] * 7 + (relief ? 99 : 0);
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };

  for (let i = 0; i < 4200; i++) {
    const x = rand() * size;
    const y = rand() * size;
    const r = 1 + rand() * 3.5;
    const d = Math.floor((rand() - 0.5) * variation * 2);
    const rr = Math.max(0, Math.min(255, baseRgb[0] + d));
    const gg = Math.max(0, Math.min(255, baseRgb[1] + d));
    const bb = Math.max(0, Math.min(255, baseRgb[2] + d));
    ctx.fillStyle = `rgba(${rr},${gg},${bb},0.45)`;
    ctx.fillRect(x, y, r, r);
  }

  // Subtle moss patches
  if (moss > 0) {
    const count = Math.floor(moss * 140);
    for (let i = 0; i < count; i++) {
      const x = rand() * size;
      const y = rand() * size;
      const rad = 4 + rand() * 14;
      ctx.fillStyle = `rgba(48, 76, 36, ${0.15 + rand() * 0.25})`;
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Ashlar stone block joints
  if (joints) {
    ctx.strokeStyle = "rgba(18, 17, 16, 0.36)";
    ctx.lineWidth = 2;
    const rows = 8;
    const rowH = size / rows;
    for (let r = 0; r < rows; r++) {
      const y = r * rowH;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(size, y);
      ctx.stroke();

      const cols = 4;
      const colW = size / cols;
      const offset = (r % 2) * (colW * 0.5);
      for (let c = 0; c <= cols; c++) {
        const x = (c * colW + offset) % size;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, y + rowH);
        ctx.stroke();
      }
    }
  }

  // Carved relief decorative framing & figures motif
  if (relief) {
    ctx.strokeStyle = "rgba(35, 32, 28, 0.55)";
    ctx.lineWidth = 3;
    ctx.strokeRect(8, 8, size - 16, size - 16);
    ctx.fillStyle = "rgba(92, 86, 78, 0.55)";
    for (let k = 0; k < 4; k++) {
      const cx = 42 + k * 56;
      ctx.beginPath();
      ctx.arc(cx, size * 0.38, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillRect(cx - 10, size * 0.48, 20, 44);
    }
    // Lotus border
    ctx.fillStyle = "rgba(70, 66, 60, 0.65)";
    for (let x = 16; x < size - 16; x += 24) {
      ctx.beginPath();
      ctx.arc(x + 8, size - 18, 7, Math.PI, 0);
      ctx.fill();
    }
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createMaterials() {
  const darkTex = makeStoneCanvasTexture({ baseRgb: [68, 66, 63], variation: 24, joints: true, moss: 0.18 });
  darkTex.repeat.set(3, 3);

  const weatheredTex = makeStoneCanvasTexture({ baseRgb: [54, 54, 50], variation: 30, joints: true, moss: 0.45 });
  weatheredTex.repeat.set(2, 2);

  const reconTex = makeStoneCanvasTexture({ baseRgb: [86, 83, 78], variation: 18, joints: true, moss: 0.04 });
  reconTex.repeat.set(2, 2);

  const reliefTex = makeStoneCanvasTexture({ baseRgb: [80, 76, 70], variation: 20, joints: false, moss: 0.08, relief: true });

  const sculpTex = makeStoneCanvasTexture({ baseRgb: [82, 79, 75], variation: 14, joints: false, moss: 0.03 });

  const pathTex = makeStoneCanvasTexture({ baseRgb: [94, 88, 78], variation: 22, joints: true, moss: 0.12 });
  pathTex.repeat.set(16, 16);

  const grassTex = makeStoneCanvasTexture({ baseRgb: [58, 92, 42], variation: 26, joints: false, moss: 0.3 });
  grassTex.repeat.set(45, 45);

  return {
    andesiteDark: new THREE.MeshStandardMaterial({ map: darkTex, roughness: 0.88, metalness: 0.04 }),
    andesiteWeathered: new THREE.MeshStandardMaterial({ map: weatheredTex, roughness: 0.94, metalness: 0.02 }),
    andesiteReconstructed: new THREE.MeshStandardMaterial({ map: reconTex, roughness: 0.82, metalness: 0.05 }),
    carvedRelief: new THREE.MeshStandardMaterial({ map: reliefTex, roughness: 0.78, metalness: 0.06 }),
    sculptureStone: new THREE.MeshStandardMaterial({ map: sculpTex, roughness: 0.72, metalness: 0.08 }),
    stonePath: new THREE.MeshStandardMaterial({ map: pathTex, roughness: 0.90, metalness: 0.02 }),
    grassJava: new THREE.MeshStandardMaterial({ map: grassTex, roughness: 0.96, metalness: 0.0 }),
    foliage: new THREE.MeshStandardMaterial({ color: 0x2e5a24, roughness: 0.88 }),
    trunk: new THREE.MeshStandardMaterial({ color: 0x4b3b2b, roughness: 0.94 }),
    hypotheticalGlow: new THREE.MeshStandardMaterial({
      color: 0x8b7d5b,
      roughness: 0.65,
      emissive: 0x2a2008,
      emissiveIntensity: 0.35,
      transparent: true,
      opacity: 0.86,
    }),
  };
}
