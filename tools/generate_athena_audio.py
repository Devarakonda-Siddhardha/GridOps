"""
Script to generate background commentary and narrative dialogue for Athena
using ElevenLabs Voice ID: AfGQOwNTk8JotVVaad3o (Sudha Devarakonda)
Model: eleven_v4 exclusively.
"""

import json
import os
import subprocess
import urllib.request
import urllib.error

API_KEY = "sk_5fb94157a98f1bf30f44a3bbb896179629ed7b572387f50b"
VOICE_ID = "AfGQOwNTk8JotVVaad3o"
MODEL_ID = "eleven_v4"

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
os.makedirs(OUT_DIR, exist_ok=True)

ATHENA_LINES = {
    "athena_intro": "Champion of Hellas, hear my voice. I am Athena. Look upon Mount Olympus. The Underworld claws at our holy mount. Take up your blade and cleanse the sacred plaza!",
    "athena_pray_zeus": "Zeus, Lord of Olympus, watches from above. Kneel before the King of the Gods and let lightning empower your strikes.",
    "athena_pray_poseidon": "Poseidon's tides crash against the shores of Hellas. Channel his oceanic fury to shatter enemy ranks.",
    "athena_pray_hades": "Hades holds the subterranean gates of Tartarus. Even in death, there is power. Claim his dark siphon.",
    "athena_pray_ares": "Ares thirsts for battle. Let rage fuel your blade, but remember: true victory is won through wisdom.",
    "athena_class_archer": "A Cretan Toxotes bow! Strike with precision from afar. Distance and positioning are your greatest allies.",
    "athena_class_cavalry": "A Thessalian warhorse! Trample the enemy cohorts beneath heavy hooves and spearhead our assault!",
    "athena_class_champion": "The shield of Sparta! Unyielding and steadfast, hold the line against all odds.",
    "athena_level2_coast": "We have reached the Peloponnese shoreline. The Roman fleet has beached their triremes. Burn their vanguard before they establish a foothold!",
    "athena_level3_valley": "The Great Valley of Arcadia lies in chains. Roman outposts patrol these hills. Find the captured Spartan cages, liberate our soldiers, and assemble the Phalanx!",
    "athena_army_assembled": "Our brothers in arms are free! Command them with courage. Together, no Roman legion can withstand the Greek Phalanx.",
    "athena_level4_chasm": "The earth tears open into Tartarus. Beware the Infernal Minotaur! Dodge his ground-slam shockwaves and strike true!",
    "athena_level5_siege": "Behold, Castrum Roma! Marcus Aurelius hides behind stone ramparts. Sound the charge! Breach the fortress gates and reclaim the glory of Hellas!",
    "athena_low_health": "Stand strong, warrior! Do not falter now. Commune with the Gods and regain your vigor!",
    "athena_victory": "Hellas is restored! Your courage and strategy have echoed into eternity. Olympus honors you, Champion of Greece!",
    "athena_tactical_advice": "Keep moving, warrior! Time your dodges and use the terrain to flank their shields.",
    "athena_block_praise": "Well guarded! Raise your shield with wisdom, and strike when the Roman legion falters.",
    "athena_combo_praise": "Magnificent strike! Your blade moves like the fury of Olympus itself!",
    "athena_boss_warning": "Beware, Champion! A mighty Roman commander approaches. Stand firm and unleash the wrath of the Gods!",
    "athena_wave_cleared": "The enemy vanguard is broken! Press the advantage and heal at the sacred shrines if you must.",
    "athena_cage_freed": "Another Spartan brother freed from Roman chains! Our phalanx grows stronger with every soul!",
    "athena_divine_cast": "The Gods answer your call! Let divine wrath sweep across the battlefield!",
    "athena_fortress_gate": "The fortress gate crumbles! Charge through the breach and claim victory for Hellas!"
}

def generate_line(key, text):
    wav_path = os.path.join(OUT_DIR, f"{key}.wav")
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
        print(f"[Athena Voice] Skipping existing '{key}.wav'")
        return True
    mp3_path = os.path.join(OUT_DIR, f"{key}.mp3")

    print(f"\n[Athena Voice] Generating '{key}' using model '{MODEL_ID}'...")
    print(f"Text: \"{text}\"")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.80,
            "style": 0.15,
            "use_speaker_boost": True
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            with open(mp3_path, "wb") as f:
                f.write(data)
            print(f"Saved MP3 ({len(data)} bytes). Converting to WAV...")

            # Convert to standard 44.1kHz 16-bit WAV for Godot
            cmd = ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "2", wav_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            if os.path.exists(mp3_path):
                os.remove(mp3_path)

            print(f"Successfully created: {wav_path} ({os.path.getsize(wav_path)} bytes)")
            return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"HTTPError {e.code} for '{key}': {err_msg}")
        return False
    except Exception as e:
        print(f"Error for '{key}': {e}")
        return False

def main():
    print(f"=== GENERATING ATHENA VOICE COMMENTARY ===")
    print(f"Voice ID: {VOICE_ID} (Sudha Devarakonda)")
    print(f"Model ID: {MODEL_ID} (Exclusively v4)")
    print(f"Total lines: {len(ATHENA_LINES)}")

    success_count = 0
    for key, text in ATHENA_LINES.items():
        if generate_line(key, text):
            success_count += 1

    print(f"\n=== GENERATION COMPLETE: {success_count}/{len(ATHENA_LINES)} lines generated successfully! ===")

if __name__ == "__main__":
    main()
