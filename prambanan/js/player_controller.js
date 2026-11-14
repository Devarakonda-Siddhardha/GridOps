/**
 * First-Person Human-Scale Player Controller
 * Controls: W/A/S/D move, Mouse look (PointerLock), Space jump, Shift run,
 * E interact, Z/Right-click zoom inspection, Esc pause menu.
 */
import * as THREE from "three";

export class FirstPersonController {
  constructor(camera, domElement, { colliders, walkableSurfaces, stairRamps }) {
    this.camera = camera;
    this.domElement = domElement;
    this.colliders = colliders;
    this.walkableSurfaces = walkableSurfaces;
    this.stairRamps = stairRamps;

    this.eyeHeight = 1.68;
    this.radius = 0.42;
    this.position = new THREE.Vector3(145, 0, 0); // Start on Eastern historical approach
    this.yaw = Math.PI * 0.5; // Facing West toward Candi Prambanan
    this.pitch = 0.04;
    this.velY = 0;
    this.onGround = true;

    this.keys = new Set();
    this.locked = false;
    this.paused = false;
    this.zoomed = false;
    this.orbitMode = false;
    this.orbitTarget = new THREE.Vector3();
    this.orbitYaw = 0;
    this.orbitPitch = 0.2;
    this.orbitDist = 3.8;
    this.orbitDragging = false;
    this.dragging = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;
    this.stepTimer = 0;
    this.onStep = null;

    this._bindEvents();
    this.syncCamera();
  }

  _bindEvents() {
    window.addEventListener("keydown", (e) => {
      this.keys.add(e.code);
      if (e.code === "KeyZ") this.setZoom(!this.zoomed);
    });
    window.addEventListener("keyup", (e) => this.keys.delete(e.code));

    document.addEventListener("pointerlockchange", () => {
      this.locked = document.pointerLockElement === this.domElement;
    });

    window.addEventListener("mousemove", (e) => {
      const dx = this.locked ? (e.movementX || 0) : (e.clientX - this.lastMouseX);
      const dy = this.locked ? (e.movementY || 0) : (e.clientY - this.lastMouseY);
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;

      if (this.orbitMode && this.orbitDragging) {
        this.orbitYaw -= dx * 0.008;
        this.orbitPitch = Math.max(-0.5, Math.min(1.1, this.orbitPitch + dy * 0.006));
        return;
      }
      if (this.paused || this.orbitMode) return;
      if (!this.locked && !this.dragging) return;
      const sens = this.zoomed ? 0.0012 : 0.0032;
      this.yaw -= dx * sens;
      this.pitch = Math.max(-1.38, Math.min(1.38, this.pitch - dy * sens));
    });

    this.domElement.addEventListener("mousedown", (e) => {
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
      if (this.orbitMode && e.button === 0) {
        this.orbitDragging = true;
        return;
      }
      if (e.button === 2) {
        this.setZoom(true);
      } else if (e.button === 0 && !this.paused && !this.orbitMode) {
        this.dragging = true;
        if (!this.locked && this.domElement.requestPointerLock) {
          try {
            const res = this.domElement.requestPointerLock();
            if (res && typeof res.catch === "function") res.catch(() => {});
          } catch (_) {}
        }
      }
    });
    window.addEventListener("mouseup", (e) => {
      if (e.button === 0) {
        this.dragging = false;
        this.orbitDragging = false;
      }
      if (e.button === 2) this.setZoom(false);
    });
    window.addEventListener("wheel", (e) => {
      if (!this.orbitMode) return;
      this.orbitDist = Math.max(1.8, Math.min(9.5, this.orbitDist + e.deltaY * 0.004));
    }, { passive: true });
    this.domElement.addEventListener("contextmenu", (e) => e.preventDefault());
  }

  toggleOrbitMode(targetPos = null) {
    this.orbitMode = !this.orbitMode;
    if (this.orbitMode) {
      document.exitPointerLock?.();
      if (targetPos) {
        this.orbitTarget.copy(targetPos);
      } else {
        const fwd = new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
        this.orbitTarget.copy(this.position).add(new THREE.Vector3(0, 1.3, 0)).addScaledVector(fwd, 3.2);
      }
      this.orbitYaw = this.yaw;
      this.orbitPitch = 0.2;
      this.orbitDist = 3.8;
    } else {
      this.orbitDragging = false;
      this.syncCamera();
    }
    return this.orbitMode;
  }

  setZoom(active) {
    this.zoomed = active;
    this.camera.fov = active ? 28 : 65;
    this.camera.updateProjectionMatrix();
  }

  teleport(x, y, z, yaw = Math.PI * 0.5) {
    this.position.set(x, y, z);
    this.yaw = yaw;
    this.pitch = 0;
    this.velY = 0;
    this.onGround = true;
    this.syncCamera();
  }

  getGroundHeight(x, z, currentY) {
    let bestY = 0;
    for (const s of this.walkableSurfaces) {
      if (x >= s.minX && x <= s.maxX && z >= s.minZ && z <= s.maxZ) {
        if (s.y <= currentY + 1.25 && s.y > bestY) {
          bestY = s.y;
        }
      }
    }
    // Check smooth stair ramps
    for (const r of this.stairRamps) {
      const rx = x - r.x0;
      const rz = z - r.z0;
      const along = rx * r.dirX + rz * r.dirZ;
      const perp = Math.abs(rx * -r.dirZ + rz * r.dirX);
      if (along >= -0.6 && along <= r.runLen + 0.6 && perp <= r.halfW) {
        const t = Math.max(0, Math.min(1, along / r.runLen));
        const ry = r.startY + t * (r.endY - r.startY);
        if (ry <= currentY + 1.35 && ry > bestY) {
          bestY = ry;
        }
      }
    }
    return bestY;
  }

  collidesAt(x, y, z) {
    const r = this.radius;
    const pMinY = y + 0.35; // Step-up tolerance
    const pMaxY = y + this.eyeHeight;
    for (const c of this.colliders) {
      if (pMaxY <= c.minY || pMinY >= c.maxY) continue;
      if (x + r > c.minX && x - r < c.maxX && z + r > c.minZ && z - r < c.maxZ) {
        return true;
      }
    }
    return false;
  }

  update(dt) {
    if (this.paused) return;
    const clampedDt = Math.min(dt, 0.05);

    if (this.orbitMode) {
      if (this.keys.has("KeyA") || this.keys.has("ArrowLeft")) this.orbitYaw += 1.6 * clampedDt;
      if (this.keys.has("KeyD") || this.keys.has("ArrowRight")) this.orbitYaw -= 1.6 * clampedDt;
      if (this.keys.has("KeyW") || this.keys.has("ArrowUp")) this.orbitDist = Math.max(1.8, this.orbitDist - 2.5 * clampedDt);
      if (this.keys.has("KeyS") || this.keys.has("ArrowDown")) this.orbitDist = Math.min(9.5, this.orbitDist + 2.5 * clampedDt);
      const cx = this.orbitTarget.x + Math.sin(this.orbitYaw) * Math.cos(this.orbitPitch) * this.orbitDist;
      const cy = this.orbitTarget.y + Math.sin(this.orbitPitch) * this.orbitDist;
      const cz = this.orbitTarget.z + Math.cos(this.orbitYaw) * Math.cos(this.orbitPitch) * this.orbitDist;
      this.camera.position.set(cx, cy, cz);
      this.camera.lookAt(this.orbitTarget);
      return;
    }

    if (this.keys.has("ArrowLeft")) this.yaw += 1.8 * clampedDt;
    if (this.keys.has("ArrowRight")) this.yaw -= 1.8 * clampedDt;
    if (this.keys.has("ArrowUp")) this.pitch = Math.min(1.38, this.pitch + 1.3 * clampedDt);
    if (this.keys.has("ArrowDown")) this.pitch = Math.max(-1.38, this.pitch - 1.3 * clampedDt);

    const forward = new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
    const right = new THREE.Vector3(Math.cos(this.yaw), 0, -Math.sin(this.yaw));

    let moveX = 0;
    let moveZ = 0;
    if (this.keys.has("KeyW")) { moveX += forward.x; moveZ += forward.z; }
    if (this.keys.has("KeyS")) { moveX -= forward.x; moveZ -= forward.z; }
    if (this.keys.has("KeyD")) { moveX += right.x; moveZ += right.z; }
    if (this.keys.has("KeyA")) { moveX -= right.x; moveZ -= right.z; }

    const len = Math.hypot(moveX, moveZ);
    const running = this.keys.has("ShiftLeft") || this.keys.has("ShiftRight");
    const speed = running ? 11.5 : 5.4;

    if (len > 0.001) {
      moveX = (moveX / len) * speed * clampedDt;
      moveZ = (moveZ / len) * speed * clampedDt;

      // Axis-separated sliding collision
      if (!this.collidesAt(this.position.x + moveX, this.position.y, this.position.z)) {
        this.position.x += moveX;
      }
      if (!this.collidesAt(this.position.x, this.position.y, this.position.z + moveZ)) {
        this.position.z += moveZ;
      }

      if (this.onGround) {
        this.stepTimer += clampedDt * (running ? 2.4 : 1.5);
        if (this.stepTimer >= 0.65) {
          this.stepTimer = 0;
          this.onStep?.();
        }
      }
    }

    // Jump & Gravity
    if (this.keys.has("Space") && this.onGround) {
      this.velY = 6.2;
      this.onGround = false;
    }
    this.velY -= 18.0 * clampedDt;
    this.position.y += this.velY * clampedDt;

    const groundY = this.getGroundHeight(this.position.x, this.position.z, this.position.y);
    if (this.position.y <= groundY) {
      this.position.y = groundY;
      this.velY = 0;
      this.onGround = true;
    } else {
      this.onGround = false;
    }

    // Keep within outer park bounds
    this.position.x = Math.max(-245, Math.min(245, this.position.x));
    this.position.z = Math.max(-245, Math.min(245, this.position.z));

    this.syncCamera();
  }

  syncCamera() {
    this.camera.position.set(this.position.x, this.position.y + this.eyeHeight, this.position.z);
    this.camera.rotation.order = "YXZ";
    this.camera.rotation.y = this.yaw;
    this.camera.rotation.x = this.pitch;
  }
}
