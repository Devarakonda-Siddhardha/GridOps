#!/usr/bin/env python3
"""Search Sketchfab for downloadable, permissively licensed, game-sized models."""
import json, sys, urllib.request, urllib.parse
TOKEN = "cc7ff50739131beb1d757280c26cf6dd"
H = {"Authorization": f"Token {TOKEN}", "User-Agent": "PantheonsWrath/1.0"}
QUERIES = sys.argv[1:] or ["spartan hoplite", "roman legionary lowpoly", "greek temple", "minotaur", "demon lowpoly", "roman centurion", "greek warrior shield", "colosseum", "roman ship trireme"]
for q in QUERIES:
    params = urllib.parse.urlencode({"type": "models", "downloadable": "true", "q": q, "count": 24, "sort_by": "-likeCount", "max_face_count": 60000})
    req = urllib.request.Request("https://api.sketchfab.com/v3/search?" + params, headers=H)
    d = json.load(urllib.request.urlopen(req, timeout=30))
    print(f"\n## {q}")
    n = 0
    for r in d["results"]:
        lic = (r.get("license") or {}).get("label", "?")
        if not (lic.startswith("CC0") or lic == "CC Attribution" or lic.startswith("CC Attribution-Share")):
            continue
        print(f'{r["uid"]} | {r["name"][:45]} | {r["user"]["displayName"][:20]} | {lic} | {r["faceCount"]} faces | {r["likeCount"]} likes | anim={r.get("animationCount",0)}')
        n += 1
        if n >= 6:
            break
