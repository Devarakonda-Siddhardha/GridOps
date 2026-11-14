# Angkor Wat (Paramavishnuloka) — Immersive 3D Temple Experience

An explorable, historically informed 3D reconstruction of **Angkor Wat** (12th-century Cambodia, consecrated under King Suryavarman II and dedicated to Lord Vishnu), built with **Blender 3.6 LTS** and **Three.js**.

## Live Browser Experience

- **First-Person Walkable Explorer:** `explore.html` (or on GitHub Pages: `https://devarakonda-siddhardha.github.io/GridOps/explore.html`)
- **Architectural Showcase & Orbit Viewer:** `index.html` (`https://devarakonda-siddhardha.github.io/GridOps/`)

---

## How to Open & Explore Locally (Windows / macOS / Linux)

Because modern browsers block ES module and `.glb` loading over `file://`, serve the repository with any lightweight local HTTP server:

### Option 1: Python (Recommended on Windows)
```powershell
cd GridOps
python -m http.server 8080
```
Then open **http://localhost:8080/explore.html** in Chrome, Edge, or Firefox.

### Option 2: Node.js
```powershell
npx serve -l 8080 .
```
Then open **http://localhost:8080/explore.html**.

---

## First-Person Exploration Controls

| Key / Input | Action |
|---|---|
| **Click "Enter Temple"** | Lock mouse cursor for 360° first-person look |
| **W A S D / Arrow Keys** | Walk across causeways, galleries, and stairs |
| **Shift** | Sprint |
| **Space** | Jump |
| **E** | Inspect nearby historical plaque / carving |
| **1 – 6** or **Warp Menu** | Quick-warp to Causeway, Avenue, Pools, Galleries, Enc. 2, or Bakan Summit |
| **M** | Toggle procedural Cambodian dawn ambience (wind, water, birdsong) |
| **ESC** | Pause / unlock mouse cursor |

---

## Architectural & Historical Highlights

1. **4-Sided Moat & Western Causeway:** Elevated sandstone bridge flanked by seven-headed *Sheshanaga* balustrades leading through the walkable Western Outer Gopura.
2. **Processional Avenue, Twin Libraries & Reflection Pools:** Framing the classic western silhouette of the five quincunx towers.
3. **First Enclosure Bas-Relief Galleries:**
   - **East-South Gallery:** *Samudra Manthana* (Churning of the Ocean of Milk)
   - **West-South Gallery:** *Battle of Kurukshetra* (Mahabharata)
   - **West-North Gallery:** *Battle of Lanka* (Ramayana)
   - **South-West Gallery:** *Procession of King Suryavarman II*
4. **Preah Poan Cruciform Cloister & Second Enclosure:** Elevated Devata & Apsara terrace.
5. **The Bakan (Mount Meru) & Central Garbhagriha:** Five lotus-bud *prasat* towers in quincunx arrangement housing the consecrated four-armed *Chaturbhuja* Lord Vishnu (*Shankha, Chakra, Gada, Padma*, and *Urdhvapundra* tilaka).

All historical plaques distinguish **Documented Evidence** (UNESCO World Heritage Centre Ref. 668, APSARA National Authority, George Coedès' *Inscriptions du Cambodge*, Rigveda I.154) from **Architectural & Iconographic Reconstructions**.

---

## Project Structure

- `explore.html` — First-person 3D exploration HUD & viewport
- `index.html` — Overview showcase & Cycles render gallery
- `js/angkor-explorer.js` — Three.js engine, spatial-grid collision, stair climbing, sunrise atmosphere
- `js/angkor-data.js` — Verified historical hotspot metadata & spawn points
- `js/angkor-audio.js` — Procedural Web Audio API wind, water, and birdsong ambience
- `blender_scripts/generate_angkor_wat.py` — Procedural Blender 3.6 LTS generator & GLB exporter
- `blender_scripts/generate_angkor_textures.py` — Sandstone, laterite, inscription, and Samudra Manthana texture generator
- `blender_scripts/generate_stage2_reliefs.py` — Kurukshetra, Battle of Lanka, and Suryavarman II bas-relief generator
- `assets/models/angkor_wat_complete.glb` — Exported game-ready 3D temple (~95k polygons)

### Regenerating the 3D Model in Blender
```bash
python3 blender_scripts/generate_angkor_textures.py
python3 blender_scripts/generate_stage2_reliefs.py
blender -b --python blender_scripts/generate_angkor_wat.py
```
