"""
Procedural sound generator for Pantheon's Wrath.
Generates sound effects as standard 16-bit mono 44.1kHz WAV files:
- sword_swing.wav
- sword_hit.wav
- demon_roar.wav
- demon_hit.wav
- demon_death.wav
- lightning.wav
- water_wave.wav
- soul_drain.wav
- ares_fury.wav
- prayer_chant.wav
- player_hurt.wav
"""

import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100

def write_wav(filename, samples):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        int_samples = [max(-32767, min(32767, int(s * 32767))) for s in samples]
        wav.writeframes(struct.pack(f'<{len(int_samples)}h', *int_samples))
    print(f"Generated sound: {filename} ({len(samples)/SAMPLE_RATE:.2f}s)")

def gen_sword_swing():
    # Whoosh: frequency slides down with white noise
    dur = 0.22
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (i / n))
        freq = 350 - (i / n) * 180
        tone = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2 - 1) * 0.4
        samples.append((tone * 0.6 + noise * 0.4) * env * 0.7)
    return samples

def gen_sword_hit():
    # Metallic clang + flesh impact
    dur = 0.3
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-i / (SAMPLE_RATE * 0.05))
        # High metallic harmonics
        clang = (math.sin(2 * math.pi * 840 * t) +
                 math.sin(2 * math.pi * 1280 * t) * 0.7 +
                 math.sin(2 * math.pi * 2150 * t) * 0.4)
        noise = (random.random() * 2 - 1) * 0.5 * math.exp(-i / (SAMPLE_RATE * 0.02))
        samples.append((clang * 0.6 + noise * 0.4) * env * 0.8)
    return samples

def gen_lightning():
    # Sharp thunder crack + low rumble
    dur = 0.8
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Initial sharp crack
        crack_env = math.exp(-i / (SAMPLE_RATE * 0.04))
        crack = (random.random() * 2 - 1) * crack_env * 0.95
        # Low rumble
        rumble_env = (1 - math.exp(-i / (SAMPLE_RATE * 0.05))) * math.exp(-i / (SAMPLE_RATE * 0.3))
        rumble = (math.sin(2 * math.pi * 75 * t) + math.sin(2 * math.pi * 120 * t) * 0.5) * rumble_env * 0.8
        samples.append(crack + rumble)
    return samples

def gen_water_wave():
    # Sweeping rush of water
    dur = 0.7
    n = int(dur * SAMPLE_RATE)
    samples = []
    lp = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (i / n)) ** 1.5
        noise = random.random() * 2 - 1
        # Lowpass filter sweeping up then down
        cutoff = 0.05 + 0.25 * math.sin(math.pi * (i / n))
        lp = lp + cutoff * (noise - lp)
        samples.append(lp * env * 0.9)
    return samples

def gen_soul_drain():
    # Ethereal descending spectral choir resonance
    dur = 0.75
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (i / n))
        f1 = 280 + math.sin(t * 12) * 20
        f2 = 420 + math.cos(t * 8) * 30
        f3 = 140
        tone = (math.sin(2 * math.pi * f1 * t) * 0.4 +
                math.sin(2 * math.pi * f2 * t) * 0.3 +
                math.sin(2 * math.pi * f3 * t) * 0.5)
        samples.append(tone * env * 0.7)
    return samples

def gen_ares_fury():
    # Roaring explosive battle burst
    dur = 0.6
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-i / (SAMPLE_RATE * 0.15))
        f = 160 - (i / n) * 90
        tone = math.sin(2 * math.pi * f * t)
        dist = math.tanh(tone * 3.0) # warm distortion
        noise = (random.random() * 2 - 1) * math.exp(-i / (SAMPLE_RATE * 0.08)) * 0.6
        samples.append((dist * 0.7 + noise * 0.3) * env * 0.85)
    return samples

def gen_prayer_chant():
    # Divine celestial chord (C Major triad shimmering: C4 261Hz, E4 329Hz, G4 392Hz, C5 523Hz)
    dur = 1.0
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (1 - math.exp(-i / (SAMPLE_RATE * 0.15))) * math.exp(-i / (SAMPLE_RATE * 0.5))
        c4 = math.sin(2 * math.pi * 261.63 * t)
        e4 = math.sin(2 * math.pi * 329.63 * t)
        g4 = math.sin(2 * math.pi * 392.00 * t)
        c5 = math.sin(2 * math.pi * 523.25 * t)
        bell = (c4 * 0.35 + e4 * 0.25 + g4 * 0.25 + c5 * 0.15)
        samples.append(bell * env * 0.8)
    return samples

def gen_demon_roar():
    dur = 0.5
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (i / n))
        f = 95 + math.sin(t * 35) * 30
        tone = math.sin(2 * math.pi * f * t)
        noise = (random.random() * 2 - 1) * 0.35
        dist = math.tanh((tone + noise) * 2.5)
        samples.append(dist * env * 0.75)
    return samples

def gen_player_hurt():
    dur = 0.25
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-i / (SAMPLE_RATE * 0.06))
        f = 190 - (i / n) * 90
        tone = math.sin(2 * math.pi * f * t)
        samples.append(tone * env * 0.7)
    return samples

def gen_demon_death():
    dur = 0.65
    n = int(dur * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-i / (SAMPLE_RATE * 0.2))
        f = 120 - (i / n) * 80
        tone = math.sin(2 * math.pi * f * t)
        noise = (random.random() * 2 - 1) * 0.4
        samples.append((tone * 0.6 + noise * 0.4) * env * 0.8)
    return samples

if __name__ == "__main__":
    out_dir = "/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/audio"
    write_wav(f"{out_dir}/sword_swing.wav", gen_sword_swing())
    write_wav(f"{out_dir}/sword_hit.wav", gen_sword_hit())
    write_wav(f"{out_dir}/lightning.wav", gen_lightning())
    write_wav(f"{out_dir}/water_wave.wav", gen_water_wave())
    write_wav(f"{out_dir}/soul_drain.wav", gen_soul_drain())
    write_wav(f"{out_dir}/ares_fury.wav", gen_ares_fury())
    write_wav(f"{out_dir}/prayer_chant.wav", gen_prayer_chant())
    write_wav(f"{out_dir}/demon_roar.wav", gen_demon_roar())
    write_wav(f"{out_dir}/demon_death.wav", gen_demon_death())
    write_wav(f"{out_dir}/player_hurt.wav", gen_player_hurt())
