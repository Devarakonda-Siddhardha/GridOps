#!/usr/bin/env python3
"""
Generate dialogues and sound effects for the expanded Pantheon's Wrath:
- 3D Gods manifestation dialogues (Zeus, Poseidon, Hades, Ares)
- Playable Class voice lines (Archer, Cavalry)
- Enemy voice callouts (Roman Archer, Roman Cavalry, Minotaur)
- Biome intro narratives
- Sound effects (arrow_shoot, arrow_hit, horse_gallop, horse_neigh, lance_pierce, minotaur_slam)
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import math
import struct
import wave

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_5fb94157a98f1bf30f44a3bbb896179629ed7b572387f50b")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)
TMP_DIR = "/tmp/elevenlabs_expanded"
os.makedirs(TMP_DIR, exist_ok=True)

VOICES = {
    "zeus": "nPczCjzI2devNBz1zQrb",       # Brian: Deep, resonant celestial authority
    "poseidon": "JBFqnCBsd6RMkjVDRZzb",   # George: Warm, deep resonance
    "hades": "N2lVS1w4EtoT3dr4eOWO",      # Callum: Dark, husky, ominous
    "ares": "pNInz6obpgDQGcFmaJgB",       # Adam: Dominant, aggressive war god
    "archer": "XB0fDUnXU5powFXDhCwa",     # Charlotte: Sharp, agile warrior
    "cavalry": "SOYHLrjzK2X1ezoPC6cr",    # Harry: Bold, thundering warrior
    "roman": "CwhRBWXzGAHq8TQ4Fs17",      # Roger: Stern Roman officer
    "narrator": "JBFqnCBsd6RMkjVDRZzb",   # George: Epic storyteller
    "minotaur": "N2lVS1w4EtoT3dr4eOWO",   # Callum: Deep monstrous roar
}

DIALOGUES = [
    ("zeus_manifest", VOICES["zeus"], "I am Zeus, King of the Gods! The heavens shake at your devotion. Smite the Roman invaders with celestial lightning!"),
    ("poseidon_manifest", VOICES["poseidon"], "Mortal! I am Poseidon, master of the ocean depths! Unleash my crushing tidal waves and drown their legions!"),
    ("hades_manifest", VOICES["hades"], "I am Hades, sovereign of the Underworld. No Roman soul shall escape the abyssal grasp of Tartarus!"),
    ("ares_manifest", VOICES["ares"], "Ares is with you! Spill their blood, crack their shields, and make the earth drown in Roman carnage!"),
    ("archer_select", VOICES["archer"], "My bow is strung. Not a single Roman shall escape my arrows!"),
    ("archer_shoot", VOICES["archer"], "Arrows away! For Hellas!"),
    ("cavalry_select", VOICES["cavalry"], "The Thessalian cavalry rides! Trample them beneath iron hooves!"),
    ("cavalry_charge", VOICES["cavalry"], "Charge! Ride them down!"),
    ("roman_archer_shout", VOICES["roman"], "Sagittarii, rain arrows upon them!"),
    ("roman_cavalry_charge", VOICES["roman"], "Equites, charge! Break their formation!"),
    ("minotaur_bellow", VOICES["minotaur"], "Raaaargh! Slay the Greek mortal!"),
    ("biome_coast", VOICES["narrator"], "The Roman fleet has landed on the shores of Peloponnese! Burn their triremes and push them into the sea!"),
    ("biome_chasm", VOICES["narrator"], "A dark fissure to Tartarus has opened! Vanquish the Infernal Minotaur before the abyss swallows Greece!"),
]

SOUND_EFFECTS = [
    ("arrow_shoot", "Sharp high-speed wooden bowstring twang release whistling arrow flight", 1.0),
    ("arrow_hit", "Arrow thudding impact into wood and iron shield armor", 1.0),
    ("horse_gallop", "Rhythmic heavy quadruped horse hooves galloping rapidly on dry dirt ground", 2.0),
    ("horse_neigh", "Spirited fierce warhorse neigh snort whinny in battle", 1.5),
    ("lance_pierce", "Heavy cavalry iron lance impaling pierce through wooden armor impact", 1.5),
    ("minotaur_slam", "Massive heavy stone battle hammer crushing ground explosion shockwave", 2.0),
]

def tts(name, voice_id, text):
    out_wav = os.path.join(OUTPUT_DIR, f"{name}.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
        print(f"Skipping {name}, already exists")
        return
    print(f"[TTS] Generating {name}...")
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
            "similarity_boost": 0.75
        }
    }).encode("utf-8")

    tmp_mp3 = os.path.join(TMP_DIR, f"{name}.mp3")
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(tmp_mp3, "wb") as f:
                f.write(resp.read())
        subprocess.run(["ffmpeg", "-y", "-i", tmp_mp3, "-ar", "44100", "-ac", "1", out_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  -> Generated {out_wav}")
    except Exception as e:
        print(f"  Warning: TTS failed for {name} ({e}), synthesizing fallback wave...")
        _synth_fallback_voice(out_wav, 1.5)

def sfx(name, text, duration):
    out_wav = os.path.join(OUTPUT_DIR, f"{name}.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
        print(f"Skipping {name}, already exists")
        return
    print(f"[SFX] Generating {name}...")
    url = "https://api.elevenlabs.io/v1/sound-generation"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "text": text,
        "duration_seconds": duration,
        "prompt_influence": 0.4
    }).encode("utf-8")

    tmp_mp3 = os.path.join(TMP_DIR, f"{name}.mp3")
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(tmp_mp3, "wb") as f:
                f.write(resp.read())
        subprocess.run(["ffmpeg", "-y", "-i", tmp_mp3, "-ar", "44100", "-ac", "1", out_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  -> Generated {out_wav}")
    except Exception as e:
        print(f"  Warning: SFX failed for {name} ({e}), synthesizing fallback wave...")
        _synth_fallback_sfx(out_wav, name, duration)

def _synth_fallback_voice(filepath, duration=1.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(filepath, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            env = math.sin(math.pi * (i / n_samples))
            val = math.sin(2.0 * math.pi * 180.0 * t) * 0.4 + math.sin(2.0 * math.pi * 360.0 * t) * 0.2
            s_val = int(val * env * 16000)
            frames.extend(struct.pack("<h", max(-32768, min(32767, s_val))))
        w.writeframes(frames)

def _synth_fallback_sfx(filepath, name, duration=1.0):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(filepath, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            env = math.exp(-3.0 * t)
            freq = 400.0 if "arrow" in name else (120.0 if "slam" in name or "pierce" in name else 220.0)
            val = math.sin(2.0 * math.pi * freq * t)
            s_val = int(val * env * 22000)
            frames.extend(struct.pack("<h", max(-32768, min(32767, s_val))))
        w.writeframes(frames)

if __name__ == "__main__":
    print("=== Generating Expanded Audio & Dialogues via ElevenLabs ===")
    for name, voice_id, text in DIALOGUES:
        tts(name, voice_id, text)
        time.sleep(0.3)

    for name, text, duration in SOUND_EFFECTS:
        sfx(name, text, duration)
        time.sleep(0.3)

    print("=== ALL AUDIO GENERATION COMPLETE ===")
