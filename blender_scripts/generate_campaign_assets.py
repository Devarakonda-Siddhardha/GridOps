"""
Blender script to generate 3D models and skeletal animations for the Greek vs. Roman Campaign:
1. greek_soldier.glb (Allied Hoplite with dory spear & aspis shield)
2. roman_soldier.glb (Roman Legionnaire with scutum & gladius)
3. roman_centurion.glb (Centurion Officer with transverse crest & cape)
4. roman_general.glb (General Marcus Boss with gilded armor & purple cloak)
5. Environment props: castrum_wall, castrum_gate, watchtower, prisoner_cage, banners
"""

import bpy
import math
import os
from mathutils import Vector, Euler, Matrix

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "models")
os.makedirs(OUT_DIR, exist_ok=True)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_mat(name, color, metallic=0.0, roughness=0.5, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 1.0
    return mat

def create_humanoid_armature(prefix="Char"):
    arm_data = bpy.data.armatures.new(f"{prefix}ArmatureData")
    arm_obj = bpy.data.objects.new(f"{prefix}Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    root = eb.new("Root")
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.2)

    hips = eb.new("Hips")
    hips.parent = root
    hips.head = (0, 0, 0.95)
    hips.tail = (0, 0, 1.1)

    spine = eb.new("Spine")
    spine.parent = hips
    spine.head = (0, 0, 1.1)
    spine.tail = (0, 0, 1.3)

    chest = eb.new("Chest")
    chest.parent = spine
    chest.head = (0, 0, 1.3)
    chest.tail = (0, 0, 1.55)

    neck = eb.new("Neck")
    neck.parent = chest
    neck.head = (0, 0, 1.55)
    neck.tail = (0, 0, 1.65)

    head = eb.new("Head")
    head.parent = neck
    head.head = (0, 0, 1.65)
    head.tail = (0, 0, 1.95)

    # Left Arm
    uarm_l = eb.new("UpperArm.L")
    uarm_l.parent = chest
    uarm_l.head = (0.24, 0, 1.5)
    uarm_l.tail = (0.48, 0, 1.45)

    farm_l = eb.new("Forearm.L")
    farm_l.parent = uarm_l
    farm_l.head = (0.48, 0, 1.45)
    farm_l.tail = (0.72, 0.12, 1.45)

    hand_l = eb.new("Hand.L")
    hand_l.parent = farm_l
    hand_l.head = (0.72, 0.12, 1.45)
    hand_l.tail = (0.84, 0.18, 1.45)

    # Right Arm
    uarm_r = eb.new("UpperArm.R")
    uarm_r.parent = chest
    uarm_r.head = (-0.24, 0, 1.5)
    uarm_r.tail = (-0.48, 0, 1.45)

    farm_r = eb.new("Forearm.R")
    farm_r.parent = uarm_r
    farm_r.head = (-0.48, 0, 1.45)
    farm_r.tail = (-0.72, 0.12, 1.45)

    hand_r = eb.new("Hand.R")
    hand_r.parent = farm_r
    hand_r.head = (-0.72, 0.12, 1.45)
    hand_r.tail = (-0.84, 0.18, 1.45)

    # Legs
    thigh_l = eb.new("Thigh.L")
    thigh_l.parent = hips
    thigh_l.head = (0.16, 0, 0.95)
    thigh_l.tail = (0.16, 0, 0.52)

    shin_l = eb.new("Shin.L")
    shin_l.parent = thigh_l
    shin_l.head = (0.16, 0, 0.52)
    shin_l.tail = (0.16, 0, 0.08)

    foot_l = eb.new("Foot.L")
    foot_l.parent = shin_l
    foot_l.head = (0.16, 0, 0.08)
    foot_l.tail = (0.16, 0.22, 0.0)

    thigh_r = eb.new("Thigh.R")
    thigh_r.parent = hips
    thigh_r.head = (-0.16, 0, 0.95)
    thigh_r.tail = (-0.16, 0, 0.52)

    shin_r = eb.new("Shin.R")
    shin_r.parent = thigh_r
    shin_r.head = (-0.16, 0, 0.52)
    shin_r.tail = (-0.16, 0, 0.08)

    foot_r = eb.new("Foot.R")
    foot_r.parent = shin_r
    foot_r.head = (-0.16, 0, 0.08)
    foot_r.tail = (-0.16, 0.22, 0.0)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

def assign_vg(obj, bone_name):
    vg = obj.vertex_groups.get(bone_name)
    if not vg:
        vg = obj.vertex_groups.new(name=bone_name)
    v_indices = [v.index for v in obj.data.vertices]
    if v_indices:
        vg.add(v_indices, 1.0, 'REPLACE')

# ==============================================================
# 1. GREEK HOPLITE ALLIED SOLDIER (Dory Spear, Aspis Shield, Blue Crest)
# ==============================================================
def build_greek_soldier():
    clear_scene()
    mat_bronze = create_mat("HopliteBronze", (0.80, 0.52, 0.20, 1.0), metallic=0.9, roughness=0.3)
    mat_blue = create_mat("GreekBlue", (0.10, 0.35, 0.85, 1.0), metallic=0.0, roughness=0.5)
    mat_white = create_mat("TunicWhite", (0.92, 0.92, 0.90, 1.0), metallic=0.0, roughness=0.6)
    mat_skin = create_mat("HopliteSkin", (0.85, 0.67, 0.52, 1.0), metallic=0.0, roughness=0.6)
    mat_iron = create_mat("SpearIron", (0.65, 0.68, 0.72, 1.0), metallic=0.95, roughness=0.2)
    mat_wood = create_mat("SpearWood", (0.42, 0.26, 0.14, 1.0), metallic=0.0, roughness=0.7)

    arm_obj = create_humanoid_armature("GreekSoldier")
    mesh_parts = []

    # Torso (Muscled Cuirass)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.35))
    torso = bpy.context.active_object
    torso.scale = (0.24, 0.16, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_bronze)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Pteruges (Skirt)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.28, location=(0, 0, 1.05))
    skirt = bpy.context.active_object
    skirt.data.materials.append(mat_blue)
    assign_vg(skirt, "Hips")
    mesh_parts.append(skirt)

    # Head & Corinthian Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 1.78))
    head = bpy.context.active_object
    head.scale = (0.95, 1.05, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mat_bronze)
    assign_vg(head, "Head")
    mesh_parts.append(head)

    # Greek Blue Crest
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.02, 1.98))
    crest = bpy.context.active_object
    crest.scale = (0.04, 0.26, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    crest.data.materials.append(mat_blue)
    assign_vg(crest, "Head")
    mesh_parts.append(crest)

    # Arms
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.28, location=(sign * 0.36, 0, 1.48))
        uarm = bpy.context.active_object
        uarm.rotation_euler = (0, math.radians(sign * 80), 0)
        bpy.ops.object.transform_apply(rotation=True)
        uarm.data.materials.append(mat_skin)
        assign_vg(uarm, f"UpperArm.{side}")
        mesh_parts.append(uarm)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.26, location=(sign * 0.60, 0.08, 1.45))
        farm = bpy.context.active_object
        farm.data.materials.append(mat_bronze)
        assign_vg(farm, f"Forearm.{side}")
        mesh_parts.append(farm)

    # Legs
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.40, location=(sign * 0.16, 0, 0.74))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_skin)
        assign_vg(thigh, f"Thigh.{side}")
        mesh_parts.append(thigh)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.42, location=(sign * 0.16, 0, 0.30))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_bronze)  # Bronze greaves
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Aspis Shield (Left Arm)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.40, depth=0.06, location=(0.76, 0.22, 1.45))
    shield = bpy.context.active_object
    shield.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    shield.data.materials.append(mat_blue)
    assign_vg(shield, "Forearm.L")
    mesh_parts.append(shield)

    # Shield Bronze Rim
    bpy.ops.mesh.primitive_torus_add(major_radius=0.40, minor_radius=0.03, location=(0.76, 0.22, 1.45))
    s_rim = bpy.context.active_object
    s_rim.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    s_rim.data.materials.append(mat_bronze)
    assign_vg(s_rim, "Forearm.L")
    mesh_parts.append(s_rim)

    # Dory Spear (Right Arm) - Shaft + Iron Tip + Bronze Sauroter
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=2.4, location=(-0.74, 0.40, 1.45))
    spear_shaft = bpy.context.active_object
    spear_shaft.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    spear_shaft.data.materials.append(mat_wood)
    assign_vg(spear_shaft, "Hand.R")
    mesh_parts.append(spear_shaft)

    bpy.ops.mesh.primitive_cone_add(radius1=0.06, depth=0.35, location=(-0.74, 1.65, 1.45))
    spear_tip = bpy.context.active_object
    spear_tip.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    spear_tip.data.materials.append(mat_iron)
    assign_vg(spear_tip, "Hand.R")
    mesh_parts.append(spear_tip)

    # Join meshes
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    char_mesh = bpy.context.active_object
    char_mesh.name = "GreekSoldierMesh"

    mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    char_mesh.parent = arm_obj

    # Create Animations
    build_humanoid_animations(arm_obj, is_spear=True)

    # Export GLB
    out_file = os.path.join(OUT_DIR, "greek_soldier.glb")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    char_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported:", out_file)

# ==============================================================
# 2. ROMAN LEGIONNAIRE (Lorica Segmentata, Scutum, Galea Helmet, Gladius)
# ==============================================================
def build_roman_soldier():
    clear_scene()
    mat_iron = create_mat("RomanIron", (0.68, 0.70, 0.74, 1.0), metallic=0.92, roughness=0.3)
    mat_red = create_mat("RomanRed", (0.78, 0.08, 0.08, 1.0), metallic=0.0, roughness=0.5)
    mat_gold = create_mat("RomanGold", (0.92, 0.75, 0.18, 1.0), metallic=0.95, roughness=0.25)
    mat_skin = create_mat("RomanSkin", (0.84, 0.66, 0.51, 1.0), metallic=0.0, roughness=0.6)
    mat_leather = create_mat("RomanLeather", (0.28, 0.15, 0.08, 1.0), metallic=0.1, roughness=0.7)

    arm_obj = create_humanoid_armature("RomanSoldier")
    mesh_parts = []

    # Torso (Lorica Segmentata)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.35))
    torso = bpy.context.active_object
    torso.scale = (0.25, 0.17, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_iron)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Red Tunic & Balteus (Leather strip belt)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.28, location=(0, 0, 1.05))
    skirt = bpy.context.active_object
    skirt.data.materials.append(mat_red)
    assign_vg(skirt, "Hips")
    mesh_parts.append(skirt)

    # Galea Helmet (Iron helmet + brass brow guard + red crest)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.155, location=(0, 0, 1.78))
    helmet = bpy.context.active_object
    helmet.scale = (0.98, 1.06, 1.08)
    bpy.ops.object.transform_apply(scale=True)
    helmet.data.materials.append(mat_iron)
    assign_vg(helmet, "Head")
    mesh_parts.append(helmet)

    # Helmet Crest (Red longitudinal horsehair)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.02, 1.96))
    crest = bpy.context.active_object
    crest.scale = (0.04, 0.22, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    crest.data.materials.append(mat_red)
    assign_vg(crest, "Head")
    mesh_parts.append(crest)

    # Arms
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.28, location=(sign * 0.36, 0, 1.48))
        uarm = bpy.context.active_object
        uarm.rotation_euler = (0, math.radians(sign * 80), 0)
        bpy.ops.object.transform_apply(rotation=True)
        uarm.data.materials.append(mat_red)  # Red tunic sleeves
        assign_vg(uarm, f"UpperArm.{side}")
        mesh_parts.append(uarm)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.26, location=(sign * 0.60, 0.08, 1.45))
        farm = bpy.context.active_object
        farm.data.materials.append(mat_skin)
        assign_vg(farm, f"Forearm.{side}")
        mesh_parts.append(farm)

    # Legs & Caligae sandals
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.40, location=(sign * 0.16, 0, 0.74))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_skin)
        assign_vg(thigh, f"Thigh.{side}")
        mesh_parts.append(thigh)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.42, location=(sign * 0.16, 0, 0.30))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_leather)
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Curved Rectangular Scutum Shield (Left Arm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.76, 0.25, 1.35))
    scutum = bpy.context.active_object
    scutum.scale = (0.05, 0.42, 0.72)
    bpy.ops.object.transform_apply(scale=True)
    scutum.data.materials.append(mat_red)
    assign_vg(scutum, "Forearm.L")
    mesh_parts.append(scutum)

    # Golden Shield Umbo (Boss) in Center
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0.81, 0.25, 1.35))
    boss = bpy.context.active_object
    boss.scale = (0.4, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    boss.data.materials.append(mat_gold)
    assign_vg(boss, "Forearm.L")
    mesh_parts.append(boss)

    # Gladius Sword (Right Hand)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.76, 0.35, 1.45))
    blade = bpy.context.active_object
    blade.scale = (0.03, 0.08, 0.65)
    blade.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    blade.data.materials.append(mat_iron)
    assign_vg(blade, "Hand.R")
    mesh_parts.append(blade)

    # Join meshes
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    char_mesh = bpy.context.active_object
    char_mesh.name = "RomanSoldierMesh"

    mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    char_mesh.parent = arm_obj

    # Create Animations
    build_humanoid_animations(arm_obj, is_spear=False, has_block=True)

    out_file = os.path.join(OUT_DIR, "roman_soldier.glb")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    char_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported:", out_file)

# ==============================================================
# 3. ROMAN CENTURION OFFICER (Transverse Plume, Muscled Cuirass, Red Cape)
# ==============================================================
def build_roman_centurion():
    clear_scene()
    mat_silver = create_mat("CenturionSilver", (0.80, 0.82, 0.85, 1.0), metallic=0.95, roughness=0.2)
    mat_gold = create_mat("CenturionGold", (0.95, 0.78, 0.18, 1.0), metallic=0.95, roughness=0.2)
    mat_red = create_mat("ImperialCrimson", (0.82, 0.05, 0.05, 1.0), metallic=0.0, roughness=0.5)
    mat_skin = create_mat("CenturionSkin", (0.84, 0.66, 0.51, 1.0), metallic=0.0, roughness=0.6)

    arm_obj = create_humanoid_armature("Centurion")
    mesh_parts = []

    # Muscled Cuirass
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.35))
    torso = bpy.context.active_object
    torso.scale = (0.26, 0.17, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_silver)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Red Cape hanging from shoulders
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.16, 1.15))
    cape = bpy.context.active_object
    cape.scale = (0.28, 0.03, 0.48)
    bpy.ops.object.transform_apply(scale=True)
    cape.data.materials.append(mat_red)
    assign_vg(cape, "Chest")
    mesh_parts.append(cape)

    # Skirt
    bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.28, location=(0, 0, 1.05))
    skirt = bpy.context.active_object
    skirt.data.materials.append(mat_red)
    assign_vg(skirt, "Hips")
    mesh_parts.append(skirt)

    # Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.155, location=(0, 0, 1.78))
    helmet = bpy.context.active_object
    helmet.scale = (0.98, 1.06, 1.08)
    bpy.ops.object.transform_apply(scale=True)
    helmet.data.materials.append(mat_silver)
    assign_vg(helmet, "Head")
    mesh_parts.append(helmet)

    # Transverse Crest (Crest runs horizontally across the head)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.98))
    crest = bpy.context.active_object
    crest.scale = (0.28, 0.06, 0.11)
    bpy.ops.object.transform_apply(scale=True)
    crest.data.materials.append(mat_red)
    assign_vg(crest, "Head")
    mesh_parts.append(crest)

    # Arms
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.28, location=(sign * 0.36, 0, 1.48))
        uarm = bpy.context.active_object
        uarm.rotation_euler = (0, math.radians(sign * 80), 0)
        bpy.ops.object.transform_apply(rotation=True)
        uarm.data.materials.append(mat_silver)
        assign_vg(uarm, f"UpperArm.{side}")
        mesh_parts.append(uarm)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.26, location=(sign * 0.60, 0.08, 1.45))
        farm = bpy.context.active_object
        farm.data.materials.append(mat_silver)
        assign_vg(farm, f"Forearm.{side}")
        mesh_parts.append(farm)

    # Legs & Silver Greaves
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.40, location=(sign * 0.16, 0, 0.74))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_skin)
        assign_vg(thigh, f"Thigh.{side}")
        mesh_parts.append(thigh)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.42, location=(sign * 0.16, 0, 0.30))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_silver)
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Round Parma Shield (Left Arm)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.06, location=(0.76, 0.22, 1.45))
    shield = bpy.context.active_object
    shield.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    shield.data.materials.append(mat_red)
    assign_vg(shield, "Forearm.L")
    mesh_parts.append(shield)

    # Golden Gladius
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.76, 0.35, 1.45))
    blade = bpy.context.active_object
    blade.scale = (0.03, 0.08, 0.65)
    blade.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    blade.data.materials.append(mat_gold)
    assign_vg(blade, "Hand.R")
    mesh_parts.append(blade)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    char_mesh = bpy.context.active_object
    char_mesh.name = "CenturionMesh"

    mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    char_mesh.parent = arm_obj

    build_humanoid_animations(arm_obj, is_spear=False, has_shout=True)

    out_file = os.path.join(OUT_DIR, "roman_centurion.glb")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    char_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported:", out_file)

# ==============================================================
# 4. ROMAN GENERAL MARCUS (Final Boss - Towering 2.3m, Gilded Armor, Imperial Purple Cloak)
# ==============================================================
def build_roman_general():
    clear_scene()
    mat_gold = create_mat("ImperialGold", (0.95, 0.78, 0.16, 1.0), metallic=0.96, roughness=0.2)
    mat_purple = create_mat("ImperialPurple", (0.42, 0.06, 0.58, 1.0), metallic=0.0, roughness=0.5)
    mat_iron = create_mat("DarkSteel", (0.35, 0.38, 0.42, 1.0), metallic=0.95, roughness=0.2)
    mat_skin = create_mat("GeneralSkin", (0.82, 0.65, 0.50, 1.0), metallic=0.0, roughness=0.6)

    arm_obj = create_humanoid_armature("GeneralMarcus")
    arm_obj.scale = (1.25, 1.25, 1.25)  # Imposing boss scale!
    bpy.ops.object.transform_apply(scale=True)

    mesh_parts = []

    # Golden Muscled Cuirass (Scaled up)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.70))
    torso = bpy.context.active_object
    torso.scale = (0.32, 0.22, 0.32)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_gold)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Imperial Purple Cloak
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.20, 1.40))
    cape = bpy.context.active_object
    cape.scale = (0.36, 0.04, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    cape.data.materials.append(mat_purple)
    assign_vg(cape, "Chest")
    mesh_parts.append(cape)

    # Skirt
    bpy.ops.mesh.primitive_cylinder_add(radius=0.33, depth=0.36, location=(0, 0, 1.30))
    skirt = bpy.context.active_object
    skirt.data.materials.append(mat_purple)
    assign_vg(skirt, "Hips")
    mesh_parts.append(skirt)

    # Gilded Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0, 0, 2.22))
    helmet = bpy.context.active_object
    helmet.scale = (0.98, 1.06, 1.08)
    bpy.ops.object.transform_apply(scale=True)
    helmet.data.materials.append(mat_gold)
    assign_vg(helmet, "Head")
    mesh_parts.append(helmet)

    # Eagle Crest on Helmet
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, depth=0.25, location=(0, 0.04, 2.48))
    eagle_crest = bpy.context.active_object
    eagle_crest.data.materials.append(mat_purple)
    assign_vg(eagle_crest, "Head")
    mesh_parts.append(eagle_crest)

    # Arms
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.35, location=(sign * 0.45, 0, 1.85))
        uarm = bpy.context.active_object
        uarm.rotation_euler = (0, math.radians(sign * 80), 0)
        bpy.ops.object.transform_apply(rotation=True)
        uarm.data.materials.append(mat_gold)
        assign_vg(uarm, f"UpperArm.{side}")
        mesh_parts.append(uarm)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.32, location=(sign * 0.75, 0.10, 1.80))
        farm = bpy.context.active_object
        farm.data.materials.append(mat_gold)
        assign_vg(farm, f"Forearm.{side}")
        mesh_parts.append(farm)

    # Legs
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.50, location=(sign * 0.20, 0, 0.92))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_skin)
        assign_vg(thigh, f"Thigh.{side}")
        mesh_parts.append(thigh)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.52, location=(sign * 0.20, 0, 0.38))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_gold)
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Heavy Ornate Golden Scutum (Left Arm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.95, 0.30, 1.70))
    scutum = bpy.context.active_object
    scutum.scale = (0.06, 0.52, 0.90)
    bpy.ops.object.transform_apply(scale=True)
    scutum.data.materials.append(mat_purple)
    assign_vg(scutum, "Forearm.L")
    mesh_parts.append(scutum)

    # Gold Eagle Emblem on Shield
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(1.02, 0.30, 1.70))
    emblem = bpy.context.active_object
    emblem.scale = (0.3, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    emblem.data.materials.append(mat_gold)
    assign_vg(emblem, "Forearm.L")
    mesh_parts.append(emblem)

    # Massive War Spatha / Sword (Right Hand)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.95, 0.45, 1.80))
    blade = bpy.context.active_object
    blade.scale = (0.04, 0.10, 0.95)
    blade.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    blade.data.materials.append(mat_gold)
    assign_vg(blade, "Hand.R")
    mesh_parts.append(blade)

    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    char_mesh = bpy.context.active_object
    char_mesh.name = "GeneralMarcusMesh"

    mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    char_mesh.parent = arm_obj

    build_humanoid_animations(arm_obj, is_spear=False, has_block=True, has_shout=True)

    out_file = os.path.join(OUT_DIR, "roman_general.glb")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    char_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported:", out_file)

# ==============================================================
# ANIMATION GENERATOR HELPER
# ==============================================================
def build_humanoid_animations(arm_obj, is_spear=False, has_block=False, has_shout=False):
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm_obj.pose.bones

    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    def reset():
        for b in pb:
            b.location = (0, 0, 0)
            b.rotation_euler = (0, 0, 0)
            b.scale = (1, 1, 1)

    def keyframe(frame):
        for b in pb:
            b.keyframe_insert(data_path="location", frame=frame)
            b.keyframe_insert(data_path="rotation_euler", frame=frame)

    actions = []

    # 1. Idle
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset()
    keyframe(1)
    pb["Spine"].rotation_euler = (math.radians(2), 0, 0)
    pb["Chest"].location = (0, 0, -0.02)
    keyframe(15)
    reset()
    keyframe(30)
    actions.append(act_idle)

    # 2. Run
    act_run = bpy.data.actions.new(name="Run")
    arm_obj.animation_data.action = act_run
    reset()
    keyframe(1)

    # Frame 6: Right leg forward, left back
    pb["Thigh.R"].rotation_euler = (math.radians(-35), 0, 0)
    pb["Shin.R"].rotation_euler = (math.radians(25), 0, 0)
    pb["Thigh.L"].rotation_euler = (math.radians(35), 0, 0)
    pb["Shin.L"].rotation_euler = (math.radians(30), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(-25), 0, 0)
    pb["UpperArm.R"].rotation_euler = (math.radians(25), 0, 0)
    keyframe(6)

    # Frame 12: Passing
    reset()
    keyframe(12)

    # Frame 18: Left leg forward, right back
    pb["Thigh.L"].rotation_euler = (math.radians(-35), 0, 0)
    pb["Shin.L"].rotation_euler = (math.radians(25), 0, 0)
    pb["Thigh.R"].rotation_euler = (math.radians(35), 0, 0)
    pb["Shin.R"].rotation_euler = (math.radians(30), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(25), 0, 0)
    pb["UpperArm.R"].rotation_euler = (math.radians(-25), 0, 0)
    keyframe(18)

    reset()
    keyframe(24)
    actions.append(act_run)

    # 3. Attack
    act_attack = bpy.data.actions.new(name="Attack")
    arm_obj.animation_data.action = act_attack
    reset()
    keyframe(1)

    if is_spear:
        # Spear thrust: pull arm back at frame 6, thrust forward powerfully at frame 12
        pb["UpperArm.R"].rotation_euler = (math.radians(-20), 0, math.radians(-30))
        pb["Forearm.R"].rotation_euler = (math.radians(50), 0, 0)
        keyframe(6)

        pb["UpperArm.R"].rotation_euler = (math.radians(70), 0, 0)
        pb["Forearm.R"].rotation_euler = (math.radians(-30), 0, 0)
        pb["Spine"].rotation_euler = (math.radians(15), 0, 0)
        keyframe(12)
    else:
        # Sword slash: windup right at frame 6, slash across at frame 12
        pb["UpperArm.R"].rotation_euler = (math.radians(-40), math.radians(-30), 0)
        keyframe(6)
        pb["UpperArm.R"].rotation_euler = (math.radians(45), math.radians(40), 0)
        pb["Forearm.R"].rotation_euler = (math.radians(20), 0, 0)
        pb["Spine"].rotation_euler = (math.radians(15), 0, math.radians(-15))
        keyframe(12)

    reset()
    keyframe(24)
    actions.append(act_attack)

    # 4. ShieldBlock
    if has_block:
        act_block = bpy.data.actions.new(name="ShieldBlock")
        arm_obj.animation_data.action = act_block
        reset()
        keyframe(1)
        pb["UpperArm.L"].rotation_euler = (math.radians(40), math.radians(30), 0)
        pb["Forearm.L"].rotation_euler = (math.radians(60), 0, 0)
        pb["Spine"].rotation_euler = (math.radians(10), 0, 0)
        keyframe(8)
        keyframe(20)
        reset()
        keyframe(26)
        actions.append(act_block)

    # 5. WarHorn / Shout
    if has_shout:
        act_shout = bpy.data.actions.new(name="WarHorn")
        arm_obj.animation_data.action = act_shout
        reset()
        keyframe(1)
        pb["Chest"].rotation_euler = (math.radians(-25), 0, 0)
        pb["Head"].rotation_euler = (math.radians(-35), 0, 0)
        pb["UpperArm.R"].rotation_euler = (math.radians(-70), 0, math.radians(-20))
        keyframe(10)
        keyframe(25)
        reset()
        keyframe(32)
        actions.append(act_shout)

    # 6. Hit
    act_hit = bpy.data.actions.new(name="Hit")
    arm_obj.animation_data.action = act_hit
    reset()
    keyframe(1)
    pb["Chest"].rotation_euler = (math.radians(-25), 0, math.radians(10))
    pb["Head"].rotation_euler = (math.radians(-20), 0, 0)
    keyframe(4)
    reset()
    keyframe(12)
    actions.append(act_hit)

    # 7. Death
    act_death = bpy.data.actions.new(name="Death")
    arm_obj.animation_data.action = act_death
    reset()
    keyframe(1)
    pb["Hips"].location = (0, -0.2, -0.45)
    pb["Thigh.L"].rotation_euler = (math.radians(60), 0, 0)
    pb["Thigh.R"].rotation_euler = (math.radians(60), 0, 0)
    keyframe(10)

    pb["Hips"].location = (0, -0.3, -0.85)
    pb["Hips"].rotation_euler = (math.radians(-85), 0, 0)
    keyframe(25)
    actions.append(act_death)

    bpy.ops.object.mode_set(mode='OBJECT')

# ==============================================================
# 5. ENVIRONMENT & FORTRESS PROPS
# ==============================================================
def build_fortress_props():
    # 1. Castrum Wall Segment
    clear_scene()
    mat_wood = create_mat("CastrumTimber", (0.35, 0.22, 0.12, 1.0), metallic=0.0, roughness=0.8)
    mat_stone = create_mat("CastrumStone", (0.55, 0.53, 0.50, 1.0), metallic=0.0, roughness=0.85)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.2))
    base = bpy.context.active_object
    base.scale = (4.0, 1.2, 2.4)
    bpy.ops.object.transform_apply(scale=True)
    base.data.materials.append(mat_stone)

    # Palisade logs on top
    for i in range(8):
        x = -1.75 + i * 0.5
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.6, location=(x, 0.45, 3.0))
        log = bpy.context.active_object
        log.data.materials.append(mat_wood)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    wall = bpy.context.active_object
    wall.name = "CastrumWall"
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "castrum_wall.glb"), export_format='GLB')
    print("Exported castrum_wall.glb")

    # 2. Castrum Fortress Gate (Double Timber Doors with Iron Reinforcement)
    clear_scene()
    mat_wood = create_mat("CastrumTimber", (0.35, 0.22, 0.12, 1.0), metallic=0.0, roughness=0.8)
    mat_iron = create_mat("IronBands", (0.45, 0.48, 0.52, 1.0), metallic=0.9, roughness=0.3)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.2))
    gate = bpy.context.active_object
    gate.scale = (4.8, 0.25, 4.4)
    bpy.ops.object.transform_apply(scale=True)
    gate.data.materials.append(mat_wood)

    # Iron crossbeams
    for z in [0.8, 2.2, 3.6]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.14, z))
        band = bpy.context.active_object
        band.scale = (4.9, 0.05, 0.20)
        bpy.ops.object.transform_apply(scale=True)
        band.data.materials.append(mat_iron)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    gate_obj = bpy.context.active_object
    gate_obj.name = "CastrumGate"
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "castrum_gate.glb"), export_format='GLB')
    print("Exported castrum_gate.glb")

    # 3. Roman Watchtower (Timber Tower with Elevated Platform)
    clear_scene()
    mat_wood = create_mat("CastrumTimber", (0.35, 0.22, 0.12, 1.0), metallic=0.0, roughness=0.8)
    # 4 Legs
    for x in [-1.4, 1.4]:
        for y in [-1.4, 1.4]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=6.0, location=(x, y, 3.0))
            post = bpy.context.active_object
            post.data.materials.append(mat_wood)

    # Platform & Parapet
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 5.8))
    plat = bpy.context.active_object
    plat.scale = (3.4, 3.4, 0.2)
    bpy.ops.object.transform_apply(scale=True)
    plat.data.materials.append(mat_wood)

    # Roof
    bpy.ops.mesh.primitive_cone_add(radius1=2.6, depth=1.5, location=(0, 0, 7.2))
    roof = bpy.context.active_object
    roof.data.materials.append(mat_wood)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    tower = bpy.context.active_object
    tower.name = "Watchtower"
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "watchtower.glb"), export_format='GLB')
    print("Exported watchtower.glb")

    # 4. Prisoner Stockade / Cage (Destructible Greek Captive Cage)
    clear_scene()
    mat_bars = create_mat("CageBars", (0.38, 0.26, 0.16, 1.0), metallic=0.0, roughness=0.85)
    # Floor and Roof
    for z in [0.1, 2.3]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z))
        c_plate = bpy.context.active_object
        c_plate.scale = (2.4, 2.4, 0.18)
        bpy.ops.object.transform_apply(scale=True)
        c_plate.data.materials.append(mat_bars)

    # Vertical Bars
    for x in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        for y in [-1.0, 1.0]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.1, location=(x, y, 1.2))
            bar = bpy.context.active_object
            bar.data.materials.append(mat_bars)
    for y in [-0.5, 0.0, 0.5]:
        for x in [-1.0, 1.0]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.1, location=(x, y, 1.2))
            bar = bpy.context.active_object
            bar.data.materials.append(mat_bars)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    cage = bpy.context.active_object
    cage.name = "PrisonerCage"
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "prisoner_cage.glb"), export_format='GLB')
    print("Exported prisoner_cage.glb")

    # 5. Roman Eagle Vexillum Banner & Greek Spartan Banner
    clear_scene()
    mat_gold = create_mat("BannerGold", (0.95, 0.78, 0.16, 1.0), metallic=0.95, roughness=0.2)
    mat_red = create_mat("BannerRed", (0.80, 0.08, 0.08, 1.0), metallic=0.0, roughness=0.5)

    # Pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=3.2, location=(0, 0, 1.6))
    pole = bpy.context.active_object
    pole.data.materials.append(mat_gold)

    # Vexillum Cloth
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.35, 2.2))
    cloth = bpy.context.active_object
    cloth.scale = (0.04, 0.70, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    cloth.data.materials.append(mat_red)

    # Eagle Finial
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, depth=0.30, location=(0, 0, 3.35))
    eagle = bpy.context.active_object
    eagle.data.materials.append(mat_gold)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    banner = bpy.context.active_object
    banner.name = "RomanBanner"
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "roman_banner.glb"), export_format='GLB')
    print("Exported roman_banner.glb")

def main():
    print("=== Generating Greek Allied Soldier ===")
    build_greek_soldier()

    print("\n=== Generating Roman Legionnaire ===")
    build_roman_soldier()

    print("\n=== Generating Roman Centurion Officer ===")
    build_roman_centurion()

    print("\n=== Generating Roman General Marcus Boss ===")
    build_roman_general()

    print("\n=== Generating Castrum Fortress Props & Cages ===")
    build_fortress_props()

    print("\nAll Campaign 3D models and skeletal animations successfully generated!")

if __name__ == "__main__":
    main()
