"""
Generate complete AAA 3D model of Angkor Wat in Blender:
- Paramavishnuloka: The Ancient Temple Mountain of Lord Vishnu
- Complete architectural hierarchy:
  1. Outer Moat, Embankments & Grand Western Causeway with Naga Balustrades & Guardian Lions
  2. Western Monumental Gopura (Gatehouse) with 3 tiered towers & Elephant Passageways
  3. Grand Processional Avenue with North & South Libraries and Sacred Reflection Pools
  4. First Enclosure (Gallery of Bas-Reliefs) with colonnade, corbelled roofs, and the epic
     'Churning of the Ocean of Milk' (Samudra Manthana) narrative frieze
  5. Ancient Epigraphic Inscriptions in Sanskrit & Old Khmer honoring Lord Vishnu
  6. Preah Poan (Cruciform Cloister) with four sunken courtyard basins
  7. Second Enclosure (Middle Terrace) with corner towers, blind balustered windows, & Apsara niches
  8. Third Enclosure (The Bakan - Mount Meru) with stepped pyramid, 12 steep staircases,
     and the iconic Quincunx of 5 Lotus Prasat Towers
  9. Central Sanctum (Garbhagriha) with the 4-armed Lord Vishnu (Chaturbhuja Vishnu)
     holding Shankha, Chakra, Gada, and Padma, adorned in royal Khmer regalia
  10. PBR Materials with Seamless Box-Projected Textures, Cinematic Sunrise Lighting, 
      6 Camera angles, High-Res Renders, and GLB Export
"""

import bpy
import bmesh
import math
import mathutils
import os
import sys

# Base directory paths
BASE_DIR = "/home/antigravity/Devarakonda-Siddhardha/GridOps"
TEXTURE_DIR = os.path.join(BASE_DIR, "assets/textures/angkor_wat")
RENDER_DIR = os.path.join(BASE_DIR, "assets/renders/angkor_wat")
MODEL_DIR = os.path.join(BASE_DIR, "assets/models")
os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

def log(msg):
    print(f"[AngkorWat] {msg}", flush=True)

def clear_scene():
    log("Clearing existing scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def setup_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def set_active_collection(col):
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[col.name]

# -------------------------------------------------------------------------
# Material & Shader Network Creation with Box-Projected Texturing
# -------------------------------------------------------------------------
def create_pbr_material(name, diff_tex=None, norm_tex=None, rough_tex=None, 
                        base_color=(0.65, 0.60, 0.52, 1.0), roughness=0.8, metallic=0.0,
                        tex_scale=0.15):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_out.location = (600, 0)

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    # Box-projection coordinates & mapping for seamless texturing
    node_coord = nodes.new(type="ShaderNodeTexCoord")
    node_coord.location = (-800, 0)

    node_mapping = nodes.new(type="ShaderNodeMapping")
    node_mapping.location = (-600, 0)
    node_mapping.inputs["Scale"].default_value = (tex_scale, tex_scale, tex_scale)
    links.new(node_coord.outputs["Object"], node_mapping.inputs["Vector"])

    x_offset = -300
    if diff_tex and os.path.exists(diff_tex):
        img_diff = bpy.data.images.load(diff_tex)
        node_diff = nodes.new(type="ShaderNodeTexImage")
        node_diff.image = img_diff
        node_diff.projection = 'BOX'
        node_diff.projection_blend = 0.15
        node_diff.location = (x_offset, 250)
        links.new(node_mapping.outputs["Vector"], node_diff.inputs["Vector"])
        links.new(node_diff.outputs["Color"], bsdf.inputs["Base Color"])

    if rough_tex and os.path.exists(rough_tex):
        img_rough = bpy.data.images.load(rough_tex)
        img_rough.colorspace_settings.name = 'Non-Color'
        node_rough = nodes.new(type="ShaderNodeTexImage")
        node_rough.image = img_rough
        node_rough.projection = 'BOX'
        node_rough.projection_blend = 0.15
        node_rough.location = (x_offset, -50)
        links.new(node_mapping.outputs["Vector"], node_rough.inputs["Vector"])
        links.new(node_rough.outputs["Color"], bsdf.inputs["Roughness"])

    if norm_tex and os.path.exists(norm_tex):
        img_norm = bpy.data.images.load(norm_tex)
        img_norm.colorspace_settings.name = 'Non-Color'
        node_norm_tex = nodes.new(type="ShaderNodeTexImage")
        node_norm_tex.image = img_norm
        node_norm_tex.projection = 'BOX'
        node_norm_tex.projection_blend = 0.15
        node_norm_tex.location = (x_offset, -350)

        node_norm_map = nodes.new(type="ShaderNodeNormalMap")
        node_norm_map.location = (0, -350)
        node_norm_map.inputs["Strength"].default_value = 1.8
        links.new(node_mapping.outputs["Vector"], node_norm_tex.inputs["Vector"])
        links.new(node_norm_tex.outputs["Color"], node_norm_map.inputs["Color"])
        links.new(node_norm_map.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def create_water_material(name="Mat_Sacred_Water"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.04, 0.12, 0.16, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.04
    bsdf.inputs["Metallic"].default_value = 0.15
    bsdf.inputs["IOR"].default_value = 1.333

    tex_noise = nodes.new(type="ShaderNodeTexNoise")
    tex_noise.inputs["Scale"].default_value = 12.0
    tex_noise.inputs["Detail"].default_value = 2.0
    tex_noise.location = (-400, -200)

    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.015
    bump.inputs["Distance"].default_value = 0.1
    bump.location = (-150, -200)

    links.new(tex_noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    return mat

def create_gold_material(name="Mat_Khmer_Gold"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.95, 0.78, 0.22, 1.0)
        bsdf.inputs["Metallic"].default_value = 0.95
        bsdf.inputs["Roughness"].default_value = 0.2
    return mat

def create_vishnu_stone_material(name="Mat_Vishnu_Deity"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Deep consecrated black granite / basalt with sacred oil sheen
        bsdf.inputs["Base Color"].default_value = (0.045, 0.045, 0.052, 1.0)
        bsdf.inputs["Metallic"].default_value = 0.10
        bsdf.inputs["Roughness"].default_value = 0.20
    return mat

def create_basic_color_material(name, color, roughness=0.3, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

def create_lawn_material(name="Mat_Tropical_Lawn"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.16, 0.28, 0.10, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    return mat

# -------------------------------------------------------------------------
# Fast Mesh Helper Functions
# -------------------------------------------------------------------------
def add_cube_mesh(bm, center, size):
    cx, cy, cz = center
    sx, sy, sz = size[0]/2, size[1]/2, size[2]/2
    v1 = bm.verts.new((cx - sx, cy - sy, cz - sz))
    v2 = bm.verts.new((cx + sx, cy - sy, cz - sz))
    v3 = bm.verts.new((cx + sx, cy + sy, cz - sz))
    v4 = bm.verts.new((cx - sx, cy + sy, cz - sz))
    v5 = bm.verts.new((cx - sx, cy - sy, cz + sz))
    v6 = bm.verts.new((cx + sx, cy - sy, cz + sz))
    v7 = bm.verts.new((cx + sx, cy + sy, cz + sz))
    v8 = bm.verts.new((cx - sx, cy + sy, cz + sz))
    bm.faces.new((v1, v4, v3, v2))
    bm.faces.new((v5, v6, v7, v8))
    bm.faces.new((v1, v2, v6, v5))
    bm.faces.new((v2, v3, v7, v6))
    bm.faces.new((v3, v4, v8, v7))
    bm.faces.new((v4, v1, v5, v8))

def add_cylinder_mesh(bm, center, radius, depth, segments=12):
    cx, cy, cz = center
    half_d = depth / 2.0
    bot_verts = []
    top_verts = []
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        x = cx + math.cos(ang) * radius
        y = cy + math.sin(ang) * radius
        bot_verts.append(bm.verts.new((x, y, cz - half_d)))
        top_verts.append(bm.verts.new((x, y, cz + half_d)))
    
    bm.faces.new(reversed(bot_verts))
    bm.faces.new(top_verts)
    for i in range(segments):
        next_i = (i + 1) % segments
        bm.faces.new((bot_verts[i], bot_verts[next_i], top_verts[next_i], top_verts[i]))

def add_disc_x(bm, center, radius, thickness, segments=16):
    cx, cy, cz = center
    half_t = thickness / 2.0
    bot_verts = []
    top_verts = []
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        y = cy + math.cos(ang) * radius
        z = cz + math.sin(ang) * radius
        bot_verts.append(bm.verts.new((cx - half_t, y, z)))
        top_verts.append(bm.verts.new((cx + half_t, y, z)))
    bm.faces.new(reversed(bot_verts))
    bm.faces.new(top_verts)
    for i in range(segments):
        next_i = (i + 1) % segments
        bm.faces.new((bot_verts[i], bot_verts[next_i], top_verts[next_i], top_verts[i]))

def add_tube_segment(bm, p1, p2, radius, segments=8):
    v1 = mathutils.Vector(p1)
    v2 = mathutils.Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-4:
        return
    center = (v1 + v2) / 2.0
    dir_norm = diff.normalized()
    up = 'X' if abs(dir_norm.y) > 0.9 else 'Y'
    rot = dir_norm.to_track_quat('Z', up).to_matrix()
    
    bot_verts = []
    top_verts = []
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        lx = math.cos(ang) * radius
        ly = math.sin(ang) * radius
        b_pt = rot @ mathutils.Vector((lx, ly, -length/2)) + center
        t_pt = rot @ mathutils.Vector((lx, ly,  length/2)) + center
        bot_verts.append(bm.verts.new(b_pt))
        top_verts.append(bm.verts.new(t_pt))
        
    bm.faces.new(reversed(bot_verts))
    bm.faces.new(top_verts)
    for i in range(segments):
        next_i = (i + 1) % segments
        bm.faces.new((bot_verts[i], bot_verts[next_i], top_verts[next_i], top_verts[i]))

def add_corbelled_roof_mesh(bm, center, length, width, height, orientation='X'):
    cx, cy, cz = center
    steps = 5
    dx = length / 2
    dy = width / 2
    for s in range(steps):
        t0 = s / steps
        t1 = (s + 1) / steps
        z0 = cz + t0 * height
        z1 = cz + t1 * height
        fac0 = 1.0 - (t0 ** 1.35) * 0.72
        fac1 = 1.0 - (t1 ** 1.35) * 0.72
        if orientation == 'X':
            w0 = dy * fac0
            w1 = dy * fac1
            v1 = bm.verts.new((cx - dx, cy - w0, z0))
            v2 = bm.verts.new((cx + dx, cy - w0, z0))
            v3 = bm.verts.new((cx + dx, cy + w0, z0))
            v4 = bm.verts.new((cx - dx, cy + w0, z0))
            v5 = bm.verts.new((cx - dx, cy - w1, z1))
            v6 = bm.verts.new((cx + dx, cy - w1, z1))
            v7 = bm.verts.new((cx + dx, cy + w1, z1))
            v8 = bm.verts.new((cx - dx, cy + w1, z1))
        else:
            w0 = dx * fac0
            w1 = dx * fac1
            v1 = bm.verts.new((cx - w0, cy - dy, z0))
            v2 = bm.verts.new((cx + w0, cy - dy, z0))
            v3 = bm.verts.new((cx + w0, cy + dy, z0))
            v4 = bm.verts.new((cx - w0, cy + dy, z0))
            v5 = bm.verts.new((cx - w1, cy - dy, z1))
            v6 = bm.verts.new((cx + w1, cy - dy, z1))
            v7 = bm.verts.new((cx + w1, cy + dy, z1))
            v8 = bm.verts.new((cx - w1, cy + dy, z1))

        bm.faces.new((v1, v2, v6, v5))
        bm.faces.new((v2, v3, v7, v6))
        bm.faces.new((v3, v4, v8, v7))
        bm.faces.new((v4, v1, v5, v8))
        if s == steps - 1:
            bm.faces.new((v5, v6, v7, v8))

def create_mesh_object(name, bm, material=None):
    me = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

# -------------------------------------------------------------------------
# Architectural Builders
# -------------------------------------------------------------------------
def build_prasat_tower_obj(name, location, base_w, total_h, tiers, mat_stone, mat_gold, is_central=False):
    bm_stone = bmesh.new()
    bm_gold = bmesh.new()
    lx, ly, lz = location
    half_w = base_w / 2.0
    current_z = lz

    # 1. Base Sanctuary Core
    base_h = total_h * 0.26
    if is_central:
        # Central sanctuary has a hollow Garbhagriha chamber!
        wall_t = 1.2
        # North & South walls
        add_cube_mesh(bm_stone, (lx, ly + half_w - wall_t/2, current_z + base_h/2), (half_w*2, wall_t, base_h))
        add_cube_mesh(bm_stone, (lx, ly - half_w + wall_t/2, current_z + base_h/2), (half_w*2, wall_t, base_h))
        # East wall
        add_cube_mesh(bm_stone, (lx + half_w - wall_t/2, ly, current_z + base_h/2), (wall_t, half_w*2 - wall_t*2, base_h))
        # West wall with open doorway
        door_w = 2.6
        door_h = 5.6
        side_w = (half_w*2 - wall_t*2 - door_w) / 2
        add_cube_mesh(bm_stone, (lx - half_w + wall_t/2, ly + door_w/2 + side_w/2, current_z + base_h/2), (wall_t, side_w, base_h))
        add_cube_mesh(bm_stone, (lx - half_w + wall_t/2, ly - door_w/2 - side_w/2, current_z + base_h/2), (wall_t, side_w, base_h))
        add_cube_mesh(bm_stone, (lx - half_w + wall_t/2, ly, current_z + door_h + (base_h - door_h)/2), (wall_t, door_w, base_h - door_h))
    else:
        # Solid core for subsidiary towers
        add_cube_mesh(bm_stone, (lx, ly, current_z + base_h/2), (half_w*1.64, half_w*1.64, base_h))
        pw = half_w * 1.2
        pe = half_w * 0.3
        add_cube_mesh(bm_stone, (lx, ly + half_w + pe/2, current_z + base_h*0.45), (pw, pe, base_h*0.9))
        add_cube_mesh(bm_stone, (lx, ly - half_w - pe/2, current_z + base_h*0.45), (pw, pe, base_h*0.9))
        add_cube_mesh(bm_stone, (lx + half_w + pe/2, ly, current_z + base_h*0.45), (pe, pw, base_h*0.9))
        add_cube_mesh(bm_stone, (lx - half_w - pe/2, ly, current_z + base_h*0.45), (pe, pw, base_h*0.9))

    # Cornice
    current_z += base_h
    add_cube_mesh(bm_stone, (lx, ly, current_z + 0.25), (half_w*1.9, half_w*1.9, 0.5))
    current_z += 0.5

    # 2. Diminishing Tiers of the Lotus Shikhara
    remaining_h = total_h - (current_z - lz) - (total_h * 0.16)
    tier_h = remaining_h / tiers

    for t in range(tiers):
        t_fac = t / tiers
        curve = math.sin(t_fac * math.pi * 0.5) ** 1.45
        tier_w = half_w * (0.88 - curve * 0.65) * 2.0
        tz = current_z + t * tier_h

        add_cube_mesh(bm_stone, (lx, ly, tz + tier_h*0.4), (tier_w, tier_w, tier_h*0.8))
        proj = tier_w * 0.18
        add_cube_mesh(bm_stone, (lx, ly, tz + tier_h*0.4), (tier_w + proj*2, tier_w*0.72, tier_h*0.76))
        add_cube_mesh(bm_stone, (lx, ly, tz + tier_h*0.4), (tier_w*0.72, tier_w + proj*2, tier_h*0.76))
        add_cube_mesh(bm_stone, (lx, ly, tz + tier_h*0.88), (tier_w*1.08, tier_w*1.08, tier_h*0.24))

        af_sz = tier_w * 0.18
        af_z = tz + tier_h * 0.8
        for sx in (-1, 1):
            for sy in (-1, 1):
                add_cube_mesh(bm_stone, (lx + sx * tier_w * 0.46, ly + sy * tier_w * 0.46, af_z), (af_sz, af_sz, tier_h * 0.6))

    # 3. Crowning Lotus Bud & Amalaka Cap
    current_z += remaining_h
    add_cylinder_mesh(bm_stone, (lx, ly, current_z + 0.6), radius=half_w*0.36, depth=1.2, segments=16)
    current_z += 1.2

    bulb_r = half_w * 0.28
    add_cylinder_mesh(bm_stone, (lx, ly, current_z + 0.5), radius=bulb_r, depth=1.0, segments=16)
    add_cylinder_mesh(bm_stone, (lx, ly, current_z + 1.2), radius=bulb_r*0.65, depth=0.8, segments=16)
    current_z += 1.6

    # 4. Sacred Finial (Gold)
    if is_central:
        add_cylinder_mesh(bm_gold, (lx, ly, current_z + 0.4), radius=bulb_r*0.4, depth=0.8, segments=12)
        add_cylinder_mesh(bm_gold, (lx, ly, current_z + 1.4), radius=0.08, depth=1.8, segments=8)
        # Trident prongs
        add_cylinder_mesh(bm_gold, (lx, ly, current_z + 2.5), radius=0.06, depth=0.8, segments=8)
        add_cylinder_mesh(bm_gold, (lx - 0.22, ly, current_z + 2.3), radius=0.05, depth=0.6, segments=8)
        add_cylinder_mesh(bm_gold, (lx + 0.22, ly, current_z + 2.3), radius=0.05, depth=0.6, segments=8)
    else:
        add_cylinder_mesh(bm_gold, (lx, ly, current_z + 0.6), radius=bulb_r*0.35, depth=1.2, segments=12)

    stone_obj = create_mesh_object(f"{name}_Stone", bm_stone, mat_stone)
    gold_obj = create_mesh_object(f"{name}_Gold", bm_gold, mat_gold)
    gold_obj.parent = stone_obj
    return stone_obj

def build_gallery_unified(name, start_pt, end_pt, width, height, mat_stone, mat_relief=None, has_colonnade=True):
    bm_stone = bmesh.new()
    bm_relief = bmesh.new() if mat_relief else None

    dx = end_pt[0] - start_pt[0]
    dy = end_pt[1] - start_pt[1]
    length = math.hypot(dx, dy)
    mid_x = (start_pt[0] + end_pt[0]) / 2.0
    mid_y = (start_pt[1] + end_pt[1]) / 2.0
    angle = math.atan2(dy, dx)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    orient = 'X' if abs(cos_a) > abs(sin_a) else 'Y'
    add_cube_mesh(bm_stone, (0, 0, 0.25), (length, width, 0.5))
    add_corbelled_roof_mesh(bm_stone, (0, 0, height), length=length, width=width, height=height*0.35, orientation=orient)

    if has_colonnade:
        col_spacing = 3.2
        num_cols = max(2, int(length / col_spacing))
        col_off_y = (width / 2.0) - 0.45
        radius = 0.22
        shaft_h = height - 0.7
        for i in range(num_cols):
            t = (i + 0.5) / num_cols
            col_x = (t - 0.5) * length
            add_cube_mesh(bm_stone, (col_x, col_off_y, 0.3), (radius*2.8, radius*2.8, 0.24))
            add_cube_mesh(bm_stone, (col_x, col_off_y, 0.35 + shaft_h/2), (radius*2, radius*2, shaft_h))
            cap_z = 0.35 + shaft_h
            add_cube_mesh(bm_stone, (col_x, col_off_y, cap_z + 0.1), (radius*2.6, radius*2.6, 0.16))
            add_cube_mesh(bm_stone, (col_x, col_off_y, cap_z + 0.25), (radius*3.2, radius*3.2, 0.12))

    wall_off_y = -(width / 2.0) + 0.25
    target_bm = bm_relief if bm_relief else bm_stone
    add_cube_mesh(target_bm, (0, wall_off_y, (height - 0.5)/2.0 + 0.5), (length, 0.35, height - 0.5))

    gal_obj = create_mesh_object(f"{name}_Stone", bm_stone, mat_stone)
    gal_obj.location = (mid_x, mid_y, 0)
    gal_obj.rotation_euler = (0, 0, angle)

    if bm_relief:
        relief_obj = create_mesh_object(f"{name}_ReliefWall", bm_relief, mat_relief)
        relief_obj.location = (mid_x, mid_y, 0)
        relief_obj.rotation_euler = (0, 0, angle)
        relief_obj.parent = gal_obj

    return gal_obj

def build_naga_balustrade_fast(name, start_pt, end_pt, count, mat_stone):
    bm = bmesh.new()
    dx = end_pt[0] - start_pt[0]
    dy = end_pt[1] - start_pt[1]
    length = math.hypot(dx, dy)
    mid_x = (start_pt[0] + end_pt[0]) / 2.0
    mid_y = (start_pt[1] + end_pt[1]) / 2.0
    angle = math.atan2(dy, dx)

    add_cylinder_mesh(bm, (0, 0, 0.65), radius=0.18, depth=length, segments=10)
    for i in range(count):
        t = (i / (count - 1)) - 0.5
        add_cube_mesh(bm, (0, t * length, 0.3), (0.32, 0.32, 0.6))

    for h in range(-3, 4):
        hz = 1.0 + (3 - abs(h)) * 0.22
        add_cylinder_mesh(bm, (h * 0.16, -length/2 - 0.3, hz), radius=0.1 + (3-abs(h))*0.02, depth=0.55, segments=8)

    obj = create_mesh_object(name, bm, mat_stone)
    obj.location = (mid_x, mid_y, 0)
    obj.rotation_euler = (math.radians(90), 0, angle - math.radians(90))
    return obj

def build_steep_staircase_fast(name, location, width, depth, height, steps_count, mat_stone, rotation_z=0):
    bm = bmesh.new()
    step_d = depth / steps_count
    step_h = height / steps_count
    for i in range(steps_count):
        sz = (i + 1) * step_h
        sy = (i + 0.5) * step_d
        add_cube_mesh(bm, (0, sy, sz/2.0), (width, step_d, sz))

    add_cube_mesh(bm, (-width/2.0 - 0.15, depth/2.0, height/2.0 + 0.2), (0.3, depth, height))
    add_cube_mesh(bm, ( width/2.0 + 0.15, depth/2.0, height/2.0 + 0.2), (0.3, depth, height))

    for sx in (-1, 1):
        lx = sx * (width/2.0 + 0.45)
        add_cube_mesh(bm, (lx, -0.4, 0.3), (0.6, 0.7, 0.6))
        add_cube_mesh(bm, (lx, -0.4, 0.9), (0.5, 0.5, 0.6))
        add_cube_mesh(bm, (lx, -0.4, 1.4), (0.4, 0.4, 0.4))

    obj = create_mesh_object(name, bm, mat_stone)
    obj.location = location
    obj.rotation_euler = (0, 0, rotation_z)
    return obj

def build_library_fast(name, location, scale, rotation_z, mat_stone):
    bm = bmesh.new()
    s = scale
    add_cube_mesh(bm, (0, 0, 0.25*s), (9.0*s, 6.4*s, 0.5*s))
    add_cube_mesh(bm, (0, 0, 0.65*s), (8.0*s, 5.6*s, 0.4*s))
    add_cube_mesh(bm, (0, 0, 1.00*s), (7.2*s, 5.0*s, 0.4*s))
    add_cube_mesh(bm, (0, 0, 2.2*s), (6.4*s, 4.2*s, 2.2*s))
    add_cube_mesh(bm, (-3.6*s, 0, 1.9*s), (1.2*s, 3.0*s, 1.6*s))
    add_cube_mesh(bm, ( 3.6*s, 0, 1.9*s), (1.2*s, 3.0*s, 1.6*s))
    add_corbelled_roof_mesh(bm, (0, 0, 3.3*s), length=7.2*s, width=4.6*s, height=1.6*s, orientation='X')

    obj = create_mesh_object(name, bm, mat_stone)
    obj.location = location
    obj.rotation_euler = (0, 0, rotation_z)
    return obj

def build_chaturbhuja_vishnu_master(name, location, scale, mat_deity, mat_gold, mat_white, mat_red, mat_pink, mat_inscriptions):
    bm_deity = bmesh.new()
    bm_gold = bmesh.new()
    bm_white = bmesh.new()
    bm_red = bmesh.new()
    bm_pink = bmesh.new()
    bm_insc = bmesh.new()
    s = scale

    # 1. Bhadra-pitha & Padma-pitha (Tiered Lotus Pedestal)
    # Square stone base
    add_cube_mesh(bm_deity, (0, 0, 0.2*s), (2.2*s, 2.2*s, 0.4*s))
    # Stepped circular plinth
    add_cylinder_mesh(bm_deity, (0, 0, 0.45*s), radius=1.05*s, depth=0.15*s, segments=24)
    # Golden lotus pedestal
    add_cylinder_mesh(bm_gold, (0, 0, 0.60*s), radius=0.92*s, depth=0.18*s, segments=24)
    # 16 Golden & Pink lotus petals around pedestal rim
    for i in range(16):
        ang = 2 * math.pi * i / 16
        px = math.cos(ang) * 0.90 * s
        py = math.sin(ang) * 0.90 * s
        add_cube_mesh(bm_pink, (px, py, 0.62*s), (0.24*s, 0.16*s, 0.12*s))
        add_cube_mesh(bm_gold, (px*0.95, py*0.95, 0.65*s), (0.16*s, 0.12*s, 0.08*s))

    # 2. Lotus Feet (Charana Kamala) in Samabhanga Stance
    add_cylinder_mesh(bm_deity, (0.05*s, -0.22*s, 0.72*s), radius=0.14*s, depth=0.12*s, segments=12)
    add_cylinder_mesh(bm_deity, (0.05*s,  0.22*s, 0.72*s), radius=0.14*s, depth=0.12*s, segments=12)
    # Feet toes extending forward (-X)
    add_cube_mesh(bm_deity, (-0.08*s, -0.22*s, 0.72*s), (0.22*s, 0.18*s, 0.10*s))
    add_cube_mesh(bm_deity, (-0.08*s,  0.22*s, 0.72*s), (0.22*s, 0.18*s, 0.10*s))
    # Golden Anklets (Nupura)
    add_cylinder_mesh(bm_gold, (0.05*s, -0.22*s, 0.80*s), radius=0.16*s, depth=0.06*s, segments=16)
    add_cylinder_mesh(bm_gold, (0.05*s,  0.22*s, 0.80*s), radius=0.16*s, depth=0.06*s, segments=16)

    # 3. Lower Legs & Pleated Royal Sampot (Dhoti)
    # Shins
    add_tube_segment(bm_deity, (0.04*s, -0.22*s, 0.82*s), (0.02*s, -0.22*s, 1.8*s), radius=0.14*s, segments=12)
    add_tube_segment(bm_deity, (0.04*s,  0.22*s, 0.82*s), (0.02*s,  0.22*s, 1.8*s), radius=0.14*s, segments=12)
    # Thighs
    add_tube_segment(bm_deity, (0.02*s, -0.22*s, 1.8*s), (0.0, -0.20*s, 2.7*s), radius=0.18*s, segments=12)
    add_tube_segment(bm_deity, (0.02*s,  0.22*s, 1.8*s), (0.0,  0.20*s, 2.7*s), radius=0.18*s, segments=12)
    # Royal Sampot draped over thighs with pleat folds
    add_cylinder_mesh(bm_deity, (0, 0, 2.2*s), radius=0.40*s, depth=1.1*s, segments=16)
    # Delicate pleat ridges along front and sides
    for pl_ang in (-0.6, -0.3, 0.0, 0.3, 0.6):
        pl_x = -math.cos(pl_ang) * 0.40 * s
        pl_y = math.sin(pl_ang) * 0.40 * s
        add_cube_mesh(bm_gold, (pl_x, pl_y, 2.2*s), (0.04*s, 0.05*s, 1.0*s))
    # Golden Jeweled Belt (Katisutra / Mekhala)
    add_cylinder_mesh(bm_gold, (0, 0, 2.75*s), radius=0.42*s, depth=0.15*s, segments=20)
    add_cylinder_mesh(bm_gold, (0, 0, 2.88*s), radius=0.44*s, depth=0.08*s, segments=20)
    # Central Lion-head buckle & Hanging Sash (Urujala)
    add_cube_mesh(bm_gold, (-0.43*s, 0, 2.80*s), (0.10*s, 0.18*s, 0.18*s))
    add_cube_mesh(bm_gold, (-0.42*s, 0, 2.30*s), (0.05*s, 0.14*s, 0.85*s))

    # 4. Torso, Divine Chest & Sacred Thread
    # Slender waist (Damaru waist / Simha-kati)
    add_cylinder_mesh(bm_deity, (0, 0, 3.10*s), radius=0.34*s, depth=0.45*s, segments=16)
    # Auspicious Navel (Nabhi)
    add_cylinder_mesh(bm_gold, (-0.33*s, 0, 3.08*s), radius=0.04*s, depth=0.03*s, segments=8)
    # Broad athletic chest (Uras)
    add_cylinder_mesh(bm_deity, (0, 0, 3.55*s), radius=0.44*s, depth=0.55*s, segments=16)
    # Defined pectoral muscles
    add_cylinder_mesh(bm_deity, (-0.08*s, -0.16*s, 3.65*s), radius=0.20*s, depth=0.22*s, segments=12)
    add_cylinder_mesh(bm_deity, (-0.08*s,  0.16*s, 3.65*s), radius=0.20*s, depth=0.22*s, segments=12)

    # Yajnopavita (Sacred Three-Strand Thread from left shoulder to right hip)
    add_tube_segment(bm_gold, (0.02*s, -0.32*s, 3.90*s), (-0.28*s, -0.12*s, 3.60*s), radius=0.025*s, segments=6)
    add_tube_segment(bm_gold, (-0.28*s, -0.12*s, 3.60*s), (-0.32*s, 0.10*s, 3.20*s), radius=0.025*s, segments=6)
    add_tube_segment(bm_gold, (-0.32*s, 0.10*s, 3.20*s), (0.02*s, 0.36*s, 2.82*s), radius=0.025*s, segments=6)

    # Kaustubha Mani & Royal Necklaces (Hara)
    add_cylinder_mesh(bm_gold, (0, 0, 3.82*s), radius=0.36*s, depth=0.14*s, segments=20)
    add_cylinder_mesh(bm_gold, (-0.36*s, 0, 3.75*s), radius=0.10*s, depth=0.06*s, segments=12) # Medallion
    add_cylinder_mesh(bm_red, (-0.39*s, 0, 3.75*s), radius=0.05*s, depth=0.05*s, segments=8) # Kaustubha Gem!

    # Vanamala (Garland of Flowers cascading past knees)
    for side_m in (-1, 1):
        add_tube_segment(bm_gold, (0, side_m*0.38*s, 3.85*s), (-0.20*s, side_m*0.42*s, 3.0*s), radius=0.035*s, segments=6)
        add_tube_segment(bm_gold, (-0.20*s, side_m*0.42*s, 3.0*s), (-0.18*s, side_m*0.36*s, 2.0*s), radius=0.035*s, segments=6)
        add_tube_segment(bm_gold, (-0.18*s, side_m*0.36*s, 2.0*s), (-0.10*s, side_m*0.28*s, 1.4*s), radius=0.035*s, segments=6)
    # Joining bottom garland loop
    add_tube_segment(bm_gold, (-0.10*s, -0.28*s, 1.4*s), (-0.15*s, 0, 1.35*s), radius=0.035*s, segments=6)
    add_tube_segment(bm_gold, (-0.15*s, 0, 1.35*s), (-0.10*s, 0.28*s, 1.4*s), radius=0.035*s, segments=6)

    # 5. Neck & Serene Divine Face
    # Neck with Tri-rekha rings
    add_cylinder_mesh(bm_deity, (0, 0, 4.08*s), radius=0.22*s, depth=0.28*s, segments=16)
    for r_z in (4.00, 4.08, 4.16):
        add_cylinder_mesh(bm_gold, (0, 0, r_z*s), radius=0.23*s, depth=0.02*s, segments=16)
    # Head core (extending up through forehead)
    add_cylinder_mesh(bm_deity, (0, 0, 4.55*s), radius=0.25*s, depth=0.75*s, segments=20)
    # Cheeks & Chin
    add_cube_mesh(bm_deity, (-0.12*s, 0, 4.28*s), (0.16*s, 0.22*s, 0.16*s)) # Chin
    # Serene smiling lips (Khmer divine smile)
    add_cube_mesh(bm_deity, (-0.22*s, 0, 4.36*s), (0.06*s, 0.14*s, 0.05*s)) # Lip ridge
    add_cube_mesh(bm_red,   (-0.23*s, 0, 4.36*s), (0.03*s, 0.10*s, 0.03*s)) # Subtle red smile
    # Aristocratic straight nose (Nasika)
    add_cube_mesh(bm_deity, (-0.24*s, 0, 4.54*s), (0.10*s, 0.06*s, 0.24*s))
    # Almond-shaped meditative eyes (Kamalanayana)
    add_cube_mesh(bm_white, (-0.21*s, -0.09*s, 4.60*s), (0.04*s, 0.08*s, 0.035*s))
    add_cube_mesh(bm_white, (-0.21*s,  0.09*s, 4.60*s), (0.04*s, 0.08*s, 0.035*s))
    add_cube_mesh(bm_deity, (-0.22*s, -0.09*s, 4.60*s), (0.03*s, 0.03*s, 0.035*s)) # Pupil
    add_cube_mesh(bm_deity, (-0.22*s,  0.09*s, 4.60*s), (0.03*s, 0.03*s, 0.035*s)) # Pupil
    # Arched Eyebrows (Bhrulata)
    add_cube_mesh(bm_deity, (-0.24*s, -0.09*s, 4.68*s), (0.04*s, 0.09*s, 0.02*s))
    add_cube_mesh(bm_deity, (-0.24*s,  0.09*s, 4.68*s), (0.04*s, 0.09*s, 0.02*s))

    # --- 6. SACRED URDHVAPUNDRA (उर्ध्वपुण्ड्र / VAISHNAVA TILAKA) ---
    # Centered proudly on the forehead above the nose bridge
    # White 'U' shaped outer prongs (Gopichandana)
    add_cube_mesh(bm_white, (-0.258*s,  0.0,     4.70*s), (0.02*s, 0.075*s, 0.03*s)) # Base connecting bridge
    add_cube_mesh(bm_white, (-0.258*s,  0.0,     4.66*s), (0.02*s, 0.024*s, 0.04*s)) # Downward nasal stem
    add_cube_mesh(bm_white, (-0.258*s,  0.032*s, 4.82*s), (0.02*s, 0.016*s, 0.22*s)) # Left upright prong
    add_cube_mesh(bm_white, (-0.258*s, -0.032*s, 4.82*s), (0.02*s, 0.016*s, 0.22*s)) # Right upright prong
    # Red Sri-churnam streak (Lakshmi sacred vermilion in exact center!)
    add_cube_mesh(bm_red,   (-0.264*s,  0.0,     4.81*s), (0.02*s, 0.012*s, 0.26*s))

    # 7. Kiriṭa-Makuṭa (Conical Royal Crown) & Makara-Kundala Earrings
    add_cylinder_mesh(bm_gold, (0, 0, 4.98*s), radius=0.26*s, depth=0.16*s, segments=20)
    add_cylinder_mesh(bm_gold, (0, 0, 5.10*s), radius=0.28*s, depth=0.08*s, segments=20)
    add_cylinder_mesh(bm_gold, (0, 0, 5.30*s), radius=0.23*s, depth=0.32*s, segments=18)
    add_cylinder_mesh(bm_gold, (0, 0, 5.58*s), radius=0.18*s, depth=0.28*s, segments=16)
    add_cylinder_mesh(bm_gold, (0, 0, 5.82*s), radius=0.13*s, depth=0.22*s, segments=14)
    add_cylinder_mesh(bm_gold, (0, 0, 5.96*s), radius=0.15*s, depth=0.08*s, segments=14)
    add_cylinder_mesh(bm_gold, (0, 0, 6.12*s), radius=0.07*s, depth=0.24*s, segments=10)
    add_cylinder_mesh(bm_gold, (0, 0, 6.28*s), radius=0.02*s, depth=0.10*s, segments=6)
    # Makara-Kundala Earrings
    for side_m in (-1, 1):
        add_cylinder_mesh(bm_gold, (0, side_m*0.27*s, 4.52*s), radius=0.05*s, depth=0.18*s, segments=8)
        add_cylinder_mesh(bm_gold, (0, side_m*0.27*s, 4.38*s), radius=0.08*s, depth=0.14*s, segments=8)

    # 8. THE FOUR DIVINE ARMS & SACRED EMBLEMS (Chaturbhuja)
    # All arms positioned laterally on the Y-axis so they frame the deity majestically!
    
    # === A. UPPER RIGHT ARM: SUDARSHANA CHAKRA (Discus) ===
    add_tube_segment(bm_deity, (0.02*s, 0.44*s, 3.82*s), (-0.02*s, 0.70*s, 3.95*s), radius=0.12*s, segments=10)
    add_cylinder_mesh(bm_gold, (-0.01*s, 0.62*s, 3.90*s), radius=0.15*s, depth=0.10*s, segments=12)
    add_tube_segment(bm_deity, (-0.02*s, 0.70*s, 3.95*s), (-0.05*s, 0.82*s, 4.60*s), radius=0.10*s, segments=10)
    add_cylinder_mesh(bm_gold, (-0.05*s, 0.82*s, 4.58*s), radius=0.12*s, depth=0.08*s, segments=12)
    add_cube_mesh(bm_deity, (-0.05*s, 0.83*s, 4.70*s), (0.12*s, 0.10*s, 0.16*s)) # Hand
    # Sudarshana Chakra: Golden Solar Discus
    ch_x = -0.05 * s
    ch_y =  0.84 * s
    ch_z =  4.90 * s
    # Hub and central Ruby bead
    add_disc_x(bm_gold, (ch_x, ch_y, ch_z), radius=0.10*s, thickness=0.06*s, segments=16)
    add_disc_x(bm_red,  (ch_x - 0.035*s, ch_y, ch_z), radius=0.04*s, thickness=0.02*s, segments=12)
    # Circular Solar Discus Wheel
    add_disc_x(bm_gold, (ch_x, ch_y, ch_z), radius=0.30*s, thickness=0.03*s, segments=24)
    # Radiating Flaming Solar Rays and Spokes
    for ray_i in range(8):
        ray_a = math.pi * ray_i / 4.0
        ry = math.cos(ray_a)
        rz = math.sin(ray_a)
        add_tube_segment(bm_gold, (ch_x, ch_y + ry*0.08*s, ch_z + rz*0.08*s), (ch_x, ch_y + ry*0.30*s, ch_z + rz*0.30*s), radius=0.015*s, segments=6)
        add_cube_mesh(bm_gold, (ch_x, ch_y + ry*0.35*s, ch_z + rz*0.35*s), (0.025*s, 0.08*s, 0.08*s))

    # === B. UPPER LEFT ARM: PANCHAJANYA SHANKHA (Conch) ===
    add_tube_segment(bm_deity, (0.02*s, -0.44*s, 3.82*s), (-0.02*s, -0.70*s, 3.95*s), radius=0.12*s, segments=10)
    add_cylinder_mesh(bm_gold, (-0.01*s, -0.62*s, 3.90*s), radius=0.15*s, depth=0.10*s, segments=12)
    add_tube_segment(bm_deity, (-0.02*s, -0.70*s, 3.95*s), (-0.05*s, -0.82*s, 4.60*s), radius=0.10*s, segments=10)
    add_cylinder_mesh(bm_gold, (-0.05*s, -0.82*s, 4.58*s), radius=0.12*s, depth=0.08*s, segments=12)
    add_cube_mesh(bm_deity, (-0.05*s, -0.83*s, 4.70*s), (0.12*s, 0.10*s, 0.16*s)) # Hand
    # Panchajanya Shankha
    sh_x = -0.05 * s
    sh_y = -0.84 * s
    sh_z =  4.88 * s
    add_cylinder_mesh(bm_white, (sh_x, sh_y, sh_z), radius=0.15*s, depth=0.34*s, segments=16)
    add_cylinder_mesh(bm_white, (sh_x, sh_y, sh_z + 0.22*s), radius=0.07*s, depth=0.18*s, segments=12)
    add_cylinder_mesh(bm_gold,  (sh_x, sh_y, sh_z + 0.32*s), radius=0.03*s, depth=0.08*s, segments=8)
    add_cube_mesh(bm_white, (sh_x - 0.08*s, sh_y, sh_z), (0.14*s, 0.18*s, 0.26*s))
    add_cube_mesh(bm_gold,  (sh_x - 0.14*s, sh_y, sh_z), (0.03*s, 0.12*s, 0.20*s))

    # === C. LOWER RIGHT ARM: KAUMODAKI GADA (Mace) ===
    add_tube_segment(bm_deity, (0.02*s, 0.42*s, 3.65*s), (-0.14*s, 0.56*s, 3.10*s), radius=0.11*s, segments=10)
    add_tube_segment(bm_deity, (-0.14*s, 0.56*s, 3.10*s), (-0.22*s, 0.64*s, 2.50*s), radius=0.10*s, segments=10)
    add_cylinder_mesh(bm_gold, (-0.22*s, 0.64*s, 2.52*s), radius=0.12*s, depth=0.08*s, segments=12)
    add_cube_mesh(bm_deity, (-0.22*s, 0.64*s, 2.44*s), (0.12*s, 0.11*s, 0.14*s)) # Hand
    # Kaumodaki Gada
    gada_x = -0.22 * s
    gada_y =  0.64 * s
    add_cylinder_mesh(bm_gold, (gada_x, gada_y, 0.88*s), radius=0.20*s, depth=0.28*s, segments=16)
    add_cylinder_mesh(bm_gold, (gada_x, gada_y, 1.10*s), radius=0.15*s, depth=0.20*s, segments=16)
    add_cylinder_mesh(bm_gold, (gada_x, gada_y, 1.80*s), radius=0.07*s, depth=1.20*s, segments=12)
    for gz in (1.35, 1.70, 2.05):
        add_cylinder_mesh(bm_gold, (gada_x, gada_y, gz*s), radius=0.09*s, depth=0.05*s, segments=12)
    add_cylinder_mesh(bm_gold, (gada_x, gada_y, 2.58*s), radius=0.10*s, depth=0.12*s, segments=12)
    add_cylinder_mesh(bm_gold, (gada_x, gada_y, 2.68*s), radius=0.04*s, depth=0.08*s, segments=8)

    # === D. LOWER LEFT ARM: PADMA (Sacred Lotus) ===
    add_tube_segment(bm_deity, (0.02*s, -0.42*s, 3.65*s), (-0.14*s, -0.54*s, 3.10*s), radius=0.11*s, segments=10)
    add_tube_segment(bm_deity, (-0.14*s, -0.54*s, 3.10*s), (-0.26*s, -0.52*s, 2.85*s), radius=0.10*s, segments=10)
    add_cylinder_mesh(bm_gold, (-0.26*s, -0.52*s, 2.88*s), radius=0.12*s, depth=0.08*s, segments=12)
    add_cube_mesh(bm_deity, (-0.28*s, -0.52*s, 2.80*s), (0.12*s, 0.11*s, 0.14*s)) # Hand
    # Blooming Padma facing forward towards viewer
    lot_stem_start = (-0.28*s, -0.52*s, 2.80*s)
    lot_base = (-0.36*s, -0.52*s, 3.02*s)
    add_tube_segment(bm_gold, lot_stem_start, lot_base, radius=0.022*s, segments=6)
    # Lotus Calyx & Golden Pericarp cup
    add_disc_x(bm_gold, (-0.38*s, -0.52*s, 3.06*s), radius=0.08*s, thickness=0.05*s, segments=16)
    add_disc_x(bm_red,  (-0.41*s, -0.52*s, 3.06*s), radius=0.03*s, thickness=0.01*s, segments=8)
    # Blooming Pink Lotus Petals facing the camera
    for pet_i in range(12):
        pet_a = 2 * math.pi * pet_i / 12.0
        pet_py = -0.52*s + math.cos(pet_a) * 0.16 * s
        pet_pz =  3.06*s + math.sin(pet_a) * 0.16 * s
        add_cube_mesh(bm_pink, (-0.39*s, pet_py, pet_pz), (0.03*s, 0.08*s, 0.08*s))
    # Inner tier of 6 pink petals
    for pet_i in range(6):
        pet_a = 2 * math.pi * pet_i / 6.0 + 0.25
        pet_py = -0.52*s + math.cos(pet_a) * 0.10 * s
        pet_pz =  3.06*s + math.sin(pet_a) * 0.10 * s
        add_cube_mesh(bm_pink, (-0.40*s, pet_py, pet_pz), (0.025*s, 0.06*s, 0.06*s))

    # 9. Prabhavali (Sacred Arch Aureole / Halo framing Lord Vishnu)
    prabh_x = 0.15 * s
    add_tube_segment(bm_gold, (prabh_x, -1.05*s, 0.75*s), (prabh_x, -1.05*s, 4.4*s), radius=0.08*s, segments=10)
    add_tube_segment(bm_gold, (prabh_x,  1.05*s, 0.75*s), (prabh_x,  1.05*s, 4.4*s), radius=0.08*s, segments=10)
    arch_pts = []
    arch_r = 1.05 * s
    arch_cz = 4.4 * s
    for ai in range(13):
        a_ang = math.pi * ai / 12.0
        ay = -math.cos(a_ang) * arch_r
        az = arch_cz + math.sin(a_ang) * arch_r * 1.55
        arch_pts.append((prabh_x, ay, az))
    for ai in range(len(arch_pts) - 1):
        add_tube_segment(bm_gold, arch_pts[ai], arch_pts[ai+1], radius=0.08*s, segments=10)
        mid_ay = (arch_pts[ai][1] + arch_pts[ai+1][1]) / 2.0
        mid_az = (arch_pts[ai][2] + arch_pts[ai+1][2]) / 2.0
        norm_y = mid_ay / arch_r
        norm_z = (mid_az - arch_cz) / (arch_r * 1.55)
        add_cube_mesh(bm_gold, (prabh_x, mid_ay + norm_y*0.14*s, mid_az + norm_z*0.14*s), (0.04*s, 0.12*s, 0.12*s))
    add_cube_mesh(bm_gold, (prabh_x, 0, arch_cz + arch_r*1.65), (0.12*s, 0.28*s, 0.28*s))

    # 10. Flanking Inscribed Stone Stelae inside sanctum (flanking North and South on Y-axis)
    add_cube_mesh(bm_insc, (0, -1.6*s, 2.0*s), (0.4*s, 0.5*s, 3.6*s))
    add_cube_mesh(bm_insc, (0,  1.6*s, 2.0*s), (0.4*s, 0.5*s, 3.6*s))

    # Create scene objects
    deity_obj = create_mesh_object(f"{name}_DeityBody", bm_deity, mat_deity)
    gold_obj = create_mesh_object(f"{name}_GoldOrnaments", bm_gold, mat_gold)
    white_obj = create_mesh_object(f"{name}_SacredWhite", bm_white, mat_white)
    red_obj = create_mesh_object(f"{name}_SacredRed", bm_red, mat_red)
    pink_obj = create_mesh_object(f"{name}_LotusPink", bm_pink, mat_pink)
    insc_obj = create_mesh_object(f"{name}_Inscriptions", bm_insc, mat_inscriptions)

    deity_obj.location = location
    for child in (gold_obj, white_obj, red_obj, pink_obj, insc_obj):
        child.parent = deity_obj
        child.matrix_parent_inverse.identity()
        child.location = (0, 0, 0)
        child.rotation_euler = (0, 0, 0)
        child.scale = (1, 1, 1)

    return deity_obj

# -------------------------------------------------------------------------
# Master Scene Assembly
# -------------------------------------------------------------------------
def build_angkor_wat():
    log("Starting Angkor Wat AAA structural construction...")
    clear_scene()

    col_terrain = setup_collection("01_Terrain_And_Moat")
    col_outer = setup_collection("02_Western_Gopura_And_Causeway")
    col_avenue = setup_collection("03_Processional_Avenue_And_Libraries")
    col_first_enc = setup_collection("04_First_Enclosure_BasReliefs")
    col_preah_poan = setup_collection("05_Cruciform_Cloister")
    col_second_enc = setup_collection("06_Second_Enclosure_Terrace")
    col_bakan = setup_collection("07_Bakan_Central_Pyramid_And_Towers")
    col_sanctum = setup_collection("08_Central_Garbhagriha_Vishnu")
    col_lighting = setup_collection("09_Lighting_And_Cameras")

    log("Loading PBR materials...")
    mat_sandstone = create_pbr_material(
        "Mat_Angkor_Sandstone",
        diff_tex=os.path.join(TEXTURE_DIR, "angkor_sandstone_diffuse.png"),
        norm_tex=os.path.join(TEXTURE_DIR, "angkor_sandstone_norm.png"),
        rough_tex=os.path.join(TEXTURE_DIR, "angkor_sandstone_rough.png"),
        roughness=0.82,
        tex_scale=0.18
    )

    # Inscription material with dedicated UV scale so epigraphic characters are crisp
    mat_inscriptions = create_pbr_material(
        "Mat_Angkor_Inscriptions",
        diff_tex=os.path.join(TEXTURE_DIR, "angkor_inscriptions_diff.png"),
        norm_tex=os.path.join(TEXTURE_DIR, "angkor_inscriptions_norm.png"),
        roughness=0.75,
        tex_scale=0.65
    )

    mat_basrelief = create_pbr_material(
        "Mat_Angkor_BasRelief",
        diff_tex=os.path.join(TEXTURE_DIR, "angkor_basrelief_samudramanthana_diff.png"),
        norm_tex=os.path.join(TEXTURE_DIR, "angkor_basrelief_samudramanthana_norm.png"),
        roughness=0.80,
        tex_scale=0.25
    )

    mat_devata = create_pbr_material(
        "Mat_Angkor_Devata",
        diff_tex=os.path.join(TEXTURE_DIR, "angkor_apsara_relief_diff.png"),
        norm_tex=os.path.join(TEXTURE_DIR, "angkor_apsara_relief_norm.png"),
        roughness=0.78,
        tex_scale=0.35
    )

    mat_laterite = create_pbr_material(
        "Mat_Angkor_Laterite",
        diff_tex=os.path.join(TEXTURE_DIR, "angkor_laterite_diff.png"),
        norm_tex=os.path.join(TEXTURE_DIR, "angkor_laterite_norm.png"),
        roughness=0.92,
        tex_scale=0.25
    )

    mat_water = create_water_material("Mat_Sacred_Water")
    mat_gold = create_gold_material("Mat_Khmer_Gold")
    mat_vishnu = create_vishnu_stone_material("Mat_Vishnu_Deity")
    mat_lawn = create_lawn_material("Mat_Tropical_Lawn")
    mat_white = create_basic_color_material("Mat_Urdhva_White", (0.98, 0.98, 0.96, 1.0), roughness=0.25)
    mat_red = create_basic_color_material("Mat_Urdhva_Red", (0.88, 0.06, 0.05, 1.0), roughness=0.30)
    mat_pink = create_basic_color_material("Mat_Lotus_Pink", (0.92, 0.42, 0.58, 1.0), roughness=0.35)

    # 1. Terrain & Moat
    log("Building 1: Terrain, Moat & Embankments...")
    set_active_collection(col_terrain)
    bm_t = bmesh.new()
    add_cube_mesh(bm_t, (0, 0, -0.4), (520, 400, 0.8))
    create_mesh_object("Sacred_Precinct_Ground", bm_t, mat_lawn)

    bm_w = bmesh.new()
    add_cube_mesh(bm_w, (-175, 0, -0.15), (70, 360, 0.3))
    create_mesh_object("Moat_West_Water", bm_w, mat_water)

    bm_lat = bmesh.new()
    add_cube_mesh(bm_lat, (-210, 0, 0.1), (3.0, 360, 1.0))
    add_cube_mesh(bm_lat, (-140, 0, 0.1), (3.0, 360, 1.0))
    create_mesh_object("Moat_Banks", bm_lat, mat_laterite)

    # 2. Western Causeway Across Moat & Outer Gopura
    log("Building 2: Western Causeway & Outer Gopura...")
    set_active_collection(col_outer)
    bm_bridge = bmesh.new()
    add_cube_mesh(bm_bridge, (-175, 0, 0.2), (70, 7.5, 0.4))
    create_mesh_object("Moat_Causeway_Bridge", bm_bridge, mat_sandstone)

    build_naga_balustrade_fast("Moat_Naga_North", (-210,  4.1), (-140,  4.1), count=14, mat_stone=mat_sandstone)
    build_naga_balustrade_fast("Moat_Naga_South", (-210, -4.1), (-140, -4.1), count=14, mat_stone=mat_sandstone)

    gopura_x = -135
    build_prasat_tower_obj("West_Gopura_Central_Prasat", (gopura_x, 0, 0.4), base_w=9.0, total_h=21.0, tiers=4, mat_stone=mat_sandstone, mat_gold=mat_gold)
    build_prasat_tower_obj("West_Gopura_North_Prasat", (gopura_x,  18.0, 0.4), base_w=7.0, total_h=16.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)
    build_prasat_tower_obj("West_Gopura_South_Prasat", (gopura_x, -18.0, 0.4), base_w=7.0, total_h=16.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)

    build_gallery_unified("West_Gopura_Gal_N", (gopura_x, 4.5), (gopura_x, 14.5), width=4.5, height=5.5, mat_stone=mat_sandstone)
    build_gallery_unified("West_Gopura_Gal_S", (gopura_x, -4.5), (gopura_x, -14.5), width=4.5, height=5.5, mat_stone=mat_sandstone)

    # 3. Processional Avenue, Libraries & Sacred Reflection Pools
    log("Building 3: Processional Avenue, Libraries & Reflection Pools...")
    set_active_collection(col_avenue)
    ave_len = 82.0
    ave_x = -130 + ave_len / 2.0
    bm_ave = bmesh.new()
    add_cube_mesh(bm_ave, (ave_x, 0, 0.45), (ave_len, 9.6, 0.9))
    mid_x = -88.0
    add_cube_mesh(bm_ave, (mid_x, 0, 0.6), (13.0, 18.0, 1.2))
    landing_x = -42.0
    add_cube_mesh(bm_ave, (landing_x, 0, 0.8), (14.0, 22.0, 1.6))
    create_mesh_object("Grand_Avenue_Terraces", bm_ave, mat_sandstone)

    build_naga_balustrade_fast("Ave_Naga_N", (-130,  5.1), (-48,  5.1), count=16, mat_stone=mat_sandstone)
    build_naga_balustrade_fast("Ave_Naga_S", (-130, -5.1), (-48, -5.1), count=16, mat_stone=mat_sandstone)

    build_library_fast("Avenue_Library_North", (mid_x,  22.0, 0), scale=1.0, rotation_z=0, mat_stone=mat_sandstone)
    build_library_fast("Avenue_Library_South", (mid_x, -22.0, 0), scale=1.0, rotation_z=0, mat_stone=mat_sandstone)

    # Reflection Pools
    pool_x = -62.0
    bm_pools = bmesh.new()
    add_cube_mesh(bm_pools, (pool_x,  24.0, -0.15), (34.0, 26.0, 0.5))
    add_cube_mesh(bm_pools, (pool_x, -24.0, -0.15), (34.0, 26.0, 0.5))
    create_mesh_object("Reflection_Pools_Water", bm_pools, mat_water)

    bm_coping = bmesh.new()
    add_cube_mesh(bm_coping, (pool_x,  24.0, 0.15), (35.2, 27.2, 0.3))
    add_cube_mesh(bm_coping, (pool_x, -24.0, 0.15), (35.2, 27.2, 0.3))
    create_mesh_object("Reflection_Pools_Coping", bm_coping, mat_sandstone)

    # Royal Inscribed Stela on Avenue Landing (Freestanding Monument for macro inspection)
    bm_stela_mon = bmesh.new()
    # Ornate stepped base
    add_cube_mesh(bm_stela_mon, (landing_x + 2.0, 4.5, 1.0), (1.4, 1.0, 0.4))
    add_cube_mesh(bm_stela_mon, (landing_x + 2.0, 4.5, 1.3), (1.1, 0.8, 0.2))
    # Inscribed Stela slab (front face facing West towards camera)
    add_cube_mesh(bm_stela_mon, (landing_x + 2.0, 4.5, 2.7), (0.24, 1.4, 2.6))
    # Carved pediment cap
    add_cube_mesh(bm_stela_mon, (landing_x + 2.0, 4.5, 4.2), (0.32, 1.5, 0.4))
    create_mesh_object("Royal_Inscribed_Stela_Suryavarman", bm_stela_mon, mat_inscriptions)

    # 4. First Enclosure (Gallery of Bas-Reliefs)
    log("Building 4: First Enclosure & Epic Bas-Relief Galleries...")
    set_active_collection(col_first_enc)
    x_min, x_max = -35.0, 75.0
    y_min, y_max = -48.0, 48.0
    enc1_h = 6.2
    gal_w = 4.4

    bm_p1 = bmesh.new()
    add_cube_mesh(bm_p1, ((x_min+x_max)/2, 0, 0.4), (x_max - x_min + 4, y_max*2 + 4, 0.8))
    create_mesh_object("First_Enclosure_Plinth", bm_p1, mat_laterite)

    build_gallery_unified("Gal_West_North", (x_min, 4.0), (x_min, y_max), width=gal_w, height=enc1_h, mat_stone=mat_sandstone, mat_relief=mat_basrelief)
    build_gallery_unified("Gal_West_South", (x_min, -4.0), (x_min, y_min), width=gal_w, height=enc1_h, mat_stone=mat_sandstone, mat_relief=mat_basrelief)
    # East Gallery (Samudra Manthana bas-relief)
    build_gallery_unified("Gal_East_SamudraManthana", (x_max, y_min), (x_max, y_max), width=gal_w, height=enc1_h, mat_stone=mat_sandstone, mat_relief=mat_basrelief)
    build_gallery_unified("Gal_North", (x_min, y_max), (x_max, y_max), width=gal_w, height=enc1_h, mat_stone=mat_sandstone, mat_relief=mat_inscriptions)
    build_gallery_unified("Gal_South", (x_min, y_min), (x_max, y_min), width=gal_w, height=enc1_h, mat_stone=mat_sandstone, mat_relief=mat_inscriptions)

    for cx, cy, cname in [
        (x_min, y_max, "Enc1_Corner_NW"),
        (x_max, y_max, "Enc1_Corner_NE"),
        (x_max, y_min, "Enc1_Corner_SE"),
        (x_min, y_min, "Enc1_Corner_SW")
    ]:
        build_prasat_tower_obj(cname, (cx, cy, 0.8), base_w=6.0, total_h=13.5, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)

    build_prasat_tower_obj("Enc1_Gopura_West", (x_min, 0, 0.8), base_w=7.5, total_h=16.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)
    build_prasat_tower_obj("Enc1_Gopura_East", (x_max, 0, 0.8), base_w=6.5, total_h=14.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)
    build_prasat_tower_obj("Enc1_Gopura_North", ((x_min+x_max)/2, y_max, 0.8), base_w=6.5, total_h=14.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)
    build_prasat_tower_obj("Enc1_Gopura_South", ((x_min+x_max)/2, y_min, 0.8), base_w=6.5, total_h=14.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)

    # 5. Preah Poan (Cruciform Cloister)
    log("Building 5: Preah Poan Cruciform Cloister...")
    set_active_collection(col_preah_poan)
    pp_min_x, pp_max_x = -30.0, -8.0
    pp_mid_x = (pp_min_x + pp_max_x) / 2.0
    pp_h = 5.6
    build_gallery_unified("PreahPoan_Axis_W_E", (pp_min_x, 0), (pp_max_x, 0), width=4.0, height=pp_h, mat_stone=mat_sandstone)
    build_gallery_unified("PreahPoan_Trans_N", (pp_mid_x, 0), (pp_mid_x,  15.0), width=3.8, height=pp_h, mat_stone=mat_sandstone)
    build_gallery_unified("PreahPoan_Trans_S", (pp_mid_x, 0), (pp_mid_x, -15.0), width=3.8, height=pp_h, mat_stone=mat_sandstone)

    bm_pp_basins = bmesh.new()
    pool_sz = 9.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = pp_mid_x + sx * 6.5
            py = sy * 7.5
            add_cube_mesh(bm_pp_basins, (px, py, 0.2), (pool_sz, pool_sz, 0.4))
    create_mesh_object("PreahPoan_Basins", bm_pp_basins, mat_water)

    build_library_fast("Courtyard1_Library_North", (pp_mid_x,  28.0, 0), scale=0.85, rotation_z=0, mat_stone=mat_sandstone)
    build_library_fast("Courtyard1_Library_South", (pp_mid_x, -28.0, 0), scale=0.85, rotation_z=0, mat_stone=mat_sandstone)

    # 6. Second Enclosure (Middle Terrace)
    log("Building 6: Second Enclosure & Devata Gallery...")
    set_active_collection(col_second_enc)
    enc2_x_min, enc2_x_max = -5.0, 45.0
    enc2_y_min, enc2_y_max = -26.0, 26.0
    enc2_plinth_h = 3.6
    enc2_gal_h = 5.2

    bm_p2 = bmesh.new()
    add_cube_mesh(bm_p2, ((enc2_x_min+enc2_x_max)/2, 0, 1.2), (enc2_x_max-enc2_x_min + 5.0, enc2_y_max*2 + 5.0, 2.4))
    add_cube_mesh(bm_p2, ((enc2_x_min+enc2_x_max)/2, 0, 2.4), (enc2_x_max-enc2_x_min + 3.0, enc2_y_max*2 + 3.0, 2.4))
    add_cube_mesh(bm_p2, ((enc2_x_min+enc2_x_max)/2, 0, 3.6), (enc2_x_max-enc2_x_min + 1.2, enc2_y_max*2 + 1.2, 2.4))
    create_mesh_object("Second_Enclosure_Plinth", bm_p2, mat_sandstone)

    build_steep_staircase_fast("Enc2_Stairs_West", (enc2_x_min - 2.5, 0, 0), width=3.8, depth=2.8, height=3.6, steps_count=6, mat_stone=mat_sandstone, rotation_z=math.radians(-90))
    build_steep_staircase_fast("Enc2_Stairs_East", (enc2_x_max + 2.5, 0, 0), width=3.8, depth=2.8, height=3.6, steps_count=6, mat_stone=mat_sandstone, rotation_z=math.radians(90))

    build_gallery_unified("Enc2_Gal_W", (enc2_x_min, enc2_y_min), (enc2_x_min, enc2_y_max), width=3.8, height=enc2_gal_h, mat_stone=mat_sandstone, mat_relief=mat_devata)
    build_gallery_unified("Enc2_Gal_E", (enc2_x_max, enc2_y_min), (enc2_x_max, enc2_y_max), width=3.8, height=enc2_gal_h, mat_stone=mat_sandstone, mat_relief=mat_devata)
    build_gallery_unified("Enc2_Gal_N", (enc2_x_min, enc2_y_max), (enc2_x_max, enc2_y_max), width=3.8, height=enc2_gal_h, mat_stone=mat_sandstone, mat_relief=mat_devata)
    build_gallery_unified("Enc2_Gal_S", (enc2_x_min, enc2_y_min), (enc2_x_max, enc2_y_min), width=3.8, height=enc2_gal_h, mat_stone=mat_sandstone, mat_relief=mat_devata)

    for cx, cy, cname in [
        (enc2_x_min, enc2_y_max, "Enc2_Corner_NW"),
        (enc2_x_max, enc2_y_max, "Enc2_Corner_NE"),
        (enc2_x_max, enc2_y_min, "Enc2_Corner_SE"),
        (enc2_x_min, enc2_y_min, "Enc2_Corner_SW")
    ]:
        build_prasat_tower_obj(cname, (cx, cy, enc2_plinth_h), base_w=5.2, total_h=12.0, tiers=3, mat_stone=mat_sandstone, mat_gold=mat_gold)

    # 7. Third Enclosure: The Bakan (Upper Sanctuary / Temple Mountain Pyramid)
    log("Building 7: The Bakan (Mount Meru) & The Quincunx of 5 Towers...")
    set_active_collection(col_bakan)
    center_x, center_y = 20.0, 0.0
    bakan_w = 26.0
    pyramid_base_h = 7.5

    bm_pyr = bmesh.new()
    add_cube_mesh(bm_pyr, (center_x, center_y, enc2_plinth_h + 2.5), (bakan_w*1.7, bakan_w*1.7, 5.0))
    add_cube_mesh(bm_pyr, (center_x, center_y, enc2_plinth_h + 5.0), (bakan_w*1.5, bakan_w*1.5, 5.0))
    add_cube_mesh(bm_pyr, (center_x, center_y, enc2_plinth_h + pyramid_base_h), (bakan_w*1.3, bakan_w*1.3, 5.0))
    create_mesh_object("Bakan_Mount_Meru_Pyramid", bm_pyr, mat_sandstone)

    bakan_floor_z = enc2_plinth_h + pyramid_base_h + 2.5

    for angle_deg in (0, 90, 180, 270):
        rad = math.radians(angle_deg)
        dist = bakan_w * 0.75
        sx = center_x + math.cos(rad) * dist
        sy = center_y + math.sin(rad) * dist
        build_steep_staircase_fast(f"Bakan_Stairs_{angle_deg}_C", (sx, sy, enc2_plinth_h), width=2.4, depth=4.2, height=pyramid_base_h + 2.5, steps_count=8, mat_stone=mat_sandstone, rotation_z=rad - math.radians(90))
        lx = sx - math.sin(rad) * 4.8
        ly = sy + math.cos(rad) * 4.8
        build_steep_staircase_fast(f"Bakan_Stairs_{angle_deg}_L", (lx, ly, enc2_plinth_h), width=2.0, depth=4.2, height=pyramid_base_h + 2.5, steps_count=8, mat_stone=mat_sandstone, rotation_z=rad - math.radians(90))
        rx = sx + math.sin(rad) * 4.8
        ry = sy - math.cos(rad) * 4.8
        build_steep_staircase_fast(f"Bakan_Stairs_{angle_deg}_R", (rx, ry, enc2_plinth_h), width=2.0, depth=4.2, height=pyramid_base_h + 2.5, steps_count=8, mat_stone=mat_sandstone, rotation_z=rad - math.radians(90))

    b_min_x, b_max_x = center_x - 12.0, center_x + 12.0
    b_min_y, b_max_y = center_y - 12.0, center_y + 12.0
    b_gal_h = 4.6
    build_gallery_unified("Bakan_Gal_W", (b_min_x, b_min_y), (b_min_x, b_max_y), width=3.2, height=b_gal_h, mat_stone=mat_sandstone)
    build_gallery_unified("Bakan_Gal_E", (b_max_x, b_min_y), (b_max_x, b_max_y), width=3.2, height=b_gal_h, mat_stone=mat_sandstone)
    build_gallery_unified("Bakan_Gal_N", (b_min_x, b_max_y), (b_max_x, b_max_y), width=3.2, height=b_gal_h, mat_stone=mat_sandstone)
    build_gallery_unified("Bakan_Gal_S", (b_min_x, b_min_y), (b_max_x, b_min_y), width=3.2, height=b_gal_h, mat_stone=mat_sandstone)

    build_gallery_unified("Bakan_Cross_WE", (b_min_x, 0), (b_max_x, 0), width=3.0, height=b_gal_h, mat_stone=mat_sandstone)
    build_gallery_unified("Bakan_Cross_NS", (center_x, b_min_y), (center_x, b_max_y), width=3.0, height=b_gal_h, mat_stone=mat_sandstone)

    corner_span = 10.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = center_x + sx * corner_span
            py = center_y + sy * corner_span
            corner_name = f"Quincunx_Corner_Prasat_{'E' if sx>0 else 'W'}_{'N' if sy>0 else 'S'}"
            build_prasat_tower_obj(
                corner_name, (px, py, bakan_floor_z),
                base_w=6.4, total_h=24.0, tiers=5,
                mat_stone=mat_sandstone, mat_gold=mat_gold, is_central=False
            )

    log("Building Central Prasat Thom with hollow Sanctum Chamber...")
    build_prasat_tower_obj(
        "Prasat_Thom_Central_Tower", (center_x, center_y, bakan_floor_z),
        base_w=9.8, total_h=38.0, tiers=6,
        mat_stone=mat_sandstone, mat_gold=mat_gold, is_central=True
    )

    # 8. Central Sanctum (Garbhagriha) & The Supreme Deity (Lord Vishnu)
    log("Building 8: Central Sanctum & Lord Vishnu (Paramavishnuloka)...")
    set_active_collection(col_sanctum)
    sanctum_z = bakan_floor_z

    build_chaturbhuja_vishnu_master(
        "Murti_Lord_Vishnu", (center_x + 0.6, center_y, sanctum_z + 0.2),
        scale=0.75, mat_deity=mat_vishnu, mat_gold=mat_gold,
        mat_white=mat_white, mat_red=mat_red, mat_pink=mat_pink,
        mat_inscriptions=mat_inscriptions
    )

    # 9. Atmospheric Lighting & Cameras
    log("Building 9: Atmospheric Lighting & Cinematic Cameras...")
    set_active_collection(col_lighting)
    scene = bpy.context.scene

    if not scene.world:
        scene.world = bpy.data.worlds.new("Angkor_World")
    scene.world.use_nodes = True
    wnodes = scene.world.node_tree.nodes
    wlinks = scene.world.node_tree.links
    wnodes.clear()
    w_out = wnodes.new(type="ShaderNodeOutputWorld")
    bg = wnodes.new(type="ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.78, 0.82, 0.94, 1.0)
    bg.inputs["Strength"].default_value = 0.9
    wlinks.new(bg.outputs["Background"], w_out.inputs["Surface"])

    # Golden Morning Sun Lamp
    sun_data = bpy.data.lights.new(name="Golden_Sunrise_Sun", type='SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.88, 0.72)
    sun_data.angle = math.radians(2.0)
    sun_obj = bpy.data.objects.new("Golden_Sunrise_Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (180, -60, 90)
    direction = mathutils.Vector((-1, 0.3, -0.6)).normalized()
    sun_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Ambient Fill
    sky_data = bpy.data.lights.new(name="Sky_Ambient_Fill", type='SUN')
    sky_data.energy = 1.2
    sky_data.color = (0.65, 0.78, 0.96)
    sky_obj = bpy.data.objects.new("Sky_Ambient_Fill", sky_data)
    bpy.context.collection.objects.link(sky_obj)
    sky_obj.rotation_euler = (math.radians(85), 0, 0)

    # Sanctum Direct Illumination (shaft of divine golden light illuminating Lord Vishnu)
    sanctum_lamp = bpy.data.lights.new(name="Sanctum_Shaft_Light", type='SPOT')
    sanctum_lamp.energy = 450.0
    sanctum_lamp.spot_size = math.radians(68)
    sanctum_lamp.spot_blend = 0.45
    sanctum_lamp.color = (1.0, 0.90, 0.72)
    sanctum_lamp_obj = bpy.data.objects.new("Sanctum_Shaft_Light", sanctum_lamp)
    bpy.context.collection.objects.link(sanctum_lamp_obj)
    sanctum_lamp_obj.location = (center_x - 3.5, 0, sanctum_z + 4.8)
    s_dir = (mathutils.Vector((center_x + 0.6, 0, sanctum_z + 2.55)) - sanctum_lamp_obj.location).normalized()
    sanctum_lamp_obj.rotation_euler = s_dir.to_track_quat('-Z', 'Y').to_euler()

    # Inscription Accent Light
    stela_lamp = bpy.data.lights.new(name="Stela_Accent_Light", type='SPOT')
    stela_lamp.energy = 250.0
    stela_lamp.spot_size = math.radians(60)
    stela_lamp.color = (1.0, 0.92, 0.78)
    stela_lamp_obj = bpy.data.objects.new("Stela_Accent_Light", stela_lamp)
    bpy.context.collection.objects.link(stela_lamp_obj)
    stela_lamp_obj.location = (landing_x - 1.0, 4.5, 3.5)
    st_dir = (mathutils.Vector((landing_x + 2.0, 4.5, 2.7)) - stela_lamp_obj.location).normalized()
    stela_lamp_obj.rotation_euler = st_dir.to_track_quat('-Z', 'Y').to_euler()

    # Sacred Deepa (Oil Lamps) illuminating Lord Vishnu in Garbhagriha
    for lamp_name, l_y in [("Sanctum_Deepa_North", 1.4), ("Sanctum_Deepa_South", -1.4)]:
        dlamp = bpy.data.lights.new(name=lamp_name, type='POINT')
        dlamp.energy = 160.0
        dlamp.color = (1.0, 0.65, 0.28)
        dlamp_obj = bpy.data.objects.new(lamp_name, dlamp)
        bpy.context.collection.objects.link(dlamp_obj)
        dlamp_obj.location = (center_x - 0.8, l_y, sanctum_z + 1.8)

    # Soft eye-level warm fill for torso, divine ornaments, and pleated sampot
    tlamp = bpy.data.lights.new(name="Sanctum_Torso_Fill", type='POINT')
    tlamp.energy = 95.0
    tlamp.color = (1.0, 0.90, 0.78)
    tlamp_obj = bpy.data.objects.new("Sanctum_Torso_Fill", tlamp)
    bpy.context.collection.objects.link(tlamp_obj)
    tlamp_obj.location = (center_x - 2.8, 0.0, sanctum_z + 2.4)

    # Gallery Corridor Illumination for Bas-Relief View
    glamp = bpy.data.lights.new(name="Gallery_Warm_Light", type='POINT')
    glamp.energy = 380.0
    glamp.color = (1.0, 0.92, 0.80)
    glamp_obj = bpy.data.objects.new("Gallery_Warm_Light", glamp)
    bpy.context.collection.objects.link(glamp_obj)
    glamp_obj.location = (75.8, -18.0, 3.2)

    # Precise Cameras setup
    cameras = {}
    def create_cam(cam_name, loc, target, fl=35.0):
        cdata = bpy.data.cameras.new(cam_name)
        cdata.lens = fl
        cdata.clip_start = 0.1
        cdata.clip_end = 2000.0
        cobj = bpy.data.objects.new(cam_name, cdata)
        bpy.context.collection.objects.link(cobj)
        cobj.location = loc
        direction = mathutils.Vector(target) - mathutils.Vector(loc)
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cobj.rotation_euler = rot_quat.to_euler()
        cameras[cam_name] = cobj
        return cobj

    # 1. Hero Western Reflection Pool Sunrise (Classic postcard angle with towers reflected in holy pool)
    create_cam("Cam_01_Hero_West_Sunrise", loc=(-105.0, 32.0, 5.8), target=(20.0, 0.0, 28.0), fl=32.0)

    # 2. Aerial Grand View (Frames entire complex: moat, causeway, enclosures, quincunx)
    create_cam("Cam_02_Aerial_Grand_View", loc=(-145.0, -120.0, 100.0), target=(10.0, 0.0, 18.0), fl=24.0)

    # 3. Bakan Upper Towers (Dramatic low angle looking up at the five lotus prasats)
    create_cam("Cam_03_Bakan_Upper_Towers", loc=(-12.0, -18.0, 5.0), target=(20.0, 0.0, 32.0), fl=22.0)

    # 4. Bas-Relief Gallery (Inside East gallery looking along colonnade and Samudra Manthana mural)
    create_cam("Cam_04_BasRelief_Gallery", loc=(74.8, -25.0, 2.2), target=(76.8, -14.0, 2.4), fl=30.0)

    # 5. Holy Garbhagriha Sanctum (Directly framed onto Four-Armed Lord Vishnu: Shankha, Chakra, Gada, Padma, Urdhvapundra)
    create_cam("Cam_05_Garbhagriha_Vishnu", loc=(center_x - 4.2, 0.0, sanctum_z + 2.55), target=(center_x + 0.6, 0.0, sanctum_z + 2.55), fl=21.0)

    # 6. Macro Inscriptions Detail (Freestanding Royal Stela inscribed with Sanskrit & Old Khmer)
    create_cam("Cam_06_Inscription_Macro", loc=(landing_x - 1.2, 4.5, 2.7), target=(landing_x + 2.0, 4.5, 2.7), fl=50.0)

    log("Angkor Wat structural assembly complete!")
    return cameras

# -------------------------------------------------------------------------
# Render & Export Pipeline
# -------------------------------------------------------------------------
def render_all_cameras(cameras):
    log("Configuring fast Cycles render settings...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 2
    scene.cycles.samples = 16
    scene.cycles.max_bounces = 3
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 0
    scene.cycles.transparent_max_bounces = 2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.image_settings.file_format = 'PNG'

    for cam_name, cam_obj in cameras.items():
        out_path = os.path.join(RENDER_DIR, f"{cam_name}.png")
        log(f"Rendering {cam_name} -> {out_path}...")
        scene.camera = cam_obj
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        log(f"Finished {cam_name}")

def export_master_assets():
    blend_path = os.path.join(MODEL_DIR, "angkor_wat_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    log(f"Saved master .blend file: {blend_path}")

    glb_path = os.path.join(MODEL_DIR, "angkor_wat_complete.glb")
    log(f"Exporting complete scene to GLB: {glb_path}...")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    log(f"GLB export finished: {glb_path}")

if __name__ == "__main__":
    cams = build_angkor_wat()
    render_all_cameras(cams)
    export_master_assets()
    log("All tasks completed successfully!")
