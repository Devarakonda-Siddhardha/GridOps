#!/usr/bin/env python3
"""
Generate campaign voice dialogues and sound effects for the Roman conquest storyline.
"""

import os
import sys
import json
import time
import subprocess
import urllib.request

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY and len(sys.argv) > 1:
    API_KEY = sys.argv[1]

if not API_KEY:
    print("Error: ELEVENLABS_API_KEY required")
    sys.exit(1)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)
TMP_DIR = "/tmp/elevenlabs_campaign"
os.makedirs(TMP_DIR, exist_ok=True)

VOICES = {
    "general": "pNInz6obpgDQGcFmaJgB",   # Adam: Dominant, Firm Roman Commander
    "centurion": "CwhRBWXzGAHq8TQ4Fs17", # Roger: Resonant officer
    "ally": "SOYHLrjzK2X1ezoPC6cr",      # Harry: Fierce Greek warrior
    "narrator": "JBFqnCBsd6RMkjVDRZzb",  # George: Warm, Epic Storyteller
}

DIALOGUES = [
    ("general_intro", VOICES["general"], "You dare challenge the eternal might of Rome, barbarian dog? You will kneel!"),
    ("general_testudo", VOICES["general"], "Legions, form the testudo! Crush their pathetic rebellion!"),
    ("general_defeat", VOICES["general"], "Impossible... Rome cannot fall to a Greek mongrel..."),
    ("centurion_shout", VOICES["centurion"], "Cohort, advance! Draw your gladii and leave none alive!"),
    ("ally_rescued", VOICES["ally"], "We are free! Lead us to war, Spartan Champion!"),
    ("ally_charge", VOICES["ally"], "For the glory of Hellas! Advance the Phalanx!"),
    ("campaign_intro_2", VOICES["narrator"], "Arcadia is overrun by Roman outposts. Liberate our captured brothers and rally the Phalanx!"),
    ("campaign_intro_3", VOICES["narrator"], "Behold Castrum Roma! Breach the fortress gate, vanquish the Legion, and reclaim Hellas!"),
    ("campaign_victory", VOICES["narrator"], "The Roman Eagle has fallen! The glory of the Greek Empire rises once more!"),
]

SOUND_EFFECTS = [
    ("war_horn_roman", "Deep resonant brass Roman war horn blast echo across ancient battlefield", 2.0),
    ("gate_smash", "Massive heavy wooden fortress gate exploding splintering destruction impact", 2.0),
    ("cage_break", "Wooden timber stockade prisoner cage smashing and splintering open impact", 1.5),
    ("shield_block", "Heavy metal sword clashing against large wooden bronze-rimmed roman shield", 1.0),
]

def tts(name, voice_id, text):
    print(f"[TTS] Generating {name}...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.8}
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
    print(f"[SFX] Generating {name} ({duration}s)...")
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
    print("=== Generating Campaign Dialogues ===")
    for name, voice, text in DIALOGUES:
        tts(name, voice, text)
        time.sleep(0.3)

    print("\n=== Generating Campaign SFX ===")
    for name, prompt, dur in SOUND_EFFECTS:
        sfx(name, prompt, dur)
        time.sleep(0.3)

    print("\nCampaign audio generation complete!")

if __name__ == "__main__":
    main()
