/**
 * Candi Prambanan — Historical, Iconographic & Relief Narrative Database
 * Strictly distinguishes verified archaeological/epigraphic evidence from reconstruction.
 */

export const DEITIES_AND_STRUCTURES = {
  SHIVA_TEMPLE: {
    id: "SHIVA_TEMPLE",
    name: "Candi Shiva Mahadeva",
    sanskrit: "Śivagṛha (House of Śiva)",
    category: "Trimūrti Principal Temple (Central)",
    evidenceStatus: "VERIFIED ARCHAEOLOGICAL & EPIGRAPHIC",
    background:
      "Standing 47 metres tall on a 34×34 m cruciform base, Candi Shiva Mahadeva is the tallest and holiest monument of the 9th-century Prambanan complex. Linked to the Shivagrha inscription (856 CE), it was restored via anastylosis between 1918 and 1953.",
    iconography:
      "Designed as a cosmic Mount Meru in Central Javanese prasada style: a stepped bhūrloka plinth, a pradakṣiṇapatha circumambulatory gallery lined with 24 Ramayana panels, and a multi-tiered ratna-crowned superstructure.",
    archaeology:
      "Contains four cardinal chambers surrounding the central core: Shiva Mahadeva (East), Agastya (South), Ganesha (West), and Durga Mahishasuramardini (North). Two small guardian shrines (Mahakala and Nandisvara) flank the eastern approach.",
    sources: "UNESCO WHC #642; Shivagrha Inscription (856 CE, de Casparis 1956); Kemendikbudristek.",
  },
  SHIVA_MAHADEVA: {
    id: "SHIVA_MAHADEVA",
    name: "Shiva Mahadeva",
    sanskrit: "Śiva Mahādeva",
    category: "Principal Deity — East Main Sanctum",
    evidenceStatus: "VERIFIED IN-SITU SCULPTURE",
    background:
      "The 3-metre andesite statue of Shiva Mahadeva occupies the largest eastern chamber of the central temple. Some scholars (e.g., Stutterheim) have proposed it served as a royal deification portrait of a Mataram king (possibly Rakai Pikatan or Balitung).",
    iconography:
      "Four-armed Shiva standing on a lotus cushion atop a Yoni pedestal carved with Nāga serpents. He bears a jaṭāmakuṭa crown adorned with a crescent moon and skull (ardhacandrakapāla), a third eye on his forehead, and holds an akṣamālā (rosary) and cāmara (fly-whisk).",
    archaeology:
      "Original 9th-century Central Javanese sculpture in situ inside the eastern garbhagṛha.",
    sources: "Bernet Kempers (1959), Ancient Indonesian Art; Balai Pelestarian Kebudayaan Wilayah X.",
  },
  DURGA_MAHISHASURAMARDINI: {
    id: "DURGA_MAHISHASURAMARDINI",
    name: "Durga Mahishasuramardini",
    sanskrit: "Durgā Mahiṣāsuramardinī",
    category: "Shiva Temple — North Chamber",
    evidenceStatus: "VERIFIED IN-SITU SCULPTURE",
    background:
      "Occupying the northern sanctum of Candi Shiva, this masterpiece of Central Javanese sculpture is locally revered in Javanese folklore as Princess Rara Jonggrang (Lara Jonggrang).",
    iconography:
      "Eight-armed Goddess Durga stands triumphantly atop the buffalo Mahiṣa, seizing the hair of the demon Mahiṣāsura emerging from the slain beast while grasping the buffalo's tail. Her multiple arms wield divine weapons including cakra, śaṅkha, sword, shield, bow, and arrow.",
    archaeology:
      "Original 9th-century andesite sculpture in situ; exhibits the refined, serene yet dynamic Central Javanese classical style rather than later East Javanese or South Indian conventions.",
    sources: "UNESCO WHC #642; Kemendikbudristek Iconographic Inventory.",
  },
  GANESHA: {
    id: "GANESHA",
    name: "Ganesha",
    sanskrit: "Gaṇeśa (Vighneśvara)",
    category: "Shiva Temple — West Chamber",
    evidenceStatus: "VERIFIED IN-SITU SCULPTURE",
    background:
      "Son of Shiva and Parvati, Lord of Wisdom and Remover of Obstacles, enshrined in the western chamber of Candi Shiva.",
    iconography:
      "Four-armed, elephant-headed deity seated in mahārājalīlāsana upon a double lotus padmāsana throne. His trunk curves toward a bowl of sweets (modaka) held in his lower left hand; his upper hands hold an akṣamālā (rosary) and paraśu (axe).",
    archaeology:
      "Original 9th-century Central Javanese andesite statue in situ.",
    sources: "Bernet Kempers (1959); Balai Pelestarian Kebudayaan.",
  },
  AGASTYA: {
    id: "AGASTYA",
    name: "Agastya (Shiva Mahaguru)",
    sanskrit: "Agastya / Śiva Mahāguru",
    category: "Shiva Temple — South Chamber",
    evidenceStatus: "VERIFIED IN-SITU SCULPTURE",
    background:
      "In Central Javanese Shaiva temple iconography, the Vedic sage Agastya (revered as Śiva Mahāguru, the great teacher who spread Shaiva dharma southward) consistently occupies the southern sanctum.",
    iconography:
      "Depicted as a bearded, pot-bellied ascetic sage standing on a lotus pedestal, holding a kamaṇḍalu (water vessel) and akṣamālā, with a triśūla (trident) beside him.",
    archaeology:
      "Original 9th-century Central Javanese sculpture in situ in the southern chamber.",
    sources: "J.G. de Casparis; Dumarçay (1986), The Temples of Java.",
  },
  VISHNU_TEMPLE: {
    id: "VISHNU_TEMPLE",
    name: "Candi Vishnu & Sanctum",
    sanskrit: "Viṣṇu Prasāda",
    category: "Trimūrti Principal Temple (North)",
    evidenceStatus: "VERIFIED ARCHAEOLOGICAL STRUCTURE & STATUE",
    background:
      "Standing north of Candi Shiva (20×20 m base, 33 m tall), Candi Vishnu is dedicated to Vishnu, the Preserver of the cosmos in the Hindu Trimūrti.",
    iconography:
      "Single eastern-facing sanctum housing a ~3 m four-armed Vishnu holding his four classical attributes: śaṅkha (conch), cakra (discus), gadā (mace), and padma (lotus/earth). Its gallery balustrade features 30 Kṛṣṇāyana relief panels.",
    archaeology:
      "Restored structure with original in-situ 9th-century Vishnu statue.",
    sources: "UNESCO WHC #642; Kemendikbudristek.",
  },
  BRAHMA_TEMPLE: {
    id: "BRAHMA_TEMPLE",
    name: "Candi Brahma & Sanctum",
    sanskrit: "Brahmā Prasāda",
    category: "Trimūrti Principal Temple (South)",
    evidenceStatus: "VERIFIED ARCHAEOLOGICAL STRUCTURE & STATUE",
    background:
      "Standing south of Candi Shiva (20×20 m base, 33 m tall), Candi Brahma is dedicated to Brahma, the Creator in the Hindu Trimūrti.",
    iconography:
      "Single eastern-facing sanctum housing a ~3 m four-headed (Caturmukha), four-armed Brahma holding akṣamālā and kamaṇḍalu. Its gallery balustrade continues the Ramayana narrative (30 panels, following Shiva Panel 24).",
    archaeology:
      "Restored structure with original 9th-century four-headed Brahma statue in situ.",
    sources: "UNESCO WHC #642; Stutterheim (1925).",
  },
  NANDI_TEMPLE: {
    id: "NANDI_TEMPLE",
    name: "Candi Nandi (with Surya & Chandra)",
    sanskrit: "Nandi Vāhana",
    category: "Vāhana Temple (Opposite Shiva)",
    evidenceStatus: "VERIFIED IN-SITU SCULPTURES",
    background:
      "Directly opposite Candi Shiva and facing west toward the Great God, Candi Nandi (~15×15 m base, ~25 m tall) houses Shiva's sacred bull Nandi.",
    iconography:
      "Contains a ~3 m calm, recumbent andesite statue of Nandi, flanked by two celestial chariot deities: Sūrya (Sun god on a 7-horse chariot) and Candra (Moon god on a 10-horse chariot).",
    archaeology:
      "All three sculptures (Nandi, Surya, Chandra) survive in situ inside the restored shrine.",
    sources: "Kemendikbudristek; Bernet Kempers (1959).",
  },
  GARUDA_TEMPLE: {
    id: "GARUDA_TEMPLE",
    name: "Candi Garuda",
    sanskrit: "Garuḍa Vāhana",
    category: "Vāhana Temple (Opposite Vishnu)",
    evidenceStatus: "STRUCTURE VERIFIED / INTERIOR STATUE MISSING",
    background:
      "Facing west directly opposite Candi Vishnu, this shrine (~14×14 m base, ~22.5 m tall) was dedicated to Garuda, the mythic sun-bird mount of Vishnu.",
    iconography:
      "Historically intended to house a Garuda sculpture facing Vishnu's sanctum. In Present-Day View (Mode A), the chamber is authentically empty. In Historical Reconstruction (Mode B), a labeled [RECONSTRUCTED] pedestal marks its ritual focus.",
    archaeology:
      "No Garuda statue was recovered in situ during 20th-century excavations.",
    sources: "Balai Pelestarian Kebudayaan Wilayah X.",
  },
  HAMSA_TEMPLE: {
    id: "HAMSA_TEMPLE",
    name: "Candi Hamsa (Angsa)",
    sanskrit: "Haṃsa Vāhana",
    category: "Vāhana Temple (Opposite Brahma)",
    evidenceStatus: "STRUCTURE VERIFIED / INTERIOR STATUE MISSING",
    background:
      "Facing west directly opposite Candi Brahma, this shrine (~14×14 m base, ~22.5 m tall) was dedicated to Hamsa (Angsa), the sacred swan mount of Brahma.",
    iconography:
      "In Present-Day View (Mode A), the chamber is authentically empty. In Historical Reconstruction (Mode B), a labeled [RECONSTRUCTED] pedestal indicates the ritual placement.",
    archaeology:
      "No Hamsa statue survived in situ.",
    sources: "Balai Pelestarian Kebudayaan Wilayah X.",
  },
  APIT_TEMPLES: {
    id: "APIT_TEMPLES",
    name: "Candi Apit (North & South)",
    sanskrit: "Apit (Flanking Shrines)",
    category: "Inner Courtyard Subsidiary Shrines",
    evidenceStatus: "VERIFIED ARCHAEOLOGICAL STRUCTURES",
    background:
      "Two slender 14 m tall temples (6×6 m base) flanking the northern and southern ends of the central corridor between the Trimurti and Vahana rows.",
    iconography:
      "Their exact deity dedication is not confirmed by surviving inscriptions; scholars note their role in framing the sacred central plaza.",
    archaeology:
      "Both structures are restored and stand at the north and south ends of the inner plaza.",
    sources: "Dumarçay (1986).",
  },
  SHIVAGRHA_INSCRIPTION: {
    id: "SHIVAGRHA_INSCRIPTION",
    name: "Shivagrha Inscription Marker (856 CE)",
    sanskrit: "Śivagṛha Praśasti (778 Śaka)",
    category: "Epigraphic Historical Record",
    evidenceStatus: "VERIFIED EPIGRAPHIC SOURCE (Original in National Museum, Jakarta)",
    background:
      "Dated 778 Saka (856 CE) and issued by Dyah Lokapala (Rakai Kayuwangi), this Old Javanese metrical inscription records the consecration of a grand Shiva temple compound and the diversion of a river.",
    iconography:
      "Provides the foundational chronological and cosmological link between the Sanjaya dynasty of Mataram and Candi Prambanan.",
    archaeology:
      "The original inscribed andesite stele is preserved at the National Museum of Indonesia in Jakarta; this marker presents its historical context on site.",
    sources: "J.G. de Casparis (1956), Prasasti Indonesia II.",
  },
  PERWARA_TEMPLES: {
    id: "PERWARA_TEMPLES",
    name: "Candi Perwara (224 Guardian Shrines)",
    sanskrit: "Parivāra (Attendant Shrines)",
    category: "Middle Courtyard (Bhuvarloka)",
    evidenceStatus: "PRESENT-DAY RUINS (Mode A) / RECONSTRUCTED (Mode B)",
    background:
      "224 smaller shrines (6×6 m base, ~14 m tall) arranged in four concentric square rows of 44, 52, 60, and 68 temples surrounding the inner court, likely donated by regional lords and successive Mataram rulers.",
    iconography:
      "Each Perwara mirrors the stepped prasada form of the central temples, symbolizing the cosmic retinue around Mount Meru.",
    archaeology:
      "Only a handful of Perwara shrines have been reconstructed today; the vast majority remain ruined plinths or fallen andesite blocks (Mode A). Toggle Mode B to view the 9th-century historical reconstruction.",
    sources: "UNESCO WHC #642; Kemendikbudristek.",
  },
};

export const RAMAYANA_SHIVA_PANELS = [
  { id: "SHIVA_RAM_01", panel: 1, title: "Vishnu Enthroned on Garuda", sanskrit: "Viṣṇu-Garuḍa / Devatā Prārthanā", text: "The gods led by Brahma beseech Vishnu, seated atop Garuda above the ocean, to incarnate on Earth and defeat the demon king Ravana (Rahwana).", sig: "Establishes the divine cosmic cause of the Ramayana on the eastern gallery.", src: "Stutterheim (1925); Kemendikbudristek Panel 1" },
  { id: "SHIVA_RAM_02", panel: 2, title: "King Dasharatha's Sacrifice", sanskrit: "Putrakāmeṣṭi Yajña", text: "King Dasharatha of Ayodhya performs the sacred ritual; his queens conceive Rama, Bharata, Lakshmana, and Shatrughna.", sig: "Javanese courtly architecture frames the royal palace of Ayodhya.", src: "Stutterheim (1925); Panel 2" },
  { id: "SHIVA_RAM_03", panel: 3, title: "Vishvamitra's Request", sanskrit: "Viśvāmitra Āgamana", text: "Sage Vishvamitra arrives at Ayodhya and asks Dasharatha to send young Rama and Lakshmana to protect his hermitage from demons.", src: "Shows Javanese ascetic iconography.", src: "Panel 3" },
  { id: "SHIVA_RAM_04", panel: 4, title: "Slaying of Tataka", sanskrit: "Tāṭakā Vadha", text: "Rama draws his bow and slays the demoness Tataka in the forest while Lakshmana stands guard.", sig: "Early demonstration of Rama's martial dharma.", src: "Panel 4" },
  { id: "SHIVA_RAM_05", panel: 5, title: "Rama Breaks Shiva's Bow", sanskrit: "Śiva Dhanurbhaṅga", text: "At King Janaka's court in Mithila, Rama strings and breaks the mighty bow of Shiva, winning the hand of Princess Sita (Shinta).", sig: "Celebrated Javanese courtly wedding prelude.", src: "Panel 5" },
  { id: "SHIVA_RAM_06", panel: 6, title: "Parashurama's Challenge", sanskrit: "Paraśurāma Saṃvāda", text: "The warrior-sage Parashurama confronts Rama on the return journey and acknowledges Rama's supreme divinity.", sig: "Transitional narrative between Mithila and Ayodhya.", src: "Panel 6" },
  { id: "SHIVA_RAM_07", panel: 7, title: "Kaikeyi's Boon & Exile", sanskrit: "Rāma Vanavāsa", text: "Queen Kaikeyi demands Rama's 14-year exile and Bharata's coronation; Rama, Sita, and Lakshmana depart Ayodhya.", sig: "Expresses Javanese ideals of filial duty.", src: "Panel 7" },
  { id: "SHIVA_RAM_08", panel: 8, title: "Dasharatha's Grief & Bharata's Plea", sanskrit: "Bharata Milāpa", text: "Dasharatha passes away; Bharata visits Rama in the forest and receives Rama's royal sandals (pādukā) to rule as regent.", sig: "Sandals symbolize legitimate royal authority.", src: "Panel 8" },
  { id: "SHIVA_RAM_09", panel: 9, title: "Slaying of Viradha / Forest Rakshasa", sanskrit: "Virādha Vadha", text: "In the Dandaka forest, Rama pierces a monstrous rakshasa with his arrow as Lakshmana watches, releasing the cursed spirit.", sig: "Famous dynamic combat relief on the southern balustrade.", src: "YatrikaOne / Panel 9" },
  { id: "SHIVA_RAM_10", panel: 10, title: "Shurpanakha's Advance & Mutilation", sanskrit: "Śūrpaṇakhā Prasaṅga", text: "Ravana's sister Shurpanakha attempts to seduce Rama and Lakshmana and is repulsed.", sig: "Triggers Ravana's vengeful plot.", src: "Panel 10" },
  { id: "SHIVA_RAM_11", panel: 11, title: "The Golden Deer (Maricha)", sanskrit: "Mārīca Māyāmṛga", text: "Maricha transforms into a glittering golden deer to lure Rama away from the forest hermitage.", sig: "One of the most recognizable pastoral reliefs.", src: "Panel 11" },
  { id: "SHIVA_RAM_12", panel: 12, title: "Ravana Abducts Sita", sanskrit: "Sītā Haraṇa", text: "Disguised as an ascetic, Ravana seizes Sita and carries her skyward toward Lanka.", sig: "Pivotal dramatic turning point of the cycle.", src: "Panel 12" },
  { id: "SHIVA_RAM_13", panel: 13, title: "Jatayu Battles Ravana", sanskrit: "Jaṭāyu Yuddha", text: "The noble vulture Jatayu intercepts Ravana in mid-air, is mortally wounded, and later informs Rama before dying.", sig: "Depicts avian wing-detail in high relief.", src: "Panel 13" },
  { id: "SHIVA_RAM_14", panel: 14, title: "Slaying of Kabandha", sanskrit: "Kabandha Vadha", text: "Rama and Lakshmana defeat the headless demon Kabandha, who advises them to seek Sugriva at Rishyamukha.", sig: "Marks the turn toward the monkey alliance.", src: "Panel 14" },
  { id: "SHIVA_RAM_15", panel: 15, title: "Meeting Hanuman & Sugriva", sanskrit: "Hanumān-Sugrīva Maitrī", text: "Hanuman introduces Rama and Lakshmana to the exiled monkey king Sugriva.", sig: "Introduces Hanuman, central hero of the Javanese Ramayana.", src: "Panel 15" },
  { id: "SHIVA_RAM_16", panel: 16, title: "Duel of Vali and Sugriva", sanskrit: "Vāli-Sugrīva Yuddha", text: "Rama shoots an arrow from behind a tree to slay Vali and restore Sugriva to the throne of Kishkindha.", sig: "Illustrates the seven tala trees motif.", src: "Panel 16" },
  { id: "SHIVA_RAM_17", panel: 17, title: "Council of Kishkindha", sanskrit: "Vānara Senā", text: "Sugriva dispatches monkey search parties in all four directions to locate Sita.", sig: "Lively depiction of vanara warriors.", src: "Panel 17" },
  { id: "SHIVA_RAM_18", panel: 18, title: "Hanuman Receives Rama's Ring", sanskrit: "Aṅgulīya Pradāna", text: "Rama entrusts his signet ring to Hanuman as a token of recognition for Sita.", sig: "Intimate devotional gesture.", src: "Panel 18" },
  { id: "SHIVA_RAM_19", panel: 19, title: "Hanuman's Leap Across the Ocean", sanskrit: "Samudra Laṅghana", text: "Hanuman leaps from Mount Mahendra across the sea toward the island fortress of Lanka.", sig: "Dynamic airborne posture carved in andesite.", src: "Panel 19" },
  { id: "SHIVA_RAM_20", panel: 20, title: "Hanuman Finds Sita in Ashoka Grove", sanskrit: "Aśoka Vāṭikā", text: "Hidden in the Ashoka garden, Hanuman presents Rama's ring to the captive Sita.", sig: "Iconic scene of hope in captivity.", src: "Panel 20" },
  { id: "SHIVA_RAM_21", panel: 21, title: "Capture & Burning of Lanka", sanskrit: "Laṅkā Dāha", text: "Ravana's guards set Hanuman's tail ablaze; Hanuman breaks free and sets Lanka's palaces on fire.", sig: "Rich architectural motifs of burning Lanka.", src: "Panel 21" },
  { id: "SHIVA_RAM_22", panel: 22, title: "Hanuman Returns to Rama", sanskrit: "Cūḍāmaṇi Pradāna", text: "Hanuman returns across the sea and delivers Sita's crest-jewel to Rama.", sig: "Confirms Sita is alive.", src: "Panel 22" },
  { id: "SHIVA_RAM_23", panel: 23, title: "March to the Southern Shore", sanskrit: "Sāgara Tīra", text: "Rama, Lakshmana, Sugriva, and the vanara army march to the ocean's edge; Vibhishana defects to Rama.", sig: "Sets the stage for the ocean crossing.", src: "Panel 23" },
  { id: "SHIVA_RAM_24", panel: 24, title: "Building the Bridge to Lanka", sanskrit: "Nala Setu (Rāma Setu)", text: "The vanaras hurl boulders into the sea to construct the causeway to Lanka. The narrative continues on Candi Brahma Panel 1.", sig: "Final Ramayana panel on Candi Shiva.", src: "IISTE Visual Grammar (2019); Panel 24" },
];

export const RAMAYANA_BRAHMA_SUMMARY = [
  "Crossing the Causeway to Lanka (Brahma Panel 1 / Epic 25)",
  "Ravana's War Council & Angada's Embassy",
  "Opening Siege of Lanka & Lakshmana's Valor",
  "Awakening & Fall of Kumbhakarna",
  "Indrajit's Maya & Nagapasha",
  "Hanuman Fetches the Healing Mountain (Sanjivani)",
  "Final Duel: Rama Slays Ravana (Dasamuka)",
  "Sita's Ordeal by Fire (Agni Pariksha)",
  "Coronation of Vibhishana & Return to Ayodhya",
  "Rama's Royal Coronation & Conclusion (Brahma Panel 30 / Epic 54)",
];

export const KRISHNAYANA_VISHNU_SUMMARY = [
  "Mathura Court of King Ugrasena & Kamsa's Tyranny (Panel 1)",
  "Birth of Krishna & Escape Across the Yamuna",
  "Childhood in Gokula & Slaying of Putana",
  "Balarama & Krishna Defeat Dhenukasura (Ass Demon)",
  "Subduing the Serpent King Kaliya",
  "Lifting Mount Govardhana to Shelter Villagers",
  "Triumph over King Kamsa & Restoration of Mathura (Panel 30)",
];
