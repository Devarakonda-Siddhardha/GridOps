#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TOKEN = "cc7ff50739131beb1d757280c26cf6dd"
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "User-Agent": "PantheonsWrath-SketchfabClient/1.0"
}

MODELS_TO_DOWNLOAD = {
    "roman_ballista.glb": "a92a4eb4ab04409dbf40344f5f63925a",
    "roman_catapult.glb": "099ca4d90a744218a1d58b55881c57db",
    "military_tent.glb": "47a5b7469e814e4a81dfdde1852adca1",
    "greek_column_ruin.glb": "42e55f2c7fdc40e0be6e1e9ce041c886",
    "trojan_horse.glb": "fdc93f7871864de19c017a129827dedb",
    "gladiator_helmet.glb": "5bbb87d48f7d4dcd81eb7883fbc89b89"
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "models")

def download_model(filename, uid):
    dest_path = os.path.join(OUTPUT_DIR, filename)
    print(f"[*] Processing {filename} ({uid})...")
    url = f"https://api.sketchfab.com/v3/models/{uid}/download"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        # Check for GLB direct download
        if "glb" in data and "url" in data["glb"]:
            download_url = data["glb"]["url"]
            print(f"    Downloading GLB ({data['glb'].get('size', 0)} bytes)...")
        elif "gltf" in data and "url" in data["gltf"]:
            download_url = data["gltf"]["url"]
            print(f"    Downloading GLTF zip...")
        else:
            print(f"    [!] No glb/gltf URL found in response: {list(data.keys())}")
            return False

        # Download file
        dl_req = urllib.request.Request(download_url, headers={"User-Agent": "PantheonsWrath-SketchfabClient/1.0"})
        with urllib.request.urlopen(dl_req) as dl_resp, open(dest_path, "wb") as out_file:
            while chunk := dl_resp.read(65536):
                out_file.write(chunk)
        
        file_size = os.path.getsize(dest_path)
        print(f"    [+] Saved {dest_path} ({file_size} bytes)")
        return True
    except Exception as e:
        print(f"    [!] Failed to download {filename}: {e}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    success = 0
    for filename, uid in MODELS_TO_DOWNLOAD.items():
        if download_model(filename, uid):
            success += 1
    print(f"Finished: {success}/{len(MODELS_TO_DOWNLOAD)} models downloaded.")

if __name__ == "__main__":
    main()
