#!/usr/bin/env python3
"""Downscale embedded images in a .glb file to max_dim (default 512) to keep APK/ZIP under 100 MB."""
import io, json, os, struct, sys
from PIL import Image

def compress_glb(path, max_dim=512):
    raw = open(path, "rb").read()
    magic, version, length = struct.unpack_from("<III", raw, 0)
    assert magic == 0x46546C67, f"Not GLB: {path}"
    j_len, j_type = struct.unpack_from("<II", raw, 12)
    assert j_type == 0x4E4F534A
    j_start = 20
    j_end = j_start + j_len
    gltf = json.loads(raw[j_start:j_end].decode("utf-8"))

    b_len, b_type = struct.unpack_from("<II", raw, j_end)
    assert b_type == 0x004E4942
    bin_data = raw[j_end + 8 : j_end + 8 + b_len]

    images = gltf.get("images", [])
    bviews = gltf.get("bufferViews", [])
    if not images:
        return

    # Map bufferView index -> replacement bytes
    replacements = {}
    for img in images:
        bv_idx = img.get("bufferView")
        if bv_idx is None:
            continue
        bv = bviews[bv_idx]
        off = bv.get("byteOffset", 0)
        ln = bv["byteLength"]
        img_bytes = bin_data[off : off + ln]
        try:
            im = Image.open(io.BytesIO(img_bytes))
            if max(im.size) > max_dim or ln > 200_000:
                im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                out = io.BytesIO()
                if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                    im.save(out, format="PNG", optimize=True)
                    img["mimeType"] = "image/png"
                else:
                    im.convert("RGB").save(out, format="JPEG", quality=82, optimize=True)
                    img["mimeType"] = "image/jpeg"
                replacements[bv_idx] = out.getvalue()
        except Exception:
            pass

    if not replacements:
        return

    # Rebuild BIN chunk updating offsets
    new_bin = bytearray()
    for i, bv in enumerate(bviews):
        # 4-byte align
        while len(new_bin) % 4 != 0:
            new_bin.append(0)
        old_off = bv.get("byteOffset", 0)
        old_len = bv["byteLength"]
        chunk = replacements.get(i, bin_data[old_off : old_off + old_len])
        bv["byteOffset"] = len(new_bin)
        bv["byteLength"] = len(chunk)
        new_bin.extend(chunk)
    while len(new_bin) % 4 != 0:
        new_bin.append(0)

    gltf["buffers"][0]["byteLength"] = len(new_bin)
    j_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(j_bytes) % 4 != 0:
        j_bytes += b" "

    total_len = 12 + 8 + len(j_bytes) + 8 + len(new_bin)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total_len))
        f.write(struct.pack("<II", len(j_bytes), 0x4E4F534A))
        f.write(j_bytes)
        f.write(struct.pack("<II", len(new_bin), 0x004E4942))
        f.write(new_bin)
    print(f"Compressed {os.path.basename(path)}: {len(raw)/1024/1024:.2f} MB -> {total_len/1024/1024:.2f} MB")

for p in sys.argv[1:]:
    compress_glb(p, 512)
