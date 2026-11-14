/**
 * PRAMBANAN — THE SACRED CITY OF JAVA
 * Main Three.js Application, Lighting Modes, Minimap, Checklist, Info Panel & Pause Menu
 */
import * as THREE from "three";
import { createMaterials } from "./materials.js";
import { buildPrambananComplex } from "./temple_builder.js";
import { FirstPersonController } from "./player_controller.js";
import { PrambananAudio } from "./audio_engine.js";
import { DEITIES_AND_STRUCTURES } from "../data/prambanan_lore.js";
import { INSCRIPTIONS_DATA } from "../data/inscriptions_data.js";
import { MUSEUM_CATEGORIES, SCULPTURE_CATALOGUE } from "../data/sculpture_inventory.js";

const LIGHTING_PRESETS = {
  sunrise: {
    label: "Golden Sunrise",
    sky: 0xe6a87c,
    fog: 0xdca57d,
    fogDensity: 0.0022,
    sunColor: 0xffb36b,
    sunIntensity: 2.3,
    sunPos: [160, 42, -60],
    hemiSky: 0xffd2a6,
    hemiGround: 0x3b3328,
    hemiIntensity: 0.65,
    lanterns: 0.2,
  },
  daytime: {
    label: "Bright Daytime",
    sky: 0x87b8de,
    fog: 0x9ec4e0,
    fogDensity: 0.0014,
    sunColor: 0xfff8eb,
    sunIntensity: 2.8,
    sunPos: [95, 165, 75],
    hemiSky: 0xd6ecff,
    hemiGround: 0x454a36,
    hemiIntensity: 0.78,
    lanterns: 0.0,
  },
  sunset: {
    label: "Sunset",
    sky: 0xc46b54,
    fog: 0xb66756,
    fogDensity: 0.0024,
    sunColor: 0xff7b47,
    sunIntensity: 2.2,
    sunPos: [-160, 38, 65],
    hemiSky: 0xf49d76,
    hemiGround: 0x2c2220,
    hemiIntensity: 0.55,
    lanterns: 0.6,
  },
  evening: {
    label: "Evening Illumination",
    sky: 0x131b2e,
    fog: 0x141d30,
    fogDensity: 0.0028,
    sunColor: 0x7a96cc,
    sunIntensity: 0.55,
    sunPos: [-80, 120, -90],
    hemiSky: 0x2e4166,
    hemiGround: 0x141418,
    hemiIntensity: 0.42,
    lanterns: 2.6,
  },
};

const CHECKLIST_ITEMS = [
  { id: "SHIVA_MAHADEVA", label: "Shiva East Chamber (Shiva Mahadeva)" },
  { id: "DURGA_MAHISHASURAMARDINI", label: "Shiva North Chamber (Durga)" },
  { id: "GANESHA", label: "Shiva West Chamber (Ganesha)" },
  { id: "AGASTYA", label: "Shiva South Chamber (Agastya)" },
  { id: "VISHNU_TEMPLE", label: "Candi Vishnu Sanctum" },
  { id: "BRAHMA_TEMPLE", label: "Candi Brahma Sanctum" },
  { id: "NANDI_TEMPLE", label: "Candi Nandi (Bull, Surya, Chandra)" },
  { id: "GARUDA_TEMPLE", label: "Candi Garuda" },
  { id: "HAMSA_TEMPLE", label: "Candi Hamsa (Angsa)" },
  { id: "RAMAYANA_GALLERY", label: "Ramayana Relief Gallery" },
];

const WAYPOINTS = [
  { name: "Eastern Approach Gate", pos: [145, 0, 0], yaw: Math.PI * 0.5 },
  { name: "Shivagrha Stele (856 CE)", pos: [48.2, 3.5, 5.2], yaw: Math.PI * 0.5 },
  { name: "Inner Courtyard Plaza", pos: [2, 3.5, 0], yaw: Math.PI * 0.5 },
  { name: "Candi Shiva — East (Shiva)", pos: [-10.5, 11.02, 0], yaw: Math.PI * 0.5 },
  { name: "Candi Shiva — North (Durga)", pos: [-18, 11.02, -7.8], yaw: Math.PI },
  { name: "Candi Shiva — West (Ganesha)", pos: [-25.5, 11.02, 0], yaw: -Math.PI * 0.5 },
  { name: "Candi Shiva — South (Agastya)", pos: [-18, 11.02, 7.8], yaw: 0 },
  { name: "Candi Vishnu Sanctum", pos: [-11.8, 8.78, -32], yaw: Math.PI * 0.5 },
  { name: "Candi Brahma Sanctum", pos: [-11.8, 8.78, 32], yaw: Math.PI * 0.5 },
  { name: "Candi Nandi Sanctum", pos: [14.8, 7.5, 0], yaw: -Math.PI * 0.5 },
  { name: "Shiva Ramayana Gallery", pos: [-5.5, 11.02, 6.5], yaw: Math.PI * 0.5 },
  { name: "Nandisvara & Mahakala Guardians", pos: [2.5, 3.5, 0], yaw: Math.PI * 0.5 },
  { name: "Shiva 24 Exterior Guardians", pos: [-5.5, 11.02, 10.5], yaw: Math.PI * 0.75 },
];

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.15, 1400);

// Lighting
const sunLight = new THREE.DirectionalLight(0xfff8eb, 2.8);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.near = 10;
sunLight.shadow.camera.far = 420;
const d = 140;
sunLight.shadow.camera.left = -d;
sunLight.shadow.camera.right = d;
sunLight.shadow.camera.top = d;
sunLight.shadow.camera.bottom = -d;
scene.add(sunLight);

const hemiLight = new THREE.HemisphereLight(0xd6ecff, 0x454a36, 0.78);
scene.add(hemiLight);

// Always-on warm oil-lamp style interior sanctum lights so all deities are clearly inspectable
for (const [lx, ly, lz] of [
  [-12.5, 13.8, 0], [-18, 13.8, -5.5], [-23.5, 13.8, 0], [-18, 13.8, 5.5],
  [-15.5, 11.4, -32], [-15.5, 11.4, 32], [18.0, 9.8, 0],
]) {
  const sl = new THREE.PointLight(0xffcf88, 2.2, 16, 1.4);
  sl.position.set(lx, ly, lz);
  scene.add(sl);
}

// Evening illumination warm exterior floodlights for Trimurti & Vahana spires
const eveningLights = [];
for (const [lx, ly, lz] of [
  [-2, 10, 0], [-2, 10, -32], [-2, 10, 32],
  [8, 9, 0], [8, 9, -32], [8, 9, 32], [2, 8, 0],
]) {
  const pl = new THREE.PointLight(0xffaa55, 0, 48, 1.2);
  pl.position.set(lx, ly, lz);
  scene.add(pl);
  eveningLights.push(pl);
}

// Build Prambanan Complex
const mats = createMaterials();
const world = buildPrambananComplex(scene, mats);
const player = new FirstPersonController(camera, renderer.domElement, world);
const audio = new PrambananAudio();
player.onStep = () => audio.playFootstep();

// State
let currentLighting = "daytime";
let isHistoricalMode = false;
let activeTarget = null;
const visitedSet = new Set();

function applyLighting(modeKey) {
  const p = LIGHTING_PRESETS[modeKey] || LIGHTING_PRESETS.daytime;
  currentLighting = modeKey;
  scene.background = new THREE.Color(p.sky);
  scene.fog = new THREE.FogExp2(p.fog, p.fogDensity);
  sunLight.color.setHex(p.sunColor);
  sunLight.intensity = p.sunIntensity;
  sunLight.position.set(...p.sunPos);
  hemiLight.color.setHex(p.hemiSky);
  hemiLight.groundColor.setHex(p.hemiGround);
  hemiLight.intensity = p.hemiIntensity;
  for (const pl of eveningLights) pl.intensity = p.lanterns;
  document.getElementById("hud-lighting").textContent = `Lighting: ${p.label} (1-4)`;
}

function toggleHistoricalMode(forceVal = null) {
  isHistoricalMode = forceVal !== null ? forceVal : !isHistoricalMode;
  world.setHistoricalMode(isHistoricalMode);
  document.getElementById("hud-mode").textContent = isHistoricalMode
    ? "Mode B: 9th-Century Historical Reconstruction (M)"
    : "Mode A: Present-Day Archaeological View (M)";
}

// UI Elements
const promptEl = document.getElementById("interact-prompt");
const infoPanel = document.getElementById("info-panel");
const epigraphyPanel = document.getElementById("epigraphy-panel");
const pauseMenu = document.getElementById("pause-menu");
const checklistEl = document.getElementById("checklist-items");
const minimapCanvas = document.getElementById("minimap");
const mmCtx = minimapCanvas.getContext("2d");

function renderChecklist() {
  checklistEl.innerHTML = "";
  let done = 0;
  for (const item of CHECKLIST_ITEMS) {
    const checked = visitedSet.has(item.id);
    if (checked) done++;
    const li = document.createElement("div");
    li.className = `check-item ${checked ? "done" : ""}`;
    li.textContent = `${checked ? "✓" : "○"} ${item.label}`;
    checklistEl.appendChild(li);
  }
  document.getElementById("checklist-progress").textContent = `${done}/${CHECKLIST_ITEMS.length} Explored`;
}

function openInfoPanel(interactable) {
  if (interactable.type === "inscription") {
    const epi = INSCRIPTIONS_DATA[interactable.id];
    if (!epi) return;
    document.getElementById("epi-title").textContent = epi.name;
    document.getElementById("epi-script-note").textContent = epi.scriptNote;
    document.getElementById("epi-provenance").textContent = epi.provenance;
    document.getElementById("epi-original").textContent = epi.originalScript;
    document.getElementById("epi-transcription").textContent = epi.transcription;
    document.getElementById("epi-iast").textContent = epi.iast;
    document.getElementById("epi-translation").textContent = epi.translation;
    document.getElementById("epi-history").textContent = epi.historicalExplanation;
    document.getElementById("epi-sources").textContent = epi.sources;
    epigraphyPanel.classList.remove("hidden");
    player.paused = true;
    document.exitPointerLock?.();
    return;
  }

  let data = null;
  if (interactable.type === "relief") {
    data = interactable.panelData;
    visitedSet.add("RAMAYANA_GALLERY");
  } else {
    data = DEITIES_AND_STRUCTURES[interactable.id];
    if (interactable.id) visitedSet.add(interactable.id);
  }
  if (!data) return;

  renderChecklist();
  document.getElementById("info-title").textContent = data.name;
  document.getElementById("info-sanskrit").textContent = data.sanskrit || "";
  document.getElementById("info-category").textContent = data.category;
  document.getElementById("info-status").textContent = data.evidenceStatus;
  document.getElementById("info-bg").textContent = data.background;
  document.getElementById("info-icon").textContent = data.iconography;
  document.getElementById("info-arch").textContent = data.archaeology;
  document.getElementById("info-src").textContent = data.sources;

  infoPanel.classList.remove("hidden");
  player.paused = true;
  document.exitPointerLock?.();
}

const museumModal = document.getElementById("museum-modal");
const museumSearch = document.getElementById("museum-search");
const museumCats = document.getElementById("museum-cats");
const museumList = document.getElementById("museum-list");
let selectedMuseumCat = "All";

function renderMuseumCatalogue() {
  const q = (museumSearch.value || "").trim().toLowerCase();
  museumCats.innerHTML = "";
  MUSEUM_CATEGORIES.forEach((cat) => {
    const b = document.createElement("button");
    b.className = `cat-btn ${selectedMuseumCat === cat ? "active" : ""}`;
    b.textContent = cat;
    b.onclick = () => {
      selectedMuseumCat = cat;
      renderMuseumCatalogue();
    };
    museumCats.appendChild(b);
  });

  const filtered = SCULPTURE_CATALOGUE.filter((item) => {
    if (selectedMuseumCat !== "All" && item.category !== selectedMuseumCat) return false;
    if (!q) return true;
    const hay = `${item.id} ${item.name} ${item.sanskrit} ${item.javanese} ${item.originalLocation} ${item.presentCondition} ${item.attributes}`.toLowerCase();
    return hay.includes(q);
  });

  museumList.innerHTML = "";
  if (filtered.length === 0) {
    museumList.innerHTML = `<div class="museum-item">No matching sculptures found.</div>`;
    return;
  }
  filtered.forEach((item) => {
    const card = document.createElement("div");
    card.className = "museum-item";
    card.innerHTML = `
      <h3>${item.name}</h3>
      <div class="sanskrit" style="margin-bottom:4px;">${item.sanskrit} &nbsp;|&nbsp; ${item.javanese}</div>
      <div class="badge-row" style="margin-bottom:6px;">
        <span class="badge">${item.category}</span>
        <span class="badge">${item.status}</span>
        <span class="badge">${item.confidence}</span>
      </div>
      <div class="museum-meta"><b>Original Location:</b> ${item.originalLocation}</div>
      <div class="museum-meta"><b>Present Condition:</b> ${item.presentCondition}</div>
      <div class="museum-meta"><b>Attributes:</b> ${item.attributes}</div>
      <div class="museum-meta"><b>Photo Ref:</b> ${item.photoRef}</div>
      <div class="btn-row" style="margin-top:8px;">
        <button class="primary-btn btn-tp">Teleport &amp; Inspect</button>
      </div>
    `;
    card.querySelector(".btn-tp").onclick = () => {
      const wp = item.waypoint;
      player.teleport(wp.pos[0], wp.pos[1], wp.pos[2], wp.yaw);
      toggleMuseumModal(false);
    };
    museumList.appendChild(card);
  });
}

function toggleMuseumModal(forceVal = null) {
  const willShow = forceVal !== null ? forceVal : museumModal.classList.contains("hidden");
  if (willShow) {
    pauseMenu.classList.add("hidden");
    infoPanel.classList.add("hidden");
    epigraphyPanel.classList.add("hidden");
    renderMuseumCatalogue();
  }
  museumModal.classList.toggle("hidden", !willShow);
  player.paused = willShow;
  if (willShow) document.exitPointerLock?.();
}

museumSearch.addEventListener("input", renderMuseumCatalogue);
document.getElementById("btn-close-museum").onclick = () => toggleMuseumModal(false);
document.getElementById("btn-open-museum").onclick = () => toggleMuseumModal(true);

function closeInfoPanel() {
  infoPanel.classList.add("hidden");
  epigraphyPanel.classList.add("hidden");
  museumModal.classList.add("hidden");
  if (pauseMenu.classList.contains("hidden")) {
    player.paused = false;
  }
}

function togglePauseMenu() {
  if (!infoPanel.classList.contains("hidden") || !epigraphyPanel.classList.contains("hidden") || !museumModal.classList.contains("hidden")) {
    closeInfoPanel();
    return;
  }
  if (player.orbitMode) {
    player.toggleOrbitMode();
    return;
  }
  const willShow = pauseMenu.classList.contains("hidden");
  pauseMenu.classList.toggle("hidden", !willShow);
  player.paused = willShow;
  if (willShow) document.exitPointerLock?.();
}

// Populate Waypoints in Pause Menu
const wpContainer = document.getElementById("waypoints-list");
WAYPOINTS.forEach((wp) => {
  const btn = document.createElement("button");
  btn.textContent = wp.name;
  btn.onclick = () => {
    player.teleport(wp.pos[0], wp.pos[1], wp.pos[2], wp.yaw);
    togglePauseMenu();
  };
  wpContainer.appendChild(btn);
});

document.getElementById("btn-close-info").onclick = closeInfoPanel;
document.getElementById("btn-close-epi").onclick = closeInfoPanel;
document.getElementById("btn-resume").onclick = togglePauseMenu;
document.getElementById("btn-toggle-mode").onclick = () => toggleHistoricalMode();
document.getElementById("btn-toggle-music").onclick = (e) => {
  audio.resume();
  audio.musicEnabled = !audio.musicEnabled;
  e.target.textContent = `Gamelan Ambience: ${audio.musicEnabled ? "ON" : "OFF"}`;
};
document.querySelectorAll("[data-light]").forEach((btn) => {
  btn.onclick = () => applyLighting(btn.dataset.light);
});

let activeHitPoint = null;
window.addEventListener("keydown", (e) => {
  if (document.activeElement === museumSearch) {
    if (e.code === "Escape") toggleMuseumModal(false);
    return;
  }
  audio.resume();
  if (e.code === "KeyE" && activeTarget && infoPanel.classList.contains("hidden") && pauseMenu.classList.contains("hidden") && museumModal.classList.contains("hidden")) {
    openInfoPanel(activeTarget);
  } else if (e.code === "KeyC" && infoPanel.classList.contains("hidden") && epigraphyPanel.classList.contains("hidden")) {
    toggleMuseumModal();
  } else if (e.code === "KeyR" && !player.paused) {
    player.toggleOrbitMode(activeHitPoint);
  } else if (e.code === "Escape") {
    togglePauseMenu();
  } else if (e.code === "Digit1") applyLighting("sunrise");
  else if (e.code === "Digit2") applyLighting("daytime");
  else if (e.code === "Digit3") applyLighting("sunset");
  else if (e.code === "Digit4") applyLighting("evening");
  else if (e.code === "KeyM") toggleHistoricalMode();
});

// Raycaster for Interaction Prompt
const raycaster = new THREE.Raycaster();
const centerNDC = new THREE.Vector2(0, 0);

function updateInteractionPrompt() {
  if (player.orbitMode) {
    promptEl.textContent = "Orbit Inspection Active — Drag / WASD Rotate & Zoom  |  [R / Esc] Exit";
    promptEl.classList.remove("hidden");
    return;
  }
  raycaster.setFromCamera(centerNDC, camera);
  const hits = raycaster.intersectObjects(world.interactables, true);
  activeTarget = null;
  activeHitPoint = null;
  if (hits.length > 0 && hits[0].distance <= 6.2) {
    const obj = hits[0].object;
    if (obj.userData?.interactable) {
      activeTarget = obj.userData.interactable;
      activeHitPoint = hits[0].point.clone();
    }
  }
  if (activeTarget && !player.paused) {
    promptEl.textContent = `[E] ${activeTarget.label}  |  [R] Orbit/Rotate  |  [Z] Zoom`;
    promptEl.classList.remove("hidden");
  } else {
    promptEl.classList.add("hidden");
  }
}

function updateProximityChecklist() {
  const { x, y, z } = player.position;
  if (y > 9.5) {
    if (Math.hypot(x - -14, z) < 3.2) visitedSet.add("SHIVA_MAHADEVA");
    if (Math.hypot(x - -18, z + 4) < 3.2) visitedSet.add("DURGA_MAHISHASURAMARDINI");
    if (Math.hypot(x - -22, z) < 3.2) visitedSet.add("GANESHA");
    if (Math.hypot(x - -18, z - 4) < 3.2) visitedSet.add("AGASTYA");
  }
  if (y > 7.5) {
    if (Math.hypot(x - -18, z + 32) < 5.0) visitedSet.add("VISHNU_TEMPLE");
    if (Math.hypot(x - -18, z - 32) < 5.0) visitedSet.add("BRAHMA_TEMPLE");
  }
  if (y > 6.5) {
    if (Math.hypot(x - 20, z) < 4.5) visitedSet.add("NANDI_TEMPLE");
    if (Math.hypot(x - 20, z + 32) < 4.5) visitedSet.add("GARUDA_TEMPLE");
    if (Math.hypot(x - 20, z - 32) < 4.5) visitedSet.add("HAMSA_TEMPLE");
  }
  renderChecklist();
}

function drawMinimap() {
  const w = minimapCanvas.width;
  const h = minimapCanvas.height;
  mmCtx.clearRect(0, 0, w, h);
  mmCtx.fillStyle = "rgba(18, 22, 24, 0.85)";
  mmCtx.fillRect(0, 0, w, h);

  const scale = w / 260;
  const toMap = (wx, wz) => [w * 0.5 + wx * scale, h * 0.5 + wz * scale];

  // Perwara concentric squares
  mmCtx.strokeStyle = "rgba(180, 165, 130, 0.35)";
  mmCtx.lineWidth = 1;
  for (const half of [111, 97, 83, 69, 55]) {
    const [x0, y0] = toMap(-half, -half);
    mmCtx.strokeRect(x0, y0, half * 2 * scale, half * 2 * scale);
  }

  // Main temples
  const drawRect = (cx, cz, size, color) => {
    const [mx, my] = toMap(cx - size * 0.5, cz - size * 0.5);
    mmCtx.fillStyle = color;
    mmCtx.fillRect(mx, my, size * scale, size * scale);
  };
  drawRect(-18, 0, 34, "#d4a857");   // Shiva
  drawRect(-18, -32, 20, "#c89d54"); // Vishnu
  drawRect(-18, 32, 20, "#c89d54");  // Brahma
  drawRect(20, 0, 15, "#a88b5a");    // Nandi
  drawRect(20, -32, 14, "#a88b5a");  // Garuda
  drawRect(20, 32, 14, "#a88b5a");   // Hamsa
  drawRect(1, -43, 6.5, "#8a7a62");  // Apit N
  drawRect(1, 43, 6.5, "#8a7a62");   // Apit S

  // Player dot & facing arrow
  const [px, py] = toMap(player.position.x, player.position.z);
  mmCtx.fillStyle = "#5eead4";
  mmCtx.beginPath();
  mmCtx.arc(px, py, 3.8, 0, Math.PI * 2);
  mmCtx.fill();
  mmCtx.strokeStyle = "#5eead4";
  mmCtx.lineWidth = 2;
  mmCtx.beginPath();
  mmCtx.moveTo(px, py);
  mmCtx.lineTo(px - Math.sin(player.yaw) * 10, py - Math.cos(player.yaw) * 10);
  mmCtx.stroke();
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Initialize
applyLighting("daytime");
toggleHistoricalMode(false);
renderChecklist();

// Expose automation/testing API
window.__PRAMBANAN__ = {
  player,
  applyLighting,
  toggleHistoricalMode,
  openInfoPanel,
  closeInfoPanel,
  toggleMuseumModal,
  visitedSet,
  WAYPOINTS,
  getStats: () => ({
    pos: player.position.toArray(),
    lighting: currentLighting,
    historicalMode: isHistoricalMode,
    visitedCount: visitedSet.size,
    collidersCount: world.colliders.length,
    interactablesCount: world.interactables.length,
  }),
};

let last = performance.now();
let checkTimer = 0;
function animate(now) {
  requestAnimationFrame(animate);
  const dt = (now - last) / 1000;
  last = now;

  player.update(dt);
  updateInteractionPrompt();
  drawMinimap();

  checkTimer += dt;
  if (checkTimer > 0.4) {
    checkTimer = 0;
    updateProximityChecklist();
  }

  renderer.render(scene, camera);
}
requestAnimationFrame(animate);
