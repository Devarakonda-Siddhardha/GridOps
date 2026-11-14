/**
 * Candi Prambanan Complete 3D Architectural Builder (Three.js)
 * Builds:
 * - 3 Trimurti Temples (Shiva 47m 4-chamber, Vishnu 33m, Brahma 33m)
 * - 3 Vahana Temples (Nandi 25m, Garuda 22.5m, Hamsa 22.5m)
 * - 2 Apit, 4 Kelir, 4 Patok, 4 Paduraksa Gates, Mahakala & Nandisvara shrines
 * - 224 Perwara shrines (4 concentric rows: 44, 52, 60, 68) with Mode A/B toggle
 * - 54 Ramayana + 30 Krishnayana relief panels
 * - Outer park, tropical vegetation, and distant Mount Merapi
 */
import * as THREE from "three";
import {
  buildShivaMahadeva,
  buildDurgaMahishasuramardini,
  buildGanesha,
  buildAgastya,
  buildVishnu,
  buildBrahma,
  buildNandi,
} from "./sculptures.js";
import {
  RAMAYANA_SHIVA_PANELS,
  RAMAYANA_BRAHMA_SUMMARY,
  KRISHNAYANA_VISHNU_SUMMARY,
} from "../data/prambanan_lore.js";
import { buildInscriptions } from "./inscriptions.js";
import { buildArchitecturalSculptures } from "./architectural_sculptures.js";

function addBox(parent, w, h, d, x, y, z, mat, colliders = null, cast = true) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  m.castShadow = cast;
  m.receiveShadow = true;
  parent.add(m);
  if (colliders) {
    const wp = new THREE.Vector3();
    m.getWorldPosition(wp);
    colliders.push({
      minX: wp.x - w * 0.5,
      maxX: wp.x + w * 0.5,
      minY: wp.y - h * 0.5,
      maxY: wp.y + h * 0.5,
      minZ: wp.z - d * 0.5,
      maxZ: wp.z + d * 0.5,
    });
  }
  return m;
}

function addRatna(parent, r, h, x, y, z, mat) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  const base = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.45, r, h * 0.45, 8), mat);
  base.position.y = h * 0.225;
  base.castShadow = true;
  const tip = new THREE.Mesh(new THREE.ConeGeometry(r * 0.55, h * 0.55, 8), mat);
  tip.position.y = h * 0.725;
  tip.castShadow = true;
  g.add(base, tip);
  parent.add(g);
}

function addKalaMakaraPortal(parent, x, y, z, rotY, doorW, doorH, mat) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.rotation.y = rotY;
  const pw = doorW * 0.22;
  addBox(g, 0.55, doorH, pw, 0, doorH * 0.5, -doorW * 0.5 - pw * 0.35, mat);
  addBox(g, 0.55, doorH, pw, 0, doorH * 0.5, doorW * 0.5 + pw * 0.35, mat);
  addBox(g, 0.70, doorH * 0.22, doorW * 1.45, 0, doorH + doorH * 0.11, 0, mat);
  // Kala face pediment
  addBox(g, 0.78, doorH * 0.28, doorW * 0.75, 0, doorH + doorH * 0.34, 0, mat);
  parent.add(g);
}

function addStaircase(parent, worldCenterX, worldCenterZ, startY, endY, runLen, width, dirX, dirZ, mat, stairRamps, colliders) {
  const rise = endY - startY;
  const steps = Math.max(4, Math.round(rise / 0.24));
  const stepH = rise / steps;
  const stepD = runLen / steps;
  const perpX = -dirZ;
  const perpZ = dirX;

  for (let i = 0; i < steps; i++) {
    const frac = (i + 0.5) / steps;
    const cx = worldCenterX + dirX * (frac * runLen);
    const cz = worldCenterZ + dirZ * (frac * runLen);
    const cy = startY + (i + 0.5) * stepH;
    const sx = Math.abs(dirX) * stepD + Math.abs(perpX) * width;
    const sz = Math.abs(dirZ) * stepD + Math.abs(perpZ) * width;
    addBox(parent, sx, stepH, sz, cx, cy, cz, mat, null);
  }

  // Side balustrades (collidable)
  for (const s of [-1, 1]) {
    const bx = worldCenterX + dirX * (runLen * 0.5) + perpX * s * (width * 0.5 + 0.25);
    const bz = worldCenterZ + dirZ * (runLen * 0.5) + perpZ * s * (width * 0.5 + 0.25);
    const bsx = Math.abs(dirX) * runLen + Math.abs(perpX) * 0.45;
    const bsz = Math.abs(dirZ) * runLen + Math.abs(perpZ) * 0.45;
    addBox(parent, bsx, rise + 0.75, bsz, bx, startY + (rise + 0.75) * 0.5, bz, mat, colliders);
  }

  // Register smooth walkable stair ramp
  stairRamps.push({
    x0: worldCenterX,
    z0: worldCenterZ,
    dirX,
    dirZ,
    runLen,
    halfW: width * 0.52,
    startY,
    endY,
  });
}

function buildPrasada({
  scene,
  name,
  cx,
  cz,
  baseY,
  baseSize,
  totalHeight,
  mats,
  colliders,
  walkableSurfaces,
  stairRamps,
  interactables,
  fourChambers = false,
  facingEast = true,
  templeLoreId = null,
}) {
  const root = new THREE.Group();
  root.name = name;
  scene.add(root);

  const stone = mats.andesiteDark;
  const carved = mats.carvedRelief;
  const plinthH = totalHeight * 0.16; // ~7.5m on Shiva, ~5.3m on Vishnu/Brahma
  const bodyH = totalHeight * 0.30;
  const roofH = totalHeight * 0.54;

  // Stepped Plinth & Gallery Platform
  addBox(root, baseSize, plinthH * 0.55, baseSize, cx, baseY + plinthH * 0.275, cz, stone);
  const galSize = baseSize * 0.88;
  addBox(root, galSize, plinthH * 0.45, galSize, cx, baseY + plinthH * 0.775, cz, stone);

  const galY = baseY + plinthH;
  walkableSurfaces.push({
    minX: cx - galSize * 0.5,
    maxX: cx + galSize * 0.5,
    minZ: cz - galSize * 0.5,
    maxZ: cz + galSize * 0.5,
    y: galY,
  });

  // Gallery Balustrade Perimeter (with cardinal openings)
  const galHalf = galSize * 0.47;
  const balH = 1.45;
  const balT = 0.50;
  const gateGap = 3.4;
  const segLen = galHalf - gateGap * 0.5;
  for (const sx of [-1, 1]) {
    for (const sz of [-1, 1]) {
      addBox(root, segLen, balH, balT, cx + sx * (gateGap * 0.5 + segLen * 0.5), galY + balH * 0.5, cz + sz * galHalf, carved, colliders);
      addBox(root, balT, balH, segLen, cx + sx * galHalf, galY + balH * 0.5, cz + sz * (gateGap * 0.5 + segLen * 0.5), carved, colliders);
    }
  }

  // Temple Body (Hollow Navigable Sanctum Walls)
  const bodyW = baseSize * 0.56;
  const wallT = Math.max(0.85, bodyW * 0.12);
  const doorW = baseSize >= 20 ? 2.6 : 2.0;
  const doorH = baseSize >= 20 ? 4.2 : 3.2;

  if (fourChambers) {
    // Central core pier separating the 4 cardinal chambers
    const coreW = bodyW * 0.28;
    addBox(root, coreW, bodyH, coreW, cx, galY + bodyH * 0.5, cz, stone, colliders);

    const sideSeg = (bodyW - doorW) * 0.5;
    const dirs = [
      { dx: 1, dz: 0, rot: 0 },
      { dx: -1, dz: 0, rot: Math.PI },
      { dx: 0, dz: -1, rot: Math.PI * 0.5 },
      { dx: 0, dz: 1, rot: -Math.PI * 0.5 },
    ];
    for (const { dx, dz, rot } of dirs) {
      if (dx !== 0) {
        const wx = cx + dx * (bodyW * 0.5 - wallT * 0.5);
        addBox(root, wallT, bodyH, sideSeg, wx, galY + bodyH * 0.5, cz - (doorW * 0.5 + sideSeg * 0.5), stone, colliders);
        addBox(root, wallT, bodyH, sideSeg, wx, galY + bodyH * 0.5, cz + (doorW * 0.5 + sideSeg * 0.5), stone, colliders);
        addBox(root, wallT, bodyH - doorH, doorW, wx, galY + doorH + (bodyH - doorH) * 0.5, cz, stone);
        addKalaMakaraPortal(root, cx + dx * (bodyW * 0.5 + 0.3), galY, cz, rot, doorW, doorH, carved);
        addStaircase(root, cx + dx * (baseSize * 0.54), cz, baseY, galY, baseSize * 0.16, doorW + 0.8, -dx, 0, stone, stairRamps, colliders);
      } else {
        const wz = cz + dz * (bodyW * 0.5 - wallT * 0.5);
        addBox(root, sideSeg, bodyH, wallT, cx - (doorW * 0.5 + sideSeg * 0.5), galY + bodyH * 0.5, wz, stone, colliders);
        addBox(root, sideSeg, bodyH, wallT, cx + (doorW * 0.5 + sideSeg * 0.5), galY + bodyH * 0.5, wz, stone, colliders);
        addBox(root, doorW, bodyH - doorH, wallT, cx, galY + doorH + (bodyH - doorH) * 0.5, wz, stone);
        addKalaMakaraPortal(root, cx, galY, cz + dz * (bodyW * 0.5 + 0.3), rot, doorW, doorH, carved);
        addStaircase(root, cx, cz + dz * (baseSize * 0.54), baseY, galY, baseSize * 0.16, doorW + 0.8, 0, -dz, stone, stairRamps, colliders);
      }
    }
  } else {
    // Single-chamber temple
    const fx = facingEast ? 1 : -1;
    // Back wall
    addBox(root, wallT, bodyH, bodyW, cx - fx * (bodyW * 0.5 - wallT * 0.5), galY + bodyH * 0.5, cz, stone, colliders);
    // Side walls
    for (const s of [-1, 1]) {
      addBox(root, bodyW, bodyH, wallT, cx, galY + bodyH * 0.5, cz + s * (bodyW * 0.5 - wallT * 0.5), stone, colliders);
    }
    // Front wall with doorway
    const sideSeg = (bodyW - doorW) * 0.5;
    const fwx = cx + fx * (bodyW * 0.5 - wallT * 0.5);
    addBox(root, wallT, bodyH, sideSeg, fwx, galY + bodyH * 0.5, cz - (doorW * 0.5 + sideSeg * 0.5), stone, colliders);
    addBox(root, wallT, bodyH, sideSeg, fwx, galY + bodyH * 0.5, cz + (doorW * 0.5 + sideSeg * 0.5), stone, colliders);
    addBox(root, wallT, bodyH - doorH, doorW, fwx, galY + doorH + (bodyH - doorH) * 0.5, cz, stone);
    addKalaMakaraPortal(root, cx + fx * (bodyW * 0.5 + 0.25), galY, cz, fx > 0 ? 0 : Math.PI, doorW, doorH, carved);
    addStaircase(root, cx + fx * (baseSize * 0.54), cz, baseY, galY, baseSize * 0.18, doorW + 0.6, -fx, 0, stone, stairRamps, colliders);
  }

  // Sanctum ceiling slab
  addBox(root, bodyW, 0.8, bodyW, cx, galY + bodyH + 0.4, cz, stone);

  // Multi-tiered Javanese Bhumi Superstructure with Ratna Finials
  const tiers = totalHeight >= 30 ? 5 : 4;
  const tierH = (roofH * 0.82) / tiers;
  const roofY0 = galY + bodyH + 0.8;
  for (let t = 0; t < tiers; t++) {
    const scale = 1.0 - t * 0.16;
    const tw = bodyW * scale;
    const ty = roofY0 + (t + 0.5) * tierH;
    addBox(root, tw, tierH * 0.92, tw, cx, ty, cz, stone, null);
    const finR = Math.max(0.22, tw * 0.065);
    const finH = tierH * 0.55;
    for (const rx of [-1, 1]) {
      for (const rz of [-1, 1]) {
        addRatna(root, finR, finH, cx + rx * tw * 0.43, ty + tierH * 0.42, cz + rz * tw * 0.43, carved);
      }
    }
  }
  addRatna(root, bodyW * 0.16, roofH * 0.24, cx, roofY0 + tiers * tierH, cz, carved);

  // Optional temple exterior info plaque near front stair
  if (templeLoreId) {
    const fx = facingEast ? 1 : -1;
    const plaque = addBox(root, 0.4, 1.3, 0.7, cx + fx * (baseSize * 0.58), baseY + 0.65, cz + 2.6, carved, colliders);
    plaque.userData.interactable = { type: "deity", id: templeLoreId, label: `Read ${name} Guide` };
    interactables.push(plaque);
  }

  return { root, galY };
}

function buildReliefGalleryPanels(scene, cx, cz, galY, radius, count, cycleType, mat, interactables) {
  const g = new THREE.Group();
  scene.add(g);
  const perSide = Math.ceil(count / 4);

  for (let i = 0; i < count; i++) {
    const side = Math.floor(i / perSide);
    const idxOnSide = i % perSide;
    const t = perSide > 1 ? idxOnSide / (perSide - 1) - 0.5 : 0;
    const span = radius * 1.38;
    let px = cx, pz = cz, rotY = 0;
    // Clockwise pradaksina starting from East
    if (side === 0) { px = cx + radius; pz = cz + t * span; rotY = Math.PI * 0.5; }
    else if (side === 1) { px = cx - t * span; pz = cz + radius; rotY = 0; }
    else if (side === 2) { px = cx - radius; pz = cz - t * span; rotY = Math.PI * 0.5; }
    else { px = cx + t * span; pz = cz - radius; rotY = 0; }

    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.92, 0.14), mat);
    panel.position.set(px, galY + 0.88, pz);
    panel.rotation.y = rotY;
    panel.receiveShadow = true;

    let meta;
    if (cycleType === "SHIVA_RAMAYANA") {
      const p = RAMAYANA_SHIVA_PANELS[i] || RAMAYANA_SHIVA_PANELS[0];
      meta = {
        type: "relief",
        id: p.id,
        label: `Ramayana Panel ${p.panel}: ${p.title}`,
        panelData: {
          name: `Ramayana Panel ${p.panel}: ${p.title}`,
          sanskrit: p.sanskrit,
          category: "Candi Shiva — Ramayana Relief Cycle (1–24)",
          evidenceStatus: "VERIFIED 9TH-CENTURY CARVED RELIEF",
          background: p.text,
          iconography: p.sig,
          archaeology: "Carved on the inner balustrade of Candi Shiva's pradakṣiṇapatha gallery, read clockwise from the East stair.",
          sources: p.src,
        },
      };
    } else if (cycleType === "BRAHMA_RAMAYANA") {
      const ep = RAMAYANA_BRAHMA_SUMMARY[Math.floor((i / count) * RAMAYANA_BRAHMA_SUMMARY.length)];
      meta = {
        type: "relief",
        id: `BRAHMA_RAM_${i + 1}`,
        label: `Ramayana (Brahma) Panel ${i + 1}: ${ep}`,
        panelData: {
          name: `Ramayana Continuation — Panel ${i + 1} (Epic ${25 + i})`,
          sanskrit: "Yuddha & Uttara Kāṇḍa",
          category: "Candi Brahma — Ramayana Relief Cycle (25–54)",
          evidenceStatus: "VERIFIED 9TH-CENTURY CARVED RELIEF",
          background: `Episode: ${ep}. Continues the epic narrative directly from Candi Shiva Panel 24.`,
          iconography: "Central Javanese narrative bas-relief with register dividers and courtly/battle iconography.",
          archaeology: "Carved on the inner balustrade of Candi Brahma.",
          sources: "Stutterheim (1925); Kemendikbudristek.",
        },
      };
    } else {
      const ep = KRISHNAYANA_VISHNU_SUMMARY[Math.floor((i / count) * KRISHNAYANA_VISHNU_SUMMARY.length)];
      meta = {
        type: "relief",
        id: `VISHNU_KRISH_${i + 1}`,
        label: `Krishnayana Panel ${i + 1}: ${ep}`,
        panelData: {
          name: `Krishnayana (Kṛṣṇāyana) — Panel ${i + 1}`,
          sanskrit: "Kṛṣṇa & Balarāma Carita",
          category: "Candi Vishnu — Krishnayana Relief Cycle (1–30)",
          evidenceStatus: "VERIFIED 9TH-CENTURY CARVED RELIEF",
          background: `Episode: ${ep}. Celebrates Vishnu's incarnation as Krishna alongside his brother Balarama.`,
          iconography: "Dynamic pastoral and heroic scenes on Candi Vishnu's balustrade.",
          archaeology: "Carved on the inner balustrade of Candi Vishnu.",
          sources: "UNESCO WHC #642; Kemendikbudristek.",
        },
      };
    }

    panel.userData.interactable = meta;
    interactables.push(panel);
    g.add(panel);
  }
}

export function buildPrambananComplex(scene, mats) {
  const colliders = [];
  const walkableSurfaces = [];
  const stairRamps = [];
  const interactables = [];

  // 1. Outer Ground (Bhurloka, 520x520 m)
  const ground = new THREE.Mesh(new THREE.BoxGeometry(520, 0.4, 520), mats.grassJava);
  ground.position.set(0, -0.2, 0);
  ground.receiveShadow = true;
  scene.add(ground);
  walkableSurfaces.push({ minX: -260, maxX: 260, minZ: -260, maxZ: 260, y: 0 });

  // Stone approach avenue from East & South
  addBox(scene, 95, 0.06, 10, 145, 0.03, 0, mats.stonePath, null, false);
  addBox(scene, 10, 0.06, 95, 0, 0.03, 145, mats.stonePath, null, false);

  // 2. Four Concentric Perwara Terraces + Inner Svarloka Courtyard (110x110 m at +3.5 m)
  const terraces = [
    { size: 236, y: 0.5 },
    { size: 208, y: 1.0 },
    { size: 180, y: 1.5 },
    { size: 152, y: 2.0 },
    { size: 110, y: 3.5 },
  ];
  for (const t of terraces) {
    addBox(scene, t.size, t.y, t.size, 0, t.y * 0.5, 0, mats.stonePath, null, false);
    walkableSurfaces.push({
      minX: -t.size * 0.5,
      maxX: t.size * 0.5,
      minZ: -t.size * 0.5,
      maxZ: t.size * 0.5,
      y: t.y,
    });
  }

  // Cardinal Terrace Approach Stairways (0.0m -> 3.5m)
  for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    addStaircase(scene, dx * 124, dz * 124, 0.0, 3.5, 70.0, 7.0, -dx, -dz, mats.andesiteDark, stairRamps, colliders);
  }

  // Inner Courtyard Enclosure Wall with 4 Paduraksa Gate Openings
  const half = 55;
  for (const axis of ["E", "W", "N", "S"]) {
    for (const s of [-1, 1]) {
      if (axis === "E" || axis === "W") {
        const x = axis === "E" ? half : -half;
        addBox(scene, 1.2, 2.8, 48, x, 3.5 + 1.4, s * 31, mats.andesiteDark, colliders);
      } else {
        const z = axis === "S" ? half : -half;
        addBox(scene, 48, 2.8, 1.2, s * 31, 3.5 + 1.4, z, mats.andesiteDark, colliders);
      }
    }
    // Paduraksa Gate Towers
    const gx = axis === "E" ? half : axis === "W" ? -half : 0;
    const gz = axis === "S" ? half : axis === "N" ? -half : 0;
    const rot = axis === "E" || axis === "W" ? 0 : Math.PI * 0.5;
    addKalaMakaraPortal(scene, gx, 3.5, gz, rot, 4.4, 5.2, mats.carvedRelief);
  }

  // 3. TRIMURTI TEMPLES (Western Row, Facing East)
  const shiva = buildPrasada({
    scene, name: "Candi Shiva Mahadeva", cx: -18, cz: 0, baseY: 3.5,
    baseSize: 34, totalHeight: 47, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: true, facingEast: true, templeLoreId: "SHIVA_TEMPLE",
  });
  const vishnu = buildPrasada({
    scene, name: "Candi Vishnu", cx: -18, cz: -32, baseY: 3.5,
    baseSize: 20, totalHeight: 33, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: true, templeLoreId: "VISHNU_TEMPLE",
  });
  const brahma = buildPrasada({
    scene, name: "Candi Brahma", cx: -18, cz: 32, baseY: 3.5,
    baseSize: 20, totalHeight: 33, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: true, templeLoreId: "BRAHMA_TEMPLE",
  });

  // 4. VAHANA TEMPLES (Eastern Row, Facing West)
  const nandi = buildPrasada({
    scene, name: "Candi Nandi", cx: 20, cz: 0, baseY: 3.5,
    baseSize: 15, totalHeight: 25, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: false, templeLoreId: "NANDI_TEMPLE",
  });
  const garuda = buildPrasada({
    scene, name: "Candi Garuda", cx: 20, cz: -32, baseY: 3.5,
    baseSize: 14, totalHeight: 22.5, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: false, templeLoreId: "GARUDA_TEMPLE",
  });
  const hamsa = buildPrasada({
    scene, name: "Candi Hamsa", cx: 20, cz: 32, baseY: 3.5,
    baseSize: 14, totalHeight: 22.5, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: false, templeLoreId: "HAMSA_TEMPLE",
  });

  // 5. APIT (2), KELIR (4), PATOK (4), MAHAKALA & NANDISVARA (2)
  buildPrasada({
    scene, name: "Candi Apit North", cx: 1, cz: -43, baseY: 3.5,
    baseSize: 6.5, totalHeight: 14, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: true, templeLoreId: "APIT_TEMPLES",
  });
  buildPrasada({
    scene, name: "Candi Apit South", cx: 1, cz: 43, baseY: 3.5,
    baseSize: 6.5, totalHeight: 14, mats, colliders, walkableSurfaces, stairRamps, interactables,
    fourChambers: false, facingEast: false, templeLoreId: "APIT_TEMPLES",
  });

  for (const [kx, kz] of [[50, 0], [-50, 0], [0, -50], [0, 50]]) {
    addBox(scene, 1.8, 3.8, 1.8, kx, 3.5 + 1.9, kz, mats.carvedRelief, colliders);
    addRatna(scene, 0.55, 1.1, kx, 3.5 + 3.8, kz, mats.carvedRelief);
  }
  for (const [px, pz] of [[50, 50], [-50, 50], [50, -50], [-50, -50]]) {
    addBox(scene, 1.8, 3.6, 1.8, px, 3.5 + 1.8, pz, mats.carvedRelief, colliders);
    addRatna(scene, 0.5, 1.0, px, 3.5 + 3.6, pz, mats.carvedRelief);
  }
  // Mahakala & Nandisvara flanking Candi Shiva's eastern entrance
  for (const sz of [-4.2, 4.2]) {
    addBox(scene, 1.4, 3.4, 1.4, -0.5, 3.5 + 1.7, sz, mats.carvedRelief, colliders);
    addRatna(scene, 0.45, 0.9, -0.5, 3.5 + 3.4, sz, mats.carvedRelief);
  }

  // 3D Engraved Epigraphy Steles (Shivagrha 856 CE Provenance Exhibit + Perwara Short Mark)
  buildInscriptions(scene, mats, interactables, colliders);

  // 6. SACRED SCULPTURES INSIDE CHAMBERS
  scene.add(buildShivaMahadeva([-14.0, shiva.galY, 0], Math.PI * 0.5, mats.sculptureStone, interactables, colliders));
  scene.add(buildDurgaMahishasuramardini([-18.0, shiva.galY, -4.0], Math.PI, mats.sculptureStone, interactables, colliders));
  scene.add(buildGanesha([-22.0, shiva.galY, 0], -Math.PI * 0.5, mats.sculptureStone, interactables, colliders));
  scene.add(buildAgastya([-18.0, shiva.galY, 4.0], 0, mats.sculptureStone, interactables, colliders));
  scene.add(buildVishnu([-18.0, vishnu.galY, -32.0], Math.PI * 0.5, mats.sculptureStone, interactables, colliders));
  scene.add(buildBrahma([-18.0, brahma.galY, 32.0], Math.PI * 0.5, mats.sculptureStone, interactables, colliders));
  scene.add(buildNandi([20.0, nandi.galY, 0], Math.PI, mats.sculptureStone, interactables, colliders));

  // Mode B (Historical Reconstruction) Hypothetical Pedestals inside Garuda & Hamsa
  const hypotheticalGroup = new THREE.Group();
  hypotheticalGroup.visible = false;
  scene.add(hypotheticalGroup);
  const gPed = addBox(hypotheticalGroup, 1.6, 1.2, 1.6, 20, garuda.galY + 0.6, -32, mats.hypotheticalGlow);
  gPed.userData.interactable = { type: "deity", id: "GARUDA_TEMPLE", label: "[RECONSTRUCTED] Garuda Pedestal" };
  const hPed = addBox(hypotheticalGroup, 1.6, 1.2, 1.6, 20, hamsa.galY + 0.6, 32, mats.hypotheticalGlow);
  hPed.userData.interactable = { type: "deity", id: "HAMSA_TEMPLE", label: "[RECONSTRUCTED] Hamsa Pedestal" };
  interactables.push(gPed, hPed);

  // 7. RAMAYANA & KRISHNAYANA RELIEF GALLERIES
  buildReliefGalleryPanels(scene, -18, 0, shiva.galY, 13.8, 24, "SHIVA_RAMAYANA", mats.carvedRelief, interactables);
  buildReliefGalleryPanels(scene, -18, 32, brahma.galY, 8.1, 30, "BRAHMA_RAMAYANA", mats.carvedRelief, interactables);
  buildReliefGalleryPanels(scene, -18, -32, vishnu.galY, 8.1, 30, "VISHNU_KRISHNAYANA", mats.carvedRelief, interactables);

  // 8. 224 PERWARA SHRINES (InstancedMesh for Mode A Present-Day vs Mode B Historical)
  const perwaraRows = [
    { half: 111, perSide: 18, y: 0.5 }, // 68
    { half: 97, perSide: 16, y: 1.0 },  // 60
    { half: 83, perSide: 14, y: 1.5 },  // 52
    { half: 69, perSide: 12, y: 2.0 },  // 44
  ];
  const perwaraCoords = [];
  for (const row of perwaraRows) {
    const seen = new Set();
    const step = (2 * row.half) / (row.perSide - 1);
    for (let i = 0; i < row.perSide; i++) {
      const p = Number((-row.half + i * step).toFixed(2));
      for (const [x, z] of [[p, row.half], [p, -row.half], [row.half, p], [-row.half, p]]) {
        const key = `${x},${z}`;
        if (!seen.has(key)) {
          seen.add(key);
          perwaraCoords.push({ x, y: row.y, z });
        }
      }
    }
  }

  // Build Mode A (Ruined/Partial/6 Intact) & Mode B (All 224 Intact) InstancedMeshes
  const perwaraPresentGroup = new THREE.Group();
  const perwaraHistGroup = new THREE.Group();
  perwaraHistGroup.visible = false;
  scene.add(perwaraPresentGroup, perwaraHistGroup);

  const intactBaseGeo = new THREE.BoxGeometry(5.6, 5.5, 5.6);
  const intactSpireGeo = new THREE.ConeGeometry(2.4, 7.5, 4);
  intactSpireGeo.rotateY(Math.PI * 0.25);
  const ruinedGeo = new THREE.BoxGeometry(5.4, 1.5, 5.4);
  const fallenGeo = new THREE.BoxGeometry(2.2, 0.9, 1.8);

  const histBases = new THREE.InstancedMesh(intactBaseGeo, mats.andesiteReconstructed, perwaraCoords.length);
  const histSpires = new THREE.InstancedMesh(intactSpireGeo, mats.andesiteReconstructed, perwaraCoords.length);
  histBases.castShadow = true;
  histSpires.castShadow = true;
  const dummy = new THREE.Object3D();

  const intactIndices = new Set([0, 14, 68, 120, 175, 210]);
  const presentIntact = [];
  const presentRuined = [];
  const presentFallen = [];

  perwaraCoords.forEach((c, idx) => {
    // Historical Mode B: all 224 complete
    dummy.position.set(c.x, c.y + 2.75, c.z);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();
    histBases.setMatrixAt(idx, dummy.matrix);
    dummy.position.set(c.x, c.y + 9.2, c.z);
    dummy.updateMatrix();
    histSpires.setMatrixAt(idx, dummy.matrix);

    // Present Mode A: 6 restored, ~35% ruined bases, ~62% fallen stones
    if (intactIndices.has(idx)) presentIntact.push(c);
    else if (idx % 3 === 0) presentRuined.push(c);
    else presentFallen.push(c);
  });
  perwaraHistGroup.add(histBases, histSpires);

  const pIntactB = new THREE.InstancedMesh(intactBaseGeo, mats.andesiteReconstructed, presentIntact.length);
  const pIntactS = new THREE.InstancedMesh(intactSpireGeo, mats.andesiteReconstructed, presentIntact.length);
  presentIntact.forEach((c, i) => {
    dummy.position.set(c.x, c.y + 2.75, c.z);
    dummy.updateMatrix();
    pIntactB.setMatrixAt(i, dummy.matrix);
    dummy.position.set(c.x, c.y + 9.2, c.z);
    dummy.updateMatrix();
    pIntactS.setMatrixAt(i, dummy.matrix);
  });

  const pRuined = new THREE.InstancedMesh(ruinedGeo, mats.andesiteWeathered, presentRuined.length);
  presentRuined.forEach((c, i) => {
    dummy.position.set(c.x, c.y + 0.75, c.z);
    dummy.updateMatrix();
    pRuined.setMatrixAt(i, dummy.matrix);
  });

  const pFallen = new THREE.InstancedMesh(fallenGeo, mats.andesiteWeathered, presentFallen.length);
  presentFallen.forEach((c, i) => {
    dummy.position.set(c.x + ((i % 3) - 1) * 0.8, c.y + 0.45, c.z);
    dummy.rotation.set(0, (i * 0.7) % Math.PI, 0);
    dummy.updateMatrix();
    pFallen.setMatrixAt(i, dummy.matrix);
  });
  perwaraPresentGroup.add(pIntactB, pIntactS, pRuined, pFallen);

  // 9. OUTER LANDSCAPE: Tropical Javanese Trees & Distant Mount Merapi
  const treeCount = 70;
  const trunkGeo = new THREE.CylinderGeometry(0.28, 0.42, 6.5, 7);
  const crownGeo = new THREE.DodecahedronGeometry(2.9, 1);
  const trunks = new THREE.InstancedMesh(trunkGeo, mats.trunk, treeCount);
  const crowns = new THREE.InstancedMesh(crownGeo, mats.foliage, treeCount);
  for (let i = 0; i < treeCount; i++) {
    const ang = (i / treeCount) * Math.PI * 2;
    const rad = 148 + (i % 5) * 18;
    const tx = Math.cos(ang) * rad;
    const tz = Math.sin(ang) * rad;
    // Leave East and South avenues open
    if (Math.abs(tz) < 12 && tx > 0) continue;
    if (Math.abs(tx) < 12 && tz > 0) continue;
    dummy.position.set(tx, 3.25, tz);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();
    trunks.setMatrixAt(i, dummy.matrix);
    dummy.position.set(tx, 7.2, tz);
    dummy.updateMatrix();
    crowns.setMatrixAt(i, dummy.matrix);
  }
  scene.add(trunks, crowns);

  // Distant Mount Merapi volcano to the North (-Z)
  const merapi = new THREE.Mesh(
    new THREE.ConeGeometry(280, 175, 24),
    new THREE.MeshStandardMaterial({ color: 0x48545c, roughness: 0.95 })
  );
  merapi.position.set(0, 82, -680);
  scene.add(merapi);

  // 10. AUDIT & ICONOGRAPHIC EXTENSIONS (Nandisvara/Mahakala, 24 Ashtadikpalas, Brahma-Maharishis, Prambanan Motif)
  buildArchitecturalSculptures(scene, mats, interactables, colliders);

  return {
    colliders,
    walkableSurfaces,
    stairRamps,
    interactables,
    setHistoricalMode(isHistorical) {
      perwaraPresentGroup.visible = !isHistorical;
      perwaraHistGroup.visible = isHistorical;
      hypotheticalGroup.visible = isHistorical;
    },
  };
}
