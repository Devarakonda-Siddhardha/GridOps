/**
 * Phase 15 — Historically Documented Epigraphy of Candi Prambanan
 * Strictly distinguishes verified readings from weathered/reconstructed characters (⟨ ⟩ / [ ]).
 * Original Shivagrha Stele (D.28) is preserved at the National Museum of Indonesia, Jakarta.
 */

export const INSCRIPTIONS_DATA = {
  SHIVAGRHA_D28: {
    id: "SHIVAGRHA_D28",
    name: "Shivagrha Inscription (Prasasti Śivagṛha, 856 CE)",
    provenance: "PROVENANCE EXHIBIT — Original Stele (Inv. D.28) in National Museum of Indonesia, Jakarta",
    scriptNote: "Old Javanese (Kawi) script (9th c. CE, derived from South Indian Pallava; distinct from Devanāgarī)",
    originalScript:
      "꧋ꦫꦶꦏꦭꦤꦶꦏꦤꦁꦯꦏꦧ꧀ꦢꦮ꧀ꦮꦭꦸꦁꦒꦸꦤꦸ⟨ꦔ⟩ꦱꦁꦮꦶꦏꦸ꧉\n" +
      "ꦱꦩꦂꦒ꧀ꦒꦯꦶꦫꦯꦸꦏ꧀ꦭꦥꦏ꧀ꦰꦱꦮꦼꦭꦱ꧀ꦪꦤꦴꦠꦁꦠꦶꦛꦶ꧉\n" +
      "ꦮꦽꦲꦱ꧀ꦥꦠꦶꦮꦒꦻꦭꦮꦤ꧀ꦩꦮꦸꦫꦸꦏꦸꦁꦪꦤꦴꦮꦫꦮꦺꦃ꧉\n" +
      "ꦪꦠꦺꦏꦤꦠꦼꦮꦼꦏ꧀ꦨꦛꦫꦒꦶꦤꦮꦻꦱꦶꦤꦁꦱ꧀ꦏꦫꦮꦺꦃ꧉\n" +
      "[Note: Rendered in Javanese Unicode (A980–A9DF), the direct typographic descendant of 9th-c. Kawi script; ⟨ꦔ⟩ marks a restored nasal.]",
    transcription:
      "Stanza 9 (Old Javanese kakawin with Sanskrit vocabulary):\n" +
      "tlas maṅkanoparata saṅ prabhu jāti niṅ rat / rājya ka ratwan asilih taṅan inangsö /\n" +
      "dyah lokapāla rānujāmata lokapāla / swastha ng prajā sacaturāśrama wipramukhya // 9 //\n\n" +
      "Stanza 24 (Chronogram & Consecration Date):\n" +
      "ri kāla nikanang śakābda wwalung gunu⟨ṅ⟩ saṅ wiku / samārggaśiraśuklapakṣa sawĕlas ya nā taṅ tithi /\n" +
      "wrĕhaspati wagai lawan mawurukuṅ ya nā wāra weḥ / yatekana tĕwĕk bhaṭāra ginawai sinangskāra weḥ // 24 //\n\n" +
      "Key Sanskrit / Old Javanese Temple Designation:\n" +
      "... śivagṛha ... (Sarkar 1971; de Casparis 1956)\n" +
      "[Uncertain/restored characters marked ⟨ ⟩; unpreserved lines are omitted rather than invented.]",
    iast:
      "Stanza 9: tlas maṅkanoparata saṅ prabhu jāti niṅ rat, rājya ka ratwan asilih taṅan inangsö; dyah lokapāla rānujāmata lokapāla, swastha ng prajā sacaturāśrama wipramukhya.\n" +
      "Stanza 24: ri kāla nikanang śakābda wwalung gunu⟨ṅ⟩ saṅ wiku, samārggaśiraśuklapakṣa sawĕlas ya nā taṅ tithi; wrĕhaspati wagai lawan mawurukuṅ ya nā wāra weḥ, yatekana tĕwĕk bhaṭāra ginawai sinangskāra weḥ.",
    translation:
      "Stanza 9: \"After these [deeds], the king [of] Jātiningrat [resigned / passed away — scholarly debate on 'uparata']; the kingship and the royal court (keraton) were handed over to his successor, Dyah Lokapāla, who was equal to a younger brother of the [divine] Lokapāla; prosperous were the subjects, together with the four āśramas with the Brāhmaṇas at the head.\"\n\n" +
      "Stanza 24: \"At the time of the Śaka year 778 [candrasangkala: wwalung (8) gunung (7) sang wiku (7) = 778 Śaka / 856 CE], in the bright half of the month Mārgaśīrṣa, the eleventh lunar day (tithi), on a Thursday, Wagai (5-day week) and Wurukung (6-day week) — that was the moment when [the sanctuary of] the Lord [Śivagṛha] was completed and consecrated.\"",
    historicalExplanation:
      "Issued in 856 CE under Dyah Lokapala (Rakai Kayuwangi) at the transition from Rakai Pikatan's reign, the Shivagrha inscription is the primary epigraphic foundation for dating and identifying Candi Prambanan. It records the consecration of a grand Shaiva sanctuary ('Śivagṛha', House of Śiva), describes surrounding subsidiary shrines and enclosing walls, and documents a major hydraulic engineering project diverting a river (identified with the Opak River) to protect and level the sacred compound. Note on provenance: the original andesite stele (Inv. D.28) was recovered from the Prambanan/Yogyakarta area and is preserved in the National Museum of Indonesia, Jakarta — not on the temple walls.",
    sources:
      "J.G. de Casparis (1956), Prasasti Indonesia II, pp. 280–330; L.-Ch. Damais (1952), BEFEO 46; H.B. Sarkar (1971), Corpus of the Inscriptions of Java; Andri Restiyadi (2020), Berkala Arkeologi 40(1):45–62.",
  },

  PERWARA_SHORT_MARK: {
    id: "PERWARA_SHORT_MARK",
    name: "Perwara Short Donor / Mason Inscription (Fragmentary)",
    provenance: "IN-SITU ARCHAEOLOGICAL FEATURE — Perwara Row 1 East",
    scriptNote: "9th-century Old Javanese (Kawi) incised/painted stone block mark",
    originalScript:
      "꧋ꦫꦏꦻ[···] / [···]ꦥꦶꦏꦠꦤ꧀[···]\n" +
      "[Fragmentary 9th-c. Kawi mason/patronage label; bracketed ellipses mark eroded or missing syllables.]",
    transcription:
      "Documented short Old Javanese stone-block marks on Central Javanese Perwara shrines record regional titles (rakai / pamgat) and construction allocations.\n" +
      "Example attested title form: rakai [...] (patronage/ward marker; exact Perwara-by-Perwara readings remain fragmentary due to 16th-century earthquake collapse).",
    iast: "rakai [...] / śrī mahārāja [...] [fragmentary]",
    translation:
      "\"Lord of [region] ...\" — Short administrative/patronage labels indicating which regional nobles or royal officials sponsored individual Perwara shrines surrounding the inner court.",
    historicalExplanation:
      "Unlike the monumental Shivagrha charter (now in Jakarta), short incised and painted Kawi labels were applied directly to Perwara temple blocks during construction in the late 9th century to coordinate stone assembly and record regional donations. Because most of the 224 Perwara shrines collapsed, many labels are lost or fragmentary.",
    sources:
      "J.G. de Casparis (1958), Berita Dinas Purbakala No. 4 (Short Inscriptions); Balai Pelestarian Kebudayaan Wilayah X.",
  },
};
