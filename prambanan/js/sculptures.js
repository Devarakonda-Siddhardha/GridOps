/**
 * Hindu Iconography & Deity Sculptures Builder (Three.js)
 * Builds historically grounded Central Javanese sculptures with collision boxes
 * and interactive inspection metadata.
 */
import * as THREE from "three";

function addPart(group, geo, mat, pos, rot = [0, 0, 0]) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(pos[0], pos[1], pos[2]);
  m.rotation.set(rot[0], rot[1], rot[2]);
  m.castShadow = true;
  m.receiveShadow = true;
  group.add(m);
  return m;
}

function tagInteractive(group, loreId, label, colliders, halfExtents = [0.95, 0.95]) {
  group.userData.interactable = { type: "deity", id: loreId, label };
  group.traverse((c) => {
    if (c.isMesh) {
      c.userData.interactable = { type: "deity", id: loreId, label };
    }
  });
  // Register sculpture collider so player never clips through deity statues
  const wp = new THREE.Vector3();
  group.getWorldPosition(wp);
  colliders.push({
    minX: wp.x - halfExtents[0],
    maxX: wp.x + halfExtents[0],
    minZ: wp.z - halfExtents[1],
    maxZ: wp.z + halfExtents[1],
    minY: wp.y,
    maxY: wp.y + 3.6,
  });
}

export function buildShivaMahadeva(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  // Yoni pedestal with Naga spout + Lotus cushion
  addPart(g, new THREE.BoxGeometry(1.7, 0.65, 1.7), mat, [0, 0.325, 0]);
  addPart(g, new THREE.CylinderGeometry(0.55, 0.62, 0.22, 16), mat, [0, 0.76, 0]);
  // Torso & legs
  addPart(g, new THREE.CylinderGeometry(0.24, 0.30, 0.95, 12), mat, [0, 1.35, 0]);
  addPart(g, new THREE.CylinderGeometry(0.30, 0.24, 0.68, 12), mat, [0, 2.08, 0]);
  // 4 Arms
  for (const s of [-1, 1]) {
    addPart(g, new THREE.CylinderGeometry(0.07, 0.06, 0.65, 8), mat, [s * 0.38, 2.12, 0.08], [0.2, 0, s * 0.25]);
    addPart(g, new THREE.CylinderGeometry(0.06, 0.05, 0.56, 8), mat, [s * 0.48, 2.34, -0.06], [-0.15, 0, s * 0.45]);
  }
  // Head + Jatamakuta crown + Prabhamandala stele
  addPart(g, new THREE.SphereGeometry(0.20, 14, 12), mat, [0, 2.60, 0]);
  addPart(g, new THREE.ConeGeometry(0.15, 0.44, 10), mat, [0, 2.94, 0]);
  addPart(g, new THREE.CylinderGeometry(0.52, 0.52, 0.12, 16), mat, [0, 2.55, -0.22], [Math.PI / 2, 0, 0]);

  tagInteractive(g, "SHIVA_MAHADEVA", "Inspect Shiva Mahadeva", colliders);
  interactables.push(g);
  return g;
}

export function buildDurgaMahishasuramardini(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  // Lotus pedestal + Mahisha buffalo
  addPart(g, new THREE.BoxGeometry(1.5, 0.52, 1.5), mat, [0, 0.26, 0]);
  addPart(g, new THREE.BoxGeometry(1.15, 0.38, 0.62), mat, [0, 0.70, 0]);
  addPart(g, new THREE.SphereGeometry(0.22, 12, 10), mat, [0.58, 0.78, 0]); // Buffalo head
  addPart(g, new THREE.CylinderGeometry(0.13, 0.15, 0.48, 10), mat, [-0.50, 0.92, 0.12]); // Mahishasura demon
  // 8-armed Goddess Durga standing atop Mahisha
  addPart(g, new THREE.CylinderGeometry(0.20, 0.24, 0.85, 12), mat, [0, 1.30, 0]);
  addPart(g, new THREE.CylinderGeometry(0.24, 0.18, 0.56, 12), mat, [0, 1.90, 0]);
  for (let i = 0; i < 4; i++) {
    const y = 1.78 + i * 0.13;
    for (const s of [-1, 1]) {
      addPart(g, new THREE.CylinderGeometry(0.045, 0.04, 0.48, 8), mat, [s * (0.30 + i * 0.08), y, 0.05], [0, 0, s * (0.3 + i * 0.15)]);
    }
  }
  addPart(g, new THREE.SphereGeometry(0.17, 14, 12), mat, [0, 2.36, 0]);
  addPart(g, new THREE.ConeGeometry(0.12, 0.38, 10), mat, [0, 2.66, 0]);
  addPart(g, new THREE.BoxGeometry(1.1, 1.9, 0.12), mat, [0, 1.85, -0.26]); // Back stele

  tagInteractive(g, "DURGA_MAHISHASURAMARDINI", "Inspect Durga Mahishasuramardini (Rara Jonggrang)", colliders);
  interactables.push(g);
  return g;
}

export function buildGanesha(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  addPart(g, new THREE.BoxGeometry(1.35, 0.52, 1.35), mat, [0, 0.26, 0]);
  addPart(g, new THREE.CylinderGeometry(0.54, 0.58, 0.20, 16), mat, [0, 0.62, 0]);
  // Seated pot-bellied body
  addPart(g, new THREE.SphereGeometry(0.42, 14, 12), mat, [0, 1.10, 0]);
  // Elephant head + curved trunk + crown
  addPart(g, new THREE.SphereGeometry(0.26, 14, 12), mat, [0, 1.66, 0.04]);
  addPart(g, new THREE.CylinderGeometry(0.08, 0.05, 0.40, 10), mat, [-0.06, 1.44, 0.26], [0.45, 0, 0.2]);
  addPart(g, new THREE.ConeGeometry(0.14, 0.34, 10), mat, [0, 2.02, 0]);
  for (const s of [-1, 1]) {
    addPart(g, new THREE.CylinderGeometry(0.075, 0.065, 0.50, 8), mat, [s * 0.42, 1.24, 0.06], [0, 0, s * 0.3]);
    addPart(g, new THREE.CylinderGeometry(0.065, 0.055, 0.44, 8), mat, [s * 0.50, 1.48, -0.05], [0, 0, s * 0.5]);
  }

  tagInteractive(g, "GANESHA", "Inspect Ganesha", colliders);
  interactables.push(g);
  return g;
}

export function buildAgastya(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  addPart(g, new THREE.BoxGeometry(1.3, 0.52, 1.3), mat, [0, 0.26, 0]);
  addPart(g, new THREE.CylinderGeometry(0.26, 0.30, 1.15, 12), mat, [0, 1.12, 0]);
  addPart(g, new THREE.SphereGeometry(0.27, 12, 10), mat, [0, 1.34, 0.10]); // Pot-belly
  addPart(g, new THREE.SphereGeometry(0.19, 12, 10), mat, [0, 1.90, 0]);
  addPart(g, new THREE.ConeGeometry(0.11, 0.28, 8), mat, [0, 1.70, 0.16], [Math.PI, 0, 0]); // Beard
  addPart(g, new THREE.CylinderGeometry(0.03, 0.03, 1.75, 8), mat, [0.36, 1.42, 0.14]); // Trisula staff

  tagInteractive(g, "AGASTYA", "Inspect Agastya (Shiva Mahaguru)", colliders);
  interactables.push(g);
  return g;
}

export function buildVishnu(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  addPart(g, new THREE.BoxGeometry(1.5, 0.60, 1.5), mat, [0, 0.30, 0]);
  addPart(g, new THREE.CylinderGeometry(0.25, 0.30, 1.50, 12), mat, [0, 1.38, 0]);
  for (const s of [-1, 1]) {
    addPart(g, new THREE.CylinderGeometry(0.065, 0.055, 0.60, 8), mat, [s * 0.38, 1.82, 0.08], [0.2, 0, s * 0.25]);
    addPart(g, new THREE.CylinderGeometry(0.055, 0.05, 0.52, 8), mat, [s * 0.48, 2.06, -0.06], [-0.15, 0, s * 0.45]);
  }
  addPart(g, new THREE.SphereGeometry(0.19, 14, 12), mat, [0, 2.38, 0]);
  addPart(g, new THREE.CylinderGeometry(0.12, 0.14, 0.44, 12), mat, [0, 2.72, 0]); // Kiritamakuta crown

  tagInteractive(g, "VISHNU_TEMPLE", "Inspect Lord Vishnu", colliders);
  interactables.push(g);
  return g;
}

export function buildBrahma(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  addPart(g, new THREE.BoxGeometry(1.5, 0.60, 1.5), mat, [0, 0.30, 0]);
  addPart(g, new THREE.CylinderGeometry(0.25, 0.30, 1.50, 12), mat, [0, 1.38, 0]);
  for (const s of [-1, 1]) {
    addPart(g, new THREE.CylinderGeometry(0.065, 0.055, 0.60, 8), mat, [s * 0.38, 1.82, 0.08], [0.2, 0, s * 0.25]);
    addPart(g, new THREE.CylinderGeometry(0.055, 0.05, 0.52, 8), mat, [s * 0.48, 2.06, -0.06], [-0.15, 0, s * 0.45]);
  }
  // 4 Heads facing cardinal directions (Caturmukha)
  for (const a of [0, Math.PI * 0.5, Math.PI, Math.PI * 1.5]) {
    addPart(g, new THREE.SphereGeometry(0.14, 12, 10), mat, [Math.cos(a) * 0.13, 2.38, Math.sin(a) * 0.13]);
  }
  addPart(g, new THREE.ConeGeometry(0.14, 0.40, 10), mat, [0, 2.72, 0]);

  tagInteractive(g, "BRAHMA_TEMPLE", "Inspect Lord Brahma (Caturmukha)", colliders);
  interactables.push(g);
  return g;
}

export function buildNandi(pos, rotY, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  addPart(g, new THREE.BoxGeometry(2.2, 0.48, 1.5), mat, [0, 0.24, 0]);
  // Recumbent sacred bull Nandi
  addPart(g, new THREE.BoxGeometry(1.65, 0.70, 0.98), mat, [0, 0.82, 0]);
  addPart(g, new THREE.SphereGeometry(0.32, 12, 10), mat, [0.45, 1.24, 0]); // Hump
  addPart(g, new THREE.BoxGeometry(0.55, 0.40, 0.42), mat, [0.95, 1.12, 0]); // Head
  for (const s of [-1, 1]) {
    addPart(g, new THREE.ConeGeometry(0.05, 0.34, 8), mat, [0.85, 1.42, s * 0.20]); // Horns
  }
  // Flanking Surya & Chandra miniature reliefs/steles
  addPart(g, new THREE.BoxGeometry(0.35, 1.45, 0.55), mat, [-0.3, 0.96, -1.15]);
  addPart(g, new THREE.BoxGeometry(0.35, 1.45, 0.55), mat, [-0.3, 0.96, 1.15]);

  tagInteractive(g, "NANDI_TEMPLE", "Inspect Nandi, Surya & Chandra", colliders, [1.25, 1.4]);
  interactables.push(g);
  return g;
}
