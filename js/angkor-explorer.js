import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { SPAWN_POINTS, HISTORICAL_HOTSPOTS } from './angkor-data.js';
import { AngkorAudioAmbience } from './angkor-audio.js';

// ---------------------------------------------------------------------------
// Constants & Player Physics Config
// ---------------------------------------------------------------------------
const EYE_HEIGHT = 1.68;
const PLAYER_RADIUS = 0.42;
const STEP_HEIGHT = 0.65; // Allows smooth climbing of Bakan (0.42m/step) & Enc2 stairs
const WALK_SPEED = 6.8;
const SPRINT_SPEED = 13.5;
const JUMP_VELOCITY = 6.8;
const GRAVITY = 19.5;
const CELL_SIZE = 16.0;

// ---------------------------------------------------------------------------
// DOM Elements
// ---------------------------------------------------------------------------
const loadingScreen = document.getElementById('loading-screen');
const loadingBar = document.getElementById('loading-bar');
const loadingText = document.getElementById('loading-text');
const startOverlay = document.getElementById('start-overlay');
const btnEnter = document.getElementById('btn-enter');
const spawnSelect = document.getElementById('spawn-select');
const btnAudio = document.getElementById('btn-audio');
const hudZone = document.getElementById('hud-zone');
const hudCoords = document.getElementById('hud-coords');
const hudFps = document.getElementById('hud-fps');
const interactPrompt = document.getElementById('interact-prompt');
const interactTitle = document.getElementById('interact-title');
const infoModal = document.getElementById('info-modal');
const btnCloseModal = document.getElementById('btn-close-modal');

// ---------------------------------------------------------------------------
// Three.js Scene, Camera, Renderer
// ---------------------------------------------------------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xdcc7b0);
scene.fog = new THREE.FogExp2(0xd9c2a9, 0.0024);

const camera = new THREE.PerspectiveCamera(68, window.innerWidth / window.innerHeight, 0.15, 900);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
document.getElementById('canvas-container').appendChild(renderer.domElement);

const controls = new PointerLockControls(camera, document.body);
const audio = new AngkorAudioAmbience();

// ---------------------------------------------------------------------------
// Cambodian Sunrise Lighting & Sky Dome
// ---------------------------------------------------------------------------
function setupAtmosphere() {
  // Sky gradient dome
  const skyGeo = new THREE.SphereGeometry(520, 24, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x3a6ea5) },
      midColor: { value: new THREE.Color(0xe6b88a) },
      bottomColor: { value: new THREE.Color(0xf4d4a8) }
    },
    vertexShader: `
      varying vec3 vWorldPos;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vWorldPos = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: `
      uniform vec3 topColor;
      uniform vec3 midColor;
      uniform vec3 bottomColor;
      varying vec3 vWorldPos;
      void main() {
        float h = normalize(vWorldPos).y;
        vec3 col = mix(bottomColor, midColor, smoothstep(-0.05, 0.18, h));
        col = mix(col, topColor, smoothstep(0.18, 0.72, h));
        gl_FragColor = vec4(col, 1.0);
      }
    `
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));

  // Hemisphere ambient light
  const hemi = new THREE.HemisphereLight(0xffe9cc, 0x5c4b3b, 0.92);
  scene.add(hemi);

  // Golden Sunrise Directional Sun (from East-Southeast)
  const sun = new THREE.DirectionalLight(0xffdcb0, 2.35);
  sun.position.set(160, 88, 65);
  sun.castShadow = true;
  sun.shadow.mapSize.width = 2048;
  sun.shadow.mapSize.height = 2048;
  sun.shadow.camera.near = 20;
  sun.shadow.camera.far = 480;
  const d = 165;
  sun.shadow.camera.left = -d;
  sun.shadow.camera.right = d;
  sun.shadow.camera.top = d;
  sun.shadow.camera.bottom = -d;
  sun.shadow.bias = -0.0005;
  scene.add(sun);

  // Subtle fill light from West for gallery & relief readability
  const westFill = new THREE.DirectionalLight(0xb8d0eb, 0.48);
  westFill.position.set(-140, 50, -40);
  scene.add(westFill);

  // Warm Garbhagriha Sanctum Glow around Lord Vishnu
  const sanctumLight = new THREE.PointLight(0xffb85c, 4.5, 16, 1.4);
  sanctumLight.position.set(19.0, 16.5, 0);
  scene.add(sanctumLight);
}

setupAtmosphere();

// ---------------------------------------------------------------------------
// Circling Tropical Birds (Lightweight Instanced Meshes)
// ---------------------------------------------------------------------------
const birds = [];
function createCirclingBirds() {
  const birdGeo = new THREE.ConeGeometry(0.22, 0.75, 4);
  birdGeo.rotateX(Math.PI / 2);
  const birdMat = new THREE.MeshBasicMaterial({ color: 0x2b2623 });
  for (let i = 0; i < 14; i++) {
    const mesh = new THREE.Mesh(birdGeo, birdMat);
    const radius = 32 + (i % 5) * 14;
    const height = 42 + (i % 4) * 6;
    const speed = 0.14 + (i % 3) * 0.04;
    const phase = (i / 14) * Math.PI * 2;
    scene.add(mesh);
    birds.push({ mesh, radius, height, speed, phase });
  }
}
createCirclingBirds();

// ---------------------------------------------------------------------------
// Spatial Grid Collision & GLB Loading
// ---------------------------------------------------------------------------
const spatialGrid = new Map();
const solidMeshes = [];
const waterMeshes = [];

function addMeshToGrid(mesh) {
  const box = new THREE.Box3().setFromObject(mesh);
  const minX = Math.floor(box.min.x / CELL_SIZE);
  const maxX = Math.floor(box.max.x / CELL_SIZE);
  const minZ = Math.floor(box.min.z / CELL_SIZE);
  const maxZ = Math.floor(box.max.z / CELL_SIZE);
  for (let cx = minX; cx <= maxX; cx++) {
    for (let cz = minZ; cz <= maxZ; cz++) {
      const key = `${cx},${cz}`;
      if (!spatialGrid.has(key)) spatialGrid.set(key, []);
      spatialGrid.get(key).push(mesh);
    }
  }
}

function getNearbySolids(x, z) {
  const cx = Math.floor(x / CELL_SIZE);
  const cz = Math.floor(z / CELL_SIZE);
  const result = new Set();
  for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
      const list = spatialGrid.get(`${cx + dx},${cz + dz}`);
      if (list) {
        for (let i = 0; i < list.length; i++) result.add(list[i]);
      }
    }
  }
  return Array.from(result);
}

// ---------------------------------------------------------------------------
// Interactive 3D Hotspot Markers
// ---------------------------------------------------------------------------
const hotspotMarkers = [];
function createHotspotMarkers() {
  const orbGeo = new THREE.OctahedronGeometry(0.32, 0);
  const orbMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, wireframe: false });
  const ringGeo = new THREE.RingGeometry(0.45, 0.58, 20);
  ringGeo.rotateX(-Math.PI / 2);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24, side: THREE.DoubleSide, transparent: true, opacity: 0.75 });

  HISTORICAL_HOTSPOTS.forEach((spot) => {
    const group = new THREE.Group();
    group.position.set(spot.pos[0], spot.pos[1] + 0.65, spot.pos[2]);

    const orb = new THREE.Mesh(orbGeo, orbMat);
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.position.y = -0.45;

    group.add(orb);
    group.add(ring);
    scene.add(group);
    hotspotMarkers.push({ group, orb, baseY: spot.pos[1] + 0.65, data: spot });
  });
}
createHotspotMarkers();

// ---------------------------------------------------------------------------
// Load Angkor Wat GLB
// ---------------------------------------------------------------------------
const loader = new GLTFLoader();
loader.load(
  './assets/models/angkor_wat_complete.glb',
  (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (!child.isMesh) return;
      const name = child.name || '';
      const isWater = name.includes('Water');
      const isFoliage = name.includes('Tropical_Palm_Fronds') || name.includes('Tropical_Canopy_Trees');

      if (isWater) {
        child.receiveShadow = true;
        if (child.material) {
          child.material.roughness = 0.08;
          child.material.metalness = 0.25;
        }
        waterMeshes.push(child);
      } else {
        child.castShadow = !name.includes('Sacred_Precinct_Ground');
        child.receiveShadow = true;
        if (!isFoliage) {
          solidMeshes.push(child);
        }
      }
    });

    scene.add(root);
    root.updateMatrixWorld(true);
    solidMeshes.forEach(addMeshToGrid);

    loadingText.textContent = 'Ready to explore Paramavishnuloka!';
    loadingBar.style.width = '100%';
    setTimeout(() => {
      loadingScreen.classList.add('hidden');
      startOverlay.classList.remove('hidden');
    }, 350);
  },
  (xhr) => {
    if (xhr.total > 0) {
      const pct = Math.min(99, Math.round((xhr.loaded / xhr.total) * 100));
      loadingBar.style.width = `${pct}%`;
      loadingText.textContent = `Loading 3D Temple Complex (${pct}%)...`;
    }
  },
  (err) => {
    console.error('GLB Load Error:', err);
    loadingText.textContent = 'Failed to load 3D model. Please check console or serve via HTTP.';
  }
);

// ---------------------------------------------------------------------------
// Spawn & UI Wiring
// ---------------------------------------------------------------------------
SPAWN_POINTS.forEach((sp, idx) => {
  const opt = document.createElement('option');
  opt.value = sp.id;
  opt.textContent = sp.name;
  spawnSelect.appendChild(opt);
});

const playerState = {
  feetY: 0.0,
  velY: 0.0,
  grounded: true,
  activeHotspot: null,
  modalOpen: false
};

function teleportToSpawn(spawnId) {
  const sp = SPAWN_POINTS.find((s) => s.id === spawnId) || SPAWN_POINTS[0];
  camera.position.set(sp.pos[0], sp.pos[1], sp.pos[2]);
  playerState.feetY = sp.pos[1] - EYE_HEIGHT;
  playerState.velY = 0;
  playerState.grounded = true;
  camera.rotation.set(0, sp.yaw, 0, 'YXZ');
  spawnSelect.value = sp.id;
}

teleportToSpawn('causeway');

spawnSelect.addEventListener('change', (e) => {
  teleportToSpawn(e.target.value);
  spawnSelect.blur();
});

btnEnter.addEventListener('click', () => {
  if (!playerState.modalOpen) {
    controls.lock();
  }
});

controls.addEventListener('lock', () => {
  startOverlay.classList.add('hidden');
});

controls.addEventListener('unlock', () => {
  if (!playerState.modalOpen) {
    startOverlay.classList.remove('hidden');
  }
});

btnAudio.addEventListener('click', () => {
  const on = audio.toggle();
  btnAudio.textContent = on ? '🔊 Sound: ON' : '🔇 Sound: OFF';
  btnAudio.classList.toggle('bg-amber-500/20', on);
  btnAudio.classList.toggle('border-amber-500/50', on);
  btnAudio.blur();
});

function openHotspotModal(spot) {
  playerState.modalOpen = true;
  controls.unlock();
  document.getElementById('modal-category').textContent = spot.category;
  document.getElementById('modal-title').textContent = spot.title;
  document.getElementById('modal-sanskrit').textContent = spot.sanskrit;
  document.getElementById('modal-context').textContent = spot.context;
  document.getElementById('modal-significance').textContent = spot.significance;
  document.getElementById('modal-evidence').textContent = spot.evidence;
  document.getElementById('modal-source').textContent = `Source: ${spot.source}`;
  infoModal.classList.remove('hidden');
}

function closeHotspotModal() {
  playerState.modalOpen = false;
  infoModal.classList.add('hidden');
  controls.lock();
}

btnCloseModal.addEventListener('click', closeHotspotModal);

// ---------------------------------------------------------------------------
// Input Handling
// ---------------------------------------------------------------------------
const keys = {};
window.addEventListener('keydown', (e) => {
  keys[e.code] = true;
  if (e.code === 'KeyE' && playerState.activeHotspot && !playerState.modalOpen) {
    openHotspotModal(playerState.activeHotspot);
  } else if ((e.code === 'Escape' || e.code === 'KeyE') && playerState.modalOpen) {
    closeHotspotModal();
  } else if (e.code === 'KeyM') {
    btnAudio.click();
  } else if (e.code.startsWith('Digit') && !playerState.modalOpen) {
    const idx = parseInt(e.code.replace('Digit', ''), 10) - 1;
    if (idx >= 0 && idx < SPAWN_POINTS.length) {
      teleportToSpawn(SPAWN_POINTS[idx].id);
    }
  }
});
window.addEventListener('keyup', (e) => {
  keys[e.code] = false;
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------------------------------------------------------------------------
// Physics, Collision & Stair Navigation
// ---------------------------------------------------------------------------
const raycaster = new THREE.Raycaster();
const downDir = new THREE.Vector3(0, -1, 0);
const radialDirs = [];
for (let i = 0; i < 8; i++) {
  const a = (i / 8) * Math.PI * 2;
  radialDirs.push(new THREE.Vector3(Math.cos(a), 0, Math.sin(a)));
}

function resolveHorizontalCollisions(pos, feetY, nearby) {
  const heights = [feetY + STEP_HEIGHT + 0.12, feetY + 1.25];
  for (const h of heights) {
    const origin = new THREE.Vector3(pos.x, h, pos.z);
    for (const dir of radialDirs) {
      raycaster.set(origin, dir);
      raycaster.far = PLAYER_RADIUS;
      const hits = raycaster.intersectObjects(nearby, false);
      if (hits.length > 0 && hits[0].distance < PLAYER_RADIUS) {
        const push = PLAYER_RADIUS - hits[0].distance;
        pos.x -= dir.x * push;
        pos.z -= dir.z * push;
      }
    }
  }
}

function getZoneLabel(x, y, z) {
  if (y > 12.5) {
    if (x > 14 && x < 26 && Math.abs(z) < 6) return 'Central Garbhagriha (Lord Vishnu Sanctum)';
    return 'The Bakan Summit (Mount Meru Terrace)';
  }
  if (y > 2.8) return 'Second Enclosure Terrace (Devata Galleries)';
  if (x < -210) return 'Western Approach Grounds';
  if (x < -140) return 'Western Causeway & Sheshanaga Bridge';
  if (x < -130) return 'Western Outer Gopura';
  if (x < -38) return 'Processional Avenue, Libraries & Reflection Pools';
  if (x >= -38 && x <= 78 && Math.abs(z) <= 52) {
    if (x > 71) return 'East Gallery (Samudra Manthana)';
    if (x < -31) return 'West Gallery (Mahabharata & Ramayana)';
    if (z > 44) return 'South Gallery (King Suryavarman II)';
    if (z < -44) return 'North Gallery (Sanskrit Epigraphy)';
    return 'First Enclosure Courtyard & Preah Poan';
  }
  return 'Sacred Temple Precinct';
}

// ---------------------------------------------------------------------------
// Main Animation Loop
// ---------------------------------------------------------------------------
let prevTime = performance.now();
let fpsFrames = 0;
let fpsTimer = 0;

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min(0.05, (now - prevTime) / 1000);
  prevTime = now;

  // FPS counter
  fpsFrames++;
  fpsTimer += dt;
  if (fpsTimer >= 0.5) {
    hudFps.textContent = `${Math.round(fpsFrames / fpsTimer)} FPS`;
    fpsFrames = 0;
    fpsTimer = 0;
  }

  // Animate birds & hotspot orbs
  const tSec = now * 0.001;
  for (const b of birds) {
    const a = tSec * b.speed + b.phase;
    const nx = 20 + Math.cos(a) * b.radius;
    const nz = Math.sin(a) * b.radius;
    b.mesh.position.set(nx, b.height + Math.sin(tSec * 2 + b.phase) * 0.8, nz);
    b.mesh.lookAt(20 + Math.cos(a + 0.1) * b.radius, b.height, Math.sin(a + 0.1) * b.radius);
  }
  for (const m of hotspotMarkers) {
    m.orb.rotation.y = tSec * 1.4;
    m.group.position.y = m.baseY + Math.sin(tSec * 2.2) * 0.12;
  }

  // Player Movement & Collision
  if (controls.isLocked && !playerState.modalOpen) {
    const forward = new THREE.Vector3();
    camera.getWorldDirection(forward);
    forward.y = 0;
    forward.normalize();

    const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

    let moveF = 0;
    let moveR = 0;
    if (keys['KeyW'] || keys['ArrowUp']) moveF += 1;
    if (keys['KeyS'] || keys['ArrowDown']) moveF -= 1;
    if (keys['KeyD'] || keys['ArrowRight']) moveR += 1;
    if (keys['KeyA'] || keys['ArrowLeft']) moveR -= 1;

    const speed = (keys['ShiftLeft'] || keys['ShiftRight']) ? SPRINT_SPEED : WALK_SPEED;
    const moveVec = new THREE.Vector3()
      .addScaledVector(forward, moveF)
      .addScaledVector(right, moveR);
    if (moveVec.lengthSq() > 0) moveVec.normalize().multiplyScalar(speed * dt);

    const pos = camera.position.clone();
    const prevX = pos.x;
    const prevZ = pos.z;
    pos.x += moveVec.x;
    pos.z += moveVec.z;

    // World bounds clamp
    pos.x = Math.max(-245, Math.min(185, pos.x));
    pos.z = Math.max(-200, Math.min(200, pos.z));

    const nearby = getNearbySolids(pos.x, pos.z);
    resolveHorizontalCollisions(pos, playerState.feetY, nearby);

    // Prevent stepping into moat or reflection pool water
    raycaster.set(new THREE.Vector3(pos.x, playerState.feetY + 1.5, pos.z), downDir);
    raycaster.far = 4.0;
    const waterHits = raycaster.intersectObjects(waterMeshes, false);
    const groundOrigin = new THREE.Vector3(pos.x, playerState.feetY + STEP_HEIGHT + 0.4, pos.z);
    raycaster.set(groundOrigin, downDir);
    raycaster.far = 25.0;
    const groundHits = raycaster.intersectObjects(nearby, false);

    const groundY = groundHits.length > 0 ? groundHits[0].point.y : 0.0;
    const waterY = waterHits.length > 0 ? waterHits[0].point.y : -99.0;

    if (waterY > groundY + 0.02 && playerState.feetY < waterY + 0.6) {
      // Blocked by water edge
      pos.x = prevX;
      pos.z = prevZ;
    } else {
      // Jump & Gravity
      if (keys['Space'] && playerState.grounded) {
        playerState.velY = JUMP_VELOCITY;
        playerState.grounded = false;
      }

      playerState.velY -= GRAVITY * dt;
      playerState.feetY += playerState.velY * dt;

      if (playerState.feetY <= groundY + 0.02 && playerState.velY <= 0) {
        playerState.feetY = groundY;
        playerState.velY = 0;
        playerState.grounded = true;
      } else if (playerState.grounded && groundY > playerState.feetY && groundY - playerState.feetY <= STEP_HEIGHT) {
        // Smooth step-up
        playerState.feetY = groundY;
      } else {
        playerState.grounded = false;
      }
    }

    camera.position.set(pos.x, playerState.feetY + EYE_HEIGHT, pos.z);
  }

  // Update Proximity Hotspot Prompt
  let closest = null;
  let closestDist = Infinity;
  for (const spot of HISTORICAL_HOTSPOTS) {
    const dx = camera.position.x - spot.pos[0];
    const dy = camera.position.y - spot.pos[1];
    const dz = camera.position.z - spot.pos[2];
    const dist = Math.hypot(dx, dy, dz);
    if (dist < spot.radius && dist < closestDist) {
      closest = spot;
      closestDist = dist;
    }
  }
  playerState.activeHotspot = closest;
  if (closest && !playerState.modalOpen) {
    interactTitle.textContent = closest.title;
    interactPrompt.classList.remove('hidden');
  } else {
    interactPrompt.classList.add('hidden');
  }

  // Update HUD Telemetry
  hudZone.textContent = getZoneLabel(camera.position.x, playerState.feetY, camera.position.z);
  hudCoords.textContent = `Elev: ${playerState.feetY.toFixed(1)}m • X:${camera.position.x.toFixed(0)} Z:${camera.position.z.toFixed(0)}`;

  renderer.render(scene, camera);
}

animate();
