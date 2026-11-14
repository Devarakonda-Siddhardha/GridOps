#!/usr/bin/env python3
"""Download Sketchfab models for player classes and Olympian God statues, appending to CREDITS.md."""
import json, os, urllib.request

TOKEN = "cc7ff50739131beb1d757280c26cf6dd"
H = {"Authorization": f"Token {TOKEN}", "User-Agent": "PantheonsWrath/1.0"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "models")

MODELS = {
    "sf_player_warrior.glb": "62d5291dd0454cb28a29a37056a59013",
    "sf_player_cavalry.glb": "b41609f97778422598ecd9e0dad24d90",
    "sf_god_zeus.glb": "a524bb3767a44d30b0dd02190568fae7",
    "sf_god_poseidon.glb": "5aa411fc7b2b4e69979d55ae6a7cb052",
    "sf_god_hades.glb": "c757573759ed49f8a0627c77998afa80",
    "sf_god_ares.glb": "0d09ee1dde8d419b83f8014292badc9f",
    "sf_god_athena.glb": "e0a5fb7a5b8b480cbb36fffef604b12a",
}

def get(url, hdr):
    return urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=120)

credits = []
for fn, uid in MODELS.items():
    try:
        meta = json.load(get(f"https://api.sketchfab.com/v3/models/{uid}", H))
        dl = json.load(get(f"https://api.sketchfab.com/v3/models/{uid}/download", H))
        src = dl.get("glb") or dl.get("gltf")
        if not src:
            print("no glb for", fn, list(dl)); continue
        is_zip = "glb" not in dl
        dest = os.path.join(OUT, fn + (".zip" if is_zip else ""))
        with get(src["url"], {"User-Agent": "PantheonsWrath/1.0"}) as r, open(dest, "wb") as f:
            while c := r.read(65536):
                f.write(c)
        sz = os.path.getsize(dest)
        print("OK", fn, f"{sz/1024/1024:.2f} MB", "(zip)" if is_zip else "")
        credits.append(f'- **{meta["name"]}** by {meta["user"]["displayName"]} ({meta["license"]["label"]}) — {meta["viewerUrl"]} — `{fn}`')
    except Exception as e:
        print("FAIL", fn, e)

credits_path = os.path.join(ROOT, "CREDITS.md")
existing = open(credits_path).read() if os.path.exists(credits_path) else "# Third-party 3D model credits (Sketchfab)\n\n"
with open(credits_path, "w") as f:
    f.write(existing.rstrip() + "\n" + "\n".join(credits) + "\n")
