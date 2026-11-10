#!/usr/bin/env python3
"""
Generate dialogues and sound effects for Pantheon's Wrath using ElevenLabs API.
Audio files are saved as 44.1kHz 16-bit PCM WAV into assets/audio/.
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY and len(sys.argv) > 1:
    API_KEY = sys.argv[1]

if not API_KEY:
    print("Error: ELEVENLABS_API_KEY environment variable or argument required.")
    sys.exit(1)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)
TMP_DIR = "/tmp/elevenlabs_gen"
os.makedirs(TMP_DIR, exist_ok=True)

VOICES = {
    "zeus": "nPczCjzI2devNBz1zQrb",      # Brian: Deep, Resonant
    "poseidon": "JBFqnCBsd6RMkjVDRZzb",  # George: Warm, Captivating Storyteller
    "hades": "N2lVS1w4EtoT3dr4eOWO",     # Callum: Husky Trickster / Abyss
    "ares": "pNInz6obpgDQGcFmaJgB",      # Adam: Dominant, Firm
    "warrior": "SOYHLrjzK2X1ezoPC6cr",   # Harry: Fierce Warrior
    "demon": "N2lVS1w4EtoT3dr4eOWO",     # Callum: Dark
}

DIALOGUES = [
    ("god_zeus_blessing", VOICES["zeus"], "I am Zeus, King of Olympus! Smite the underworld with my thunderbolts!"),
    ("god_zeus_cast", VOICES["zeus"], "Feel the wrath of Olympus!"),
    ("god_poseidon_blessing", VOICES["poseidon"], "I am Poseidon, Lord of the Oceans! Let the crushing tides swallow your foes!"),
    ("god_poseidon_cast", VOICES["poseidon"], "The ocean depths answer my call!"),
    ("god_hades_blessing", VOICES["hades"], "I am Hades, Ruler of the Dead. Claim their souls and drag them to the abyss!"),
    ("god_hades_cast", VOICES["hades"], "Your soul belongs to Tartarus!"),
    ("god_ares_blessing", VOICES["ares"], "I am Ares, God of War! Let blood spill and carnage reign upon this sacred arena!"),
    ("god_ares_cast", VOICES["ares"], "Spartan Berserk! Unleash the fury!"),
    ("warrior_intro", VOICES["warrior"], "By the gods of Olympus, no Tartarus demon shall leave this arena alive!"),
    ("warrior_pray", VOICES["warrior"], "Hear me, Immortals! Grant me divine power!"),
    ("warrior_attack", VOICES["warrior"], "For Sparta! Die!"),
    ("warrior_hurt", VOICES["warrior"], "You will pay for that!"),
    ("warrior_victory", VOICES["warrior"], "Olympus stands undefeated!"),
    ("demon_spawn", VOICES["demon"], "Mortal flesh shall burn in the pits!"),
    ("demon_defeat", VOICES["demon"], "The darkness... will return!"),
]

SOUND_EFFECTS = [
    ("sword_swing", "Fast sharp steel sword swing slicing through the air with clean swoosh", 1.0),
    ("sword_hit", "Heavy metallic sword blade slash cutting flesh with wet punch impact", 1.0),
    ("lightning", "Explosive crack of lightning and Zeus thunder blast with electric resonance", 2.0),
    ("water_wave", "Violent oceanic tidal wave crashing flood surging water splash", 2.0),
    ("soul_drain", "Dark magical necrotic energy vortex vacuum eerie ghost soul absorption", 2.0),
    ("ares_fury", "Ancient war horn blast followed by intense roaring fire eruption", 2.5),
    ("prayer_chant", "Celestial ethereal golden chime divine choir reverberating hum", 2.5),
    ("demon_roar", "Terrifying demonic guttural roar monster abyssal screech", 1.5),
    ("demon_death", "Monstrous beast dying agonized scream dissolving into smoke", 2.0),
    ("player_hurt", "Heavy blunt hit on bronze warrior armor chest with grunt", 1.0),
]

def tts(name, voice_id, text):
    print(f"[TTS] Generating {name}: '{text}'...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers)
    mp3_path = os.path.join(TMP_DIR, f"{name}.mp3")
    wav_path = os.path.join(OUTPUT_DIR, f"{name}.wav")

    try:
        with urllib.request.urlopen(req) as resp:
            with open(mp3_path, "wb") as f:
                f.write(resp.read())
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "2", wav_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"  -> Saved {wav_path}")
    except Exception as e:
        print(f"  Error generating {name}: {e}")

def sfx(name, prompt, duration):
    print(f"[SFX] Generating {name} ({duration}s): '{prompt}'...")
    url = "https://api.elevenlabs.io/v1/sound-generation"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "text": prompt,
        "duration_seconds": duration
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers)
    mp3_path = os.path.join(TMP_DIR, f"{name}.mp3")
    wav_path = os.path.join(OUTPUT_DIR, f"{name}.wav")

    try:
        with urllib.request.urlopen(req) as resp:
            with open(mp3_path, "wb") as f:
                f.write(resp.read())
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "2", wav_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"  -> Saved {wav_path}")
    except Exception as e:
        print(f"  Error generating {name}: {e}")

def main():
    print("=== Generating Dialogues ===")
    for name, voice, text in DIALOGUES:
        tts(name, voice, text)
        time.sleep(0.3)

    print("\n=== Generating Sound Effects ===")
    for name, prompt, dur in SOUND_EFFECTS:
        sfx(name, prompt, dur)
        time.sleep(0.3)

    print("\nDone! All audio files generated in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
