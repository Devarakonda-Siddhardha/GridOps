#!/usr/bin/env python3
"""Download a curated set of Sketchfab models and write CREDITS.md (CC-BY attribution)."""
import json, os, urllib.request

TOKEN = "cc7ff50739131beb1d757280c26cf6dd"
H = {"Authorization": f"Token {TOKEN}", "User-Agent": "PantheonsWrath/1.0"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "models")

MODELS = {
    "sf_temple_greco.glb": "f3e9bae12d83436bba2f7b24f03ecf0f",
    "sf_temple_empty.glb": "1cb5bcd8cd0745d3ae7934816d0af72a",
    "sf_doric_columns.glb": "e27b5b5c101c480dbf1a9781ae289155",
    "sf_minotaur.glb": "e822f283ec9f4985a19e6d60d0b26823",
    "sf_roman_soldier.glb": "68ca46a8d10a431588211bfa060f0c41",
    "sf_spartan.glb": "4c7165bd8c164465b761e0dc2fb34fe0",
    "sf_greek_javelineer.glb": "f28e7662df474862be46ef7fbacc06a3",
    "sf_corinthian_helmet.glb": "793a3eb779454e8db5552ac934f20098",
    "sf_spartan_shield.glb": "03b51fb57d4747deb71ca22f14971dfb",
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
        print("OK", fn, os.path.getsize(dest), "bytes", "(zip)" if is_zip else "")
        credits.append(f'- **{meta["name"]}** by {meta["user"]["displayName"]} ({meta["license"]["label"]}) — {meta["viewerUrl"]} — `{fn}`')
    except Exception as e:
        print("FAIL", fn, e)

with open(os.path.join(ROOT, "CREDITS.md"), "w") as f:
    f.write("# Third-party 3D model credits (Sketchfab)\n\n" + "\n".join(credits) + "\n")
