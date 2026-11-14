/**
 * Historically verified architectural & epigraphic data for Angkor Wat (Paramavishnuloka).
 * Sources: UNESCO World Heritage Centre (ID 668), APSARA National Authority,
 * George Coedès (Inscriptions du Cambodge), and Rigveda Samhita I.154.
 */

export const SPAWN_POINTS = [
  {
    id: 'causeway',
    name: '1. Western Causeway Approach',
    desc: 'Cross the 70m sandstone causeway over the outer moat.',
    pos: [-222, 1.8, 0],
    yaw: -Math.PI / 2 // Facing +X (East)
  },
  {
    id: 'avenue',
    name: '2. Processional Avenue',
    desc: 'Walk past the Outer Gopura toward the twin Libraries & Pools.',
    pos: [-126, 2.6, 0],
    yaw: -Math.PI / 2
  },
  {
    id: 'pools',
    name: '3. Reflection Pools & Stela',
    desc: 'Classic view of the five quincunx towers reflected in the northern basin.',
    pos: [-58, 2.0, -10],
    yaw: -Math.PI * 0.42
  },
  {
    id: 'samudra',
    name: '4. Gallery: Samudra Manthana',
    desc: 'First Enclosure East-South gallery with the Churning of the Ocean of Milk.',
    pos: [74.2, 2.5, 16],
    yaw: 0 // Facing -Z (North)
  },
  {
    id: 'enc2',
    name: '5. Second Enclosure Terrace',
    desc: 'Elevated Devata & Apsara terrace surrounding the central pyramid.',
    pos: [2, 5.4, 0],
    yaw: -Math.PI / 2
  },
  {
    id: 'sanctum',
    name: '6. Bakan Summit & Garbhagriha',
    desc: 'Mount Meru upper terrace before the sanctuary of Chaturbhuja Lord Vishnu.',
    pos: [9.5, 15.4, 0],
    yaw: -Math.PI / 2
  }
];

export const HISTORICAL_HOTSPOTS = [
  {
    id: 'vishnu-murti',
    title: 'Chaturbhuja Lord Vishnu & Urdhvapundra',
    category: 'Central Sanctum (Garbhagriha)',
    sanskrit: 'Oṃ Namo Bhagavate Vāsudevāya • Viṣṇu Caturbhuja',
    pos: [19.8, 15.2, 0],
    radius: 5.5,
    context: 'Constructed under King Suryavarman II (r. 1113–1150 CE), Angkor Wat was originally consecrated as a state Vaishnava temple (Paramavishnuloka). The central sanctum (Garbhagriha) beneath Prasat Thom housed a monolithic four-armed image of Lord Vishnu.',
    significance: 'The deity holds the four canonical emblems: Panchajanya Shankha (conch, cosmic sound), Sudarshana Chakra (discus, cosmic order), Kaumodaki Gada (mace, primordial force), and Padma (lotus, purity), wearing the Vaishnava Urdhvapundra tilaka.',
    evidence: 'Documented Evidence: Epigraphic records (K. 300, K. 298) and the 12th-century pedestal socket in the central sanctuary confirm original Vishnu worship before later 14th–16th century Theravada Buddhist conversion. Reconstruction Note: The 3D statue is an iconographic reconstruction based on Khmer Angkor Wat-style Vishnu sculptures (e.g., National Museum of Cambodia).',
    source: 'UNESCO World Heritage Centre (Ref. 668) • APSARA National Authority'
  },
  {
    id: 'samudra-manthana',
    title: 'Samudra Manthana (Churning of the Ocean of Milk)',
    category: 'East-South Bas-Relief Gallery',
    sanskrit: 'Samudra Manthana • Kūrma Avatāra',
    pos: [74.2, 2.5, 24],
    radius: 7.0,
    context: 'Spanning 49 meters along the southern half of the East Gallery (First Enclosure), this is one of Angkor Wat’s most celebrated narrative reliefs from the Bhagavata Purana and Mahabharata.',
    significance: 'Depicts 88 Devas (gods) on the north and 92 Asuras (demons) on the south pulling the serpent Vasuki wrapped around Mount Mandara, stabilized by Vishnu in his tortoise Kurma Avatar, to churn the elixir of immortality (Amrita).',
    evidence: 'Documented Evidence: Carved in situ in 12th-century fine-grained sandstone under Suryavarman II, with subtle traces of laterite/lacquer patina documented by APSARA conservation teams.',
    source: 'APSARA National Authority • Bhagavata Purana VIII.6–8'
  },
  {
    id: 'kurukshetra',
    title: 'Battle of Kurukshetra (Mahabharata)',
    category: 'West-South Bas-Relief Gallery',
    sanskrit: 'Mahābhārata • Kurukṣetra Yuddha',
    pos: [-34.2, 2.5, 24],
    radius: 7.0,
    context: 'Located in the southern wing of the West Gallery, this 49-meter frieze illustrates the climactic 18-day war between the Pandavas and Kauravas from the Sanskrit epic Mahabharata.',
    significance: 'Commanders ride spoked war chariots under royal parasols (chattra) flanked by war elephants and infantry. Highlights the moral and cosmic duty (Dharma) taught in the Bhagavad Gita.',
    evidence: 'Documented Evidence: In situ 12th-century relief panels; Old Khmer and Sanskrit epigraphic captions identify key heroes including Bhishma, Arjuna, and Krishna.',
    source: 'UNESCO World Heritage Centre • George Coedès, Inscriptions du Cambodge'
  },
  {
    id: 'battle-of-lanka',
    title: 'Battle of Lanka (Ramayana)',
    category: 'West-North Bas-Relief Gallery',
    sanskrit: 'Rāmāyaṇa • Laṅkā Yuddha',
    pos: [-34.2, 2.5, -24],
    radius: 7.0,
    context: 'Occupying the northern half of the West Gallery, this dynamic frieze portrays the siege of Lanka from Valmiki’s Ramayana.',
    significance: 'Lord Rama (an avatar of Vishnu) and Lakshmana draw their bows alongside Hanuman and the leaping Vanara (monkey) army clashing against the ten-headed king Ravana.',
    evidence: 'Documented Evidence: Original 12th-century Khmer sandstone carving; the fluid overlapping figures demonstrate the pinnacle of Angkor Wat’s classical relief style.',
    source: 'APSARA National Authority • Valmiki Ramayana (Yuddha Kanda)'
  },
  {
    id: 'suryavarman-procession',
    title: 'Procession of King Suryavarman II',
    category: 'South-West Bas-Relief Gallery',
    sanskrit: 'Paramaviṣṇuloka • Sūryavarman II (1113–1150 CE)',
    pos: [-8, 2.5, 47.2],
    radius: 7.0,
    context: 'The western half of the South Gallery is unique at Angkor Wat for depicting historical—rather than purely mythological—events: King Suryavarman II holding court and leading his royal army.',
    significance: 'The king is seated on Mount Sivapada beneath 15 tiered royal parasols, accompanied by court ministers, Brahmin priests carrying the sacred fire, and regiments of Khmer & allied troops.',
    evidence: 'Documented Evidence: Short Old Khmer inscriptions carved directly beside the figures identify Suryavarman II (posthumously Paramavishnuloka) and specific generals.',
    source: 'EFEO / George Coedès • APSARA National Authority'
  },
  {
    id: 'royal-stela',
    title: 'Royal Sanskrit Inscription Stela (Rigveda I.154)',
    category: 'Processional Avenue Landing',
    sanskrit: 'Viṣṇor nu kaṃ vīryāṇi pra vocam (RV I.154.1)',
    pos: [-40, 2.5, -4.5],
    radius: 5.5,
    context: 'Freestanding sandstone stelae in Angkorian temples recorded royal decrees, lineages, and Vedic hymns praising the presiding deity in classical Sanskrit kavya meter.',
    significance: 'Features the verified Vedic hymn Rigveda I.154.1–2 ("I will proclaim the mighty deeds of Vishnu, who measured out the earthly regions and established the highest abode in three strides").',
    evidence: 'Documented Evidence: Rigveda I.154.1–2 is an authentic Vedic Sanskrit text; Khmer epigraphy (e.g., Preah Khan & Angkor Wat stelae) frequently invokes Vishnu’s three strides (Trivikrama). Placement here is an interpretive educational exhibit.',
    source: 'Rigveda Samhita I.154 • Corpus Inscriptionum Indicarum / Coedès'
  },
  {
    id: 'naga-balustrade',
    title: 'Sheshanaga Balustrades & Western Causeway',
    category: 'Outer Moat & Causeway',
    sanskrit: 'Śeṣanāga • Setu (Sacred Rainbow Bridge)',
    pos: [-175, 2.0, -4.1],
    radius: 6.5,
    context: 'A 70-meter elevated sandstone causeway spans the vast rectangular moat (historically 190m wide), flanked by sculpted seven-headed Naga serpents.',
    significance: 'In Khmer cosmology, the Naga balustrade acts as a cosmic rainbow bridge linking the mundane human world to the divine abode of Mount Meru inside the enclosure.',
    evidence: 'Documented Evidence: Original 12th-century sandstone paving and Naga hood finials preserved along the western approach; moat water symbolizes the primordial cosmic ocean.',
    source: 'UNESCO World Heritage Centre • APSARA National Authority'
  },
  {
    id: 'devata-apsara',
    title: 'Devata & Apsara Sculptures',
    category: 'Second Enclosure Terrace',
    sanskrit: 'Devatā • Apsaras',
    pos: [-4.2, 5.3, 14],
    radius: 6.0,
    context: 'Over 1,700 celestial female figures (Devatas) are carved in high relief across the walls, pillars, and niches of Angkor Wat’s galleries and towers.',
    significance: 'No two Devatas are identical; each displays distinct mukuta headdresses, floral ornaments, and hand mudras, symbolizing the auspicious abundance of Vishnu’s celestial paradise.',
    evidence: 'Documented Evidence: Cataloged extensively by the German Apsara Conservation Project (GACP) and APSARA National Authority.',
    source: 'APSARA National Authority • GACP'
  },
  {
    id: 'preah-poan',
    title: 'Preah Poan (Cruciform Cloister)',
    category: 'Inner Courtyard Axis',
    sanskrit: 'Bhadra-maṇḍapa • Ritual Ablution Basins',
    pos: [-20, 2.5, 0],
    radius: 6.0,
    context: 'Connecting the First and Second Enclosures along the western axis, this cruciform pillared gallery forms four sunken square courtyards.',
    significance: 'Originally served as a ritual purification space filled with water before devotees ascended the steep stairs of the Second Enclosure and the Bakan.',
    evidence: 'Documented Evidence: Architectural drainage channels and stepped stone basins are preserved in situ; the name "Preah Poan" (Hall of a Thousand Buddhas) dates to the later Theravada period.',
    source: 'APSARA National Authority • Jacques Dumarçay'
  }
];
