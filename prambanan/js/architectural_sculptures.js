/**
 * Architectural & Iconographic Audit Extensions (Three.js)
 * Adds ONLY missing documented components without altering existing architecture:
 * 1. Nandisvara & Mahakala guardian statues flanking Candi Shiva's East entrance
 * 2. 24 Exterior Wall Relief Positions on Candi Shiva (8 paired Ashtadikpalas + 8 interposed figures)
 * 3. Brahma Surrounded by Maharishis relief on Candi Brahma
 * 4. Prambanan Motif (Lion in niche flanked by Kalpataru trees) architectural ornaments
 */
import * as THREE from "three";

const ASHTADIKPALA_24_PLAN = [
  // East Wall (facing +X)
  { wall: "E", offset: -7.6, name: "Indra (East Guardian — Position 1)", sanskrit: "Indra", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Lord of the East and Heaven; holds vajra thunderbolt. Paired representation flanking the eastern portal." },
  { wall: "E", offset: -5.4, name: "Interposed Figure: Brihaspati (?)", sanskrit: "Bṛhaspati (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Bearded preceptor-like figure interposed between Dikpālas. Identified by some scholars as Bṛhaspati; identity remains debated." },
  { wall: "E", offset: -3.4, name: "Indra (East Guardian — Position 2)", sanskrit: "Indra", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Indra on the eastern facade, accompanied by royal attendants." },
  { wall: "E", offset: 3.4, name: "Agni (Southeast Guardian — Position 1)", sanskrit: "Agni", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Lord of Fire and the Southeast; depicted with flame aureole / rosary and water pot." },
  { wall: "E", offset: 5.4, name: "Interposed Figure: Surya (?)", sanskrit: "Sūrya (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Solar-attributed interposed figure holding lotus buds. Proposed as Sūrya by Jordaan / Sundberg; not conclusively established." },
  { wall: "E", offset: 7.6, name: "Agni (Southeast Guardian — Position 2)", sanskrit: "Agni", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Agni toward the southeast corner." },

  // South Wall (facing +Z)
  { wall: "S", offset: 7.6, name: "Yama (South Guardian — Position 1)", sanskrit: "Yama", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Lord of Dharma and Death guarding the South; holds daṇḍa (staff/club)." },
  { wall: "S", offset: 5.4, name: "Interposed Figure: Karttikeya (?)", sanskrit: "Kārttikeya / Skanda (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Youthful warrior figure interposed on the south wall; tentatively linked to Kārttikeya." },
  { wall: "S", offset: 3.4, name: "Yama (South Guardian — Position 2)", sanskrit: "Yama", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Yama flanking the southern Agastya chamber." },
  { wall: "S", offset: -3.4, name: "Nairrita (Southwest Guardian — Position 1)", sanskrit: "Nairṛta", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Guardian of the Southwest; depicted with sword/shield and fierce aspect." },
  { wall: "S", offset: -5.4, name: "Interposed Figure: Hanuman (?)", sanskrit: "Hanumān (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Simian-featured or ascetic-warrior relief; proposed as Hanumān or a Shaiva attendant in scholarly literature." },
  { wall: "S", offset: -7.6, name: "Nairrita (Southwest Guardian — Position 2)", sanskrit: "Nairṛta", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Nairṛta toward the southwest corner." },

  // West Wall (facing -X)
  { wall: "W", offset: 7.6, name: "Varuna (West Guardian — Position 1)", sanskrit: "Varuṇa", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Lord of the Waters and the West; holds pāśa (noose) and makara/serpent motif." },
  { wall: "W", offset: 5.4, name: "Interposed Figure: Kama (?)", sanskrit: "Kāma (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Graceful figure with floral bow-like attributes; tentatively proposed as Kāma." },
  { wall: "W", offset: 3.4, name: "Varuna (West Guardian — Position 2)", sanskrit: "Varuṇa", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Varuṇa flanking the western Ganesha chamber." },
  { wall: "W", offset: -3.4, name: "Vayu (Northwest Guardian — Position 1)", sanskrit: "Vāyu", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Lord of the Wind and the Northwest; holds fluttering banner/scarf." },
  { wall: "W", offset: -5.4, name: "Interposed Figure: Vishvakarman (?)", sanskrit: "Viśvakarman (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Interposed divine figure with artisan/ritual attributes; proposed as Viśvakarman (disputed)." },
  { wall: "W", offset: -7.6, name: "Vayu (Northwest Guardian — Position 2)", sanskrit: "Vāyu", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Vāyu toward the northwest corner." },

  // North Wall (facing -Z)
  { wall: "N", offset: -7.6, name: "Kubera (North Guardian — Position 1)", sanskrit: "Kubera", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Lord of Wealth and the North; holds money-bag (nakulī) / lotus." },
  { wall: "N", offset: -5.4, name: "Interposed Figure: Narada (?)", sanskrit: "Nārada (Disputed)", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Sage-like interposed relief; tentatively identified as Nārada by some researchers." },
  { wall: "N", offset: -3.4, name: "Kubera (North Guardian — Position 2)", sanskrit: "Kubera", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Kubera flanking the northern Durga chamber." },
  { wall: "N", offset: 3.4, name: "Ishana (Northeast Guardian — Position 1)", sanskrit: "Īśāna", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Shaiva aspect guarding the Northeast; holds triśūla trident." },
  { wall: "N", offset: 5.4, name: "Interposed Figure: Unresolved Deity (?)", sanskrit: "Disputed Ascetic / Deva", category: "Directional guardians", status: "UNCERTAIN / SCHOLARLY HYPOTHESIS", disputed: true, desc: "Eighth interposed relief; scholarly consensus has not settled on a single identification." },
  { wall: "N", offset: 7.6, name: "Ishana (Northeast Guardian — Position 2)", sanskrit: "Īśāna", category: "Directional guardians", status: "VERIFIED IN-SITU (PAIRED DIKPALA)", disputed: false, desc: "Second paired representation of Īśāna toward the northeast corner." },
];

function makeInteractable(group, meta) {
  group.userData.interactable = meta;
  group.traverse((c) => {
    if (c.isMesh) c.userData.interactable = meta;
  });
}

function buildDvarapala(pos, rotY, isMahakala, mat, interactables, colliders) {
  const g = new THREE.Group();
  g.position.set(pos[0], pos[1], pos[2]);
  g.rotation.y = rotY;

  // Pedestal
  const ped = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.55, 1.15), mat);
  ped.position.y = 0.275;
  ped.castShadow = true;
  ped.receiveShadow = true;
  g.add(ped);

  // Standing figure
  const legs = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.28, 0.95, 10), mat);
  legs.position.y = 1.02;
  const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.23, 0.72, 10), mat);
  torso.position.y = 1.85;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 10), mat);
  head.position.y = 2.38;
  const crown = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.36, 8), mat);
  crown.position.y = 2.68;
  const halo = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.1, 14), mat);
  halo.rotation.x = Math.PI / 2;
  halo.position.set(0, 2.32, -0.2);
  g.add(legs, torso, head, crown, halo);

  // Weapon: Mahakala holds club (gada), Nandisvara holds trident (trishula)
  const weapon = new THREE.Mesh(
    isMahakala ? new THREE.CylinderGeometry(0.08, 0.05, 1.35, 8) : new THREE.CylinderGeometry(0.03, 0.03, 1.55, 8),
    mat
  );
  weapon.position.set(0.36, 1.55, 0.18);
  g.add(weapon);
  if (!isMahakala) {
    const prong = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.18, 0.04), mat);
    prong.position.set(0.36, 2.35, 0.18);
    g.add(prong);
  }

  const name = isMahakala ? "Mahakala Guardian" : "Nandisvara Guardian";
  const sanskrit = isMahakala ? "Mahākāla (Shaiva Dvārapāla)" : "Nandīśvara (Shaiva Dvārapāla)";
  makeInteractable(g, {
    type: "relief",
    id: isMahakala ? "SCULP_MAHAKALA" : "SCULP_NANDISVARA",
    label: `Inspect ${name}`,
    panelData: {
      name,
      sanskrit,
      category: "Shiva — Inner Court Entrance Guardians",
      evidenceStatus: "VERIFIED / RECONSTRUCTED GUARDIAN SHRINE",
      background: isMahakala
        ? "Mahākāla stands on the south flank of Candi Shiva's eastern approach, embodying fierce protection of the sanctum threshold."
        : "Nandīśvara stands on the north flank of Candi Shiva's eastern approach, paired with Mahākāla as peaceful/devotional guardian.",
      iconography: isMahakala
        ? "Stout standing dvārapāla with fierce expression, club (gadā), jaṭāmakuṭa headdress, and prabhāmaṇḍala backplate."
        : "Standing Shaiva guardian holding triśūla trident and akṣamālā, with ornate Central Javanese jewelry.",
      archaeology: "Flanks the eastern stair of Candi Shiva between the central court and Candi Nandi.",
      sources: "Roy E. Jordaan (1996), In Praise of Prambanan; Kemendikbudristek.",
    },
  });

  colliders.push({
    minX: pos[0] - 0.65,
    maxX: pos[0] + 0.65,
    minZ: pos[2] - 0.65,
    maxZ: pos[2] + 0.65,
    minY: pos[1],
    maxY: pos[1] + 2.9,
  });

  interactables.push(g);
  return g;
}

export function buildArchitecturalSculptures(scene, mats, interactables, colliders) {
  const group = new THREE.Group();
  group.name = "AUDIT_ARCHITECTURAL_SCULPTURES";
  scene.add(group);

  // 1. Nandisvara (North flank) & Mahakala (South flank) at Candi Shiva's East approach
  group.add(buildDvarapala([-0.5, 3.5, -4.2], Math.PI * 0.5, false, mats.andesiteCarved, interactables, colliders));
  group.add(buildDvarapala([-0.5, 3.5, 4.2], Math.PI * 0.5, true, mats.andesiteCarved, interactables, colliders));

  // 2. 24 Exterior Wall Relief Positions around Candi Shiva's body (cx=-18, cz=0, galY=11.02, bodyHalf=9.52)
  const shivaCX = -18;
  const shivaGalY = 11.02;
  const bodyHalf = 9.52;

  ASHTADIKPALA_24_PLAN.forEach((item, idx) => {
    const niche = new THREE.Group();
    let px = shivaCX, pz = 0, rotY = 0;
    if (item.wall === "E") { px = shivaCX + bodyHalf + 0.08; pz = item.offset; rotY = Math.PI * 0.5; }
    else if (item.wall === "W") { px = shivaCX - bodyHalf - 0.08; pz = item.offset; rotY = -Math.PI * 0.5; }
    else if (item.wall === "S") { px = shivaCX + item.offset; pz = bodyHalf + 0.08; rotY = 0; }
    else { px = shivaCX + item.offset; pz = -bodyHalf - 0.08; rotY = Math.PI; }

    niche.position.set(px, shivaGalY + 1.95, pz);
    niche.rotation.y = rotY;

    // Carved niche frame (darker recessed stone) & central deity relief figure (lighter carved andesite)
    const frame = new THREE.Mesh(new THREE.BoxGeometry(1.18, 1.75, 0.14), mats.andesiteWeathered);
    frame.receiveShadow = true;
    const fig = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.24, 1.05, 8), mats.andesiteCarved);
    fig.position.set(0, -0.1, 0.14);
    fig.castShadow = true;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.14, 10, 8), mats.andesiteCarved);
    head.position.set(0, 0.52, 0.14);
    head.castShadow = true;
    const halo = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.06, 12), mats.andesiteCarved);
    halo.rotation.x = Math.PI / 2;
    halo.position.set(0, 0.45, 0.09);
    niche.add(frame, fig, head, halo);

    makeInteractable(niche, {
      type: "relief",
      id: `DIKPALA_${idx + 1}`,
      label: `Inspect Relief ${idx + 1}/24: ${item.name}`,
      panelData: {
        name: `Candi Shiva Exterior Relief #${idx + 1}: ${item.name}`,
        sanskrit: item.sanskrit,
        category: "Candi Shiva — 24 Exterior Wall Guardians",
        evidenceStatus: item.status,
        background: item.desc,
        iconography: item.disputed
          ? "Preserved carved figure in niche; iconographic attribution remains debated among epigraphists and art historians."
          : "Classical Central Javanese directional guardian (Aṣṭadikpāla) in paired architectural placement.",
        archaeology: `Located on the ${item.wall} exterior body wall of Candi Shiva along the pradakṣiṇapatha gallery.`,
        sources: "Roy E. Jordaan (1996), In Praise of Prambanan; Jeffrey Sundberg.",
      },
    });

    interactables.push(niche);
    group.add(niche);
  });

  // 3. Brahma Surrounded by Maharishis Relief (on Candi Brahma East-side body wall, cx=-18, cz=32, galY=8.78)
  const brahmaRelief = new THREE.Group();
  brahmaRelief.position.set(-18 + 5.65, 8.78 + 1.85, 32 - 3.3);
  brahmaRelief.rotation.y = Math.PI * 0.5;
  const brFrame = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.35, 0.18), mats.andesiteCarved);
  const brCenter = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.22, 0.78, 8), mats.andesiteCarved);
  brCenter.position.set(0, -0.05, 0.12);
  brahmaRelief.add(brFrame, brCenter);
  for (const sx of [-0.68, -0.36, 0.36, 0.68]) {
    const rishi = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 0.62, 7), mats.andesiteCarved);
    rishi.position.set(sx, -0.1, 0.10);
    brahmaRelief.add(rishi);
  }
  makeInteractable(brahmaRelief, {
    type: "relief",
    id: "REL_BRAHMA_MAHARISHI",
    label: "Inspect Brahma & Maharishis Relief",
    panelData: {
      name: "Brahma Surrounded by Maharishis",
      sanskrit: "Brahmā & Maharṣayaḥ",
      category: "Brahma — Exterior Iconography",
      evidenceStatus: "VERIFIED IN-SITU",
      background: "Seated four-headed Brahmā flanked by bearded Vedic sages (Maharṣis) holding ritual staffs/tridents.",
      iconography: "Highlights Brahmā's role as source of Vedic revelation rather than a standalone narrative episode.",
      archaeology: "Carved on Candi Brahma's exterior body wall.",
      sources: "Kemendikbudristek; Attached Reference Archive.",
    },
  });
  interactables.push(brahmaRelief);
  group.add(brahmaRelief);

  // 4. Prambanan Motif (Lion in Niche flanked by Kalpataru trees) on Candi Shiva lower plinth
  const motifCoords = [
    [-18 + 17.05, 3.5 + 2.2, -7.2, Math.PI * 0.5],
    [-18 + 17.05, 3.5 + 2.2, 7.2, Math.PI * 0.5],
    [-18 - 7.2, 3.5 + 2.2, 17.05, 0],
    [-18 + 7.2, 3.5 + 2.2, 17.05, 0],
  ];
  motifCoords.forEach(([mx, my, mz, ry], idx) => {
    const motif = new THREE.Group();
    motif.position.set(mx, my, mz);
    motif.rotation.y = ry;
    const panel = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.6, 0.18), mats.andesiteCarved);
    const lion = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.78, 0.22), mats.andesiteCarved);
    lion.position.set(0, -0.1, 0.1);
    const treeL = new THREE.Mesh(new THREE.ConeGeometry(0.32, 1.05, 6), mats.andesiteCarved);
    treeL.position.set(-0.78, 0, 0.1);
    const treeR = new THREE.Mesh(new THREE.ConeGeometry(0.32, 1.05, 6), mats.andesiteCarved);
    treeR.position.set(0.78, 0, 0.1);
    motif.add(panel, lion, treeL, treeR);
    makeInteractable(motif, {
      type: "relief",
      id: `ARCH_PRAMBANAN_MOTIF_${idx + 1}`,
      label: "Inspect Prambanan Motif (Architectural Ornament)",
      panelData: {
        name: "Prambanan Motif (Lion in Niche & Kalpataru)",
        sanskrit: "Siṃha & Kalpataru",
        category: "Architectural Sculpture (Ornamental — Not Worshipped Deity)",
        evidenceStatus: "VERIFIED ARCHITECTURAL GRAMMAR",
        background: "Characteristic Prambanan decorative triad: a seated lion inside a recessed niche flanked by wish-fulfilling Kalpataru trees and kinnara birds.",
        iconography: "Explicitly classified as structural architectural ornament rather than an object of cult worship.",
        archaeology: "Repeated rhythmically along the lower plinth walls of the Trimūrti temples.",
        sources: "UNESCO WHC #642; Kemendikbudristek.",
      },
    });
    interactables.push(motif);
    group.add(motif);
  });

  return group;
}
