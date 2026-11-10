"""
Updated Inscription generator with high-contrast epigraphic engraving and Khmer lotus motifs.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TEXTURE_DIR = "/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/textures/angkor_wat"
os.makedirs(TEXTURE_DIR, exist_ok=True)

def height_to_normal(height_arr, intensity=4.0):
    h, w = height_arr.shape
    height = height_arr.astype(np.float32) / 255.0
    gx = np.zeros_like(height)
    gy = np.zeros_like(height)
    gx[:, 1:-1] = (height[:, 2:] - height[:, :-2]) * 0.5 * intensity
    gx[:, 0] = (height[:, 1] - height[:, 0]) * intensity
    gx[:, -1] = (height[:, -1] - height[:, -2]) * intensity
    gy[1:-1, :] = (height[2:, :] - height[:-2, :]) * 0.5 * intensity
    gy[0, :] = (height[1, :] - height[0, :]) * intensity
    gy[-1, :] = (height[-1, :] - height[-2, :]) * intensity
    nx = -gx
    ny = gy
    nz = np.ones_like(height)
    mag = np.sqrt(nx*nx + ny*ny + nz*nz) + 1e-6
    nx /= mag
    ny /= mag
    nz /= mag
    norm_rgb = np.zeros((h, w, 3), dtype=np.uint8)
    norm_rgb[:, :, 0] = np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    norm_rgb[:, :, 1] = np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    norm_rgb[:, :, 2] = np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    return norm_rgb

def draw_khmer_lotus(draw, x, y, size):
    pts = [
        (x, y - size),
        (x + size*0.4, y - size*0.4),
        (x + size*0.7, y - size*0.1),
        (x + size*0.8, y + size*0.3),
        (x + size*0.4, y + size*0.7),
        (x, y + size),
        (x - size*0.4, y + size*0.7),
        (x - size*0.8, y + size*0.3),
        (x - size*0.7, y - size*0.1),
        (x - size*0.4, y - size*0.4)
    ]
    draw.polygon(pts, fill=220)
    inner = [(p[0]*0.55 + x*0.45, p[1]*0.55 + y*0.45) for p in pts]
    draw.polygon(inner, fill=255)

def generate_crisp_inscriptions():
    print("Regenerating crisp high-detail Inscriptions...")
    size = 2048
    canvas = Image.new("L", (size, size), 135)
    draw = ImageDraw.Draw(canvas)

    # Architectural Border Frames
    draw.rectangle([30, 30, size - 30, size - 30], outline=220, width=16)
    draw.rectangle([55, 55, size - 55, size - 55], outline=60, width=6)
    draw.rectangle([75, 75, size - 75, size - 75], outline=190, width=4)

    # Ornate top & bottom lotus bands
    for x in range(100, size - 100, 75):
        draw_khmer_lotus(draw, x, 42, 22)
        draw_khmer_lotus(draw, x, size - 42, 22)
    for y in range(100, size - 100, 75):
        draw_khmer_lotus(draw, 42, y, 22)
        draw_khmer_lotus(draw, size - 42, y, 22)

    font_path = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
    font_title = ImageFont.truetype(font_path, 54)
    font_sub = ImageFont.truetype(font_path, 40)
    font_body = ImageFont.truetype(font_path, 32)

    epigraphic_lines = [
        ("OM NAMO BHAGAVATE VASUDEVAYA", font_title, 140),
        ("PARAMAVISHNULOKA : ANGKOR WAT", font_sub, 230),
        ("REIGN OF KING SURYAVARMAN II (1113 - 1150 CE)", font_body, 310),
        ("--------------------------------------------------------------------------------", font_body, 350),
        ("VISNOR NU KAM VIRYANI PRA VOCAM YAH PARTHIVANI", font_body, 410),
        ("VIMAME RAJAMSI YO ASKABHAYAD UTTARAM SADHASTHAM", font_body, 470),
        ("VICAKRAMANAS TREDHORUGAYAH // RV I.154.1 //", font_body, 530),
        (" ", font_body, 570),
        ("PRA TAD VISNUH STAVATE VIRYENA MRGO NA BHIMAH", font_body, 620),
        ("KUCARO GIRISTHAH YASYORUSU TRISU VIKRAMANESU", font_body, 680),
        ("ADHIKSIYANTI BHUVANANI VISVA // RV I.154.2 //", font_body, 740),
        ("--------------------------------------------------------------------------------", font_body, 790),
        ("DEDICATED TO LORD VISHNU - SUPREME PRESERVER", font_sub, 850),
        ("CHATURBHUJA VISHNU : CONCH, DISCUS, MACE, LOTUS", font_body, 920),
        ("ESTABLISHED AS THE SACRED COSMIC MOUNT MERU", font_body, 980),
        ("CHURNING OF THE PRIMORDIAL OCEAN OF MILK (SAMUDRA MANTHANA)", font_body, 1040),
        ("BY 88 DEVAS AND 92 ASURAS WITH NAGA VASUKI", font_body, 1100),
        ("AND KURMA AVATAR AS THE ETERNAL PIVOT OF CREATION", font_body, 1160),
        ("--------------------------------------------------------------------------------", font_body, 1220),
        ("KAMBUJADESE PARAMESVARA PRASADA STHAPITAM", font_body, 1280),
        ("JAYATU JAYATU VISNUH SRIPATIH SARVA-LOKESVARAH", font_body, 1340),
        ("OM SHANTI SHANTI SHANTIH //", font_sub, 1420)
    ]

    for text, font, y in epigraphic_lines:
        # Calculate centered X
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        x = (size - tw) // 2

        # Chiseled V-groove effect (dark inner cut with bright bevel edge)
        draw.text((x + 2, y + 2), text, font=font, fill=220)
        draw.text((x - 1, y - 1), text, font=font, fill=30)
        draw.text((x, y), text, font=font, fill=45)

    # Ancient stone cracks and weathering
    np.random.seed(99)
    for _ in range(16):
        cx = np.random.randint(150, size - 150)
        cy = np.random.randint(150, size - 150)
        c_len = np.random.randint(60, 280)
        ang = np.random.uniform(0, math.pi * 2)
        pts = [(cx, cy)]
        for s in range(5):
            cx += int(math.cos(ang) * (c_len / 5) + np.random.randint(-12, 12))
            cy += int(math.sin(ang) * (c_len / 5) + np.random.randint(-12, 12))
            pts.append((cx, cy))
        draw.line(pts, fill=35, width=2)

    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=1.0))
    height_arr = np.array(canvas, dtype=np.uint8)

    # Normal map
    norm_rgb = height_to_normal(height_arr, intensity=5.5)
    norm_img = Image.fromarray(norm_rgb)
    norm_img.save(os.path.join(TEXTURE_DIR, "angkor_inscriptions_norm.png"))

    # Diffuse map (warm Baphuon sandstone with dark aged pigment in incisions)
    diff_arr = np.zeros((size, size, 3), dtype=np.uint8)
    base_col = np.array([178, 164, 140], dtype=np.float32)
    h_norm = height_arr.astype(np.float32) / 255.0

    for c in range(3):
        col_c = base_col[c] * (0.65 + 0.35 * h_norm)
        if c == 0:
            col_c += (1.0 - h_norm) * 35.0 # slight red ochre patina in grooves
        diff_arr[:, :, c] = np.clip(col_c, 0, 255).astype(np.uint8)

    diff_img = Image.fromarray(diff_arr)
    diff_img.save(os.path.join(TEXTURE_DIR, "angkor_inscriptions_diff.png"))
    print("Crisp Inscriptions saved successfully!")

if __name__ == "__main__":
    generate_crisp_inscriptions()
