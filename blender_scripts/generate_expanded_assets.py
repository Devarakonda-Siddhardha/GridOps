"""
Blender script to generate 3D models and skeletal animations for the expanded Pantheon's Wrath:
1. 3D Gods: god_zeus.glb, god_poseidon.glb, god_hades.glb, god_ares.glb
2. Playable Classes: archer.glb (Cretan Toxotes), cavalry.glb (Thessalian Hippeus on Warhorse)
3. New Enemies: roman_archer.glb (Sagittarii), roman_cavalry.glb (Equites), minotaur.glb (Mythic Horned Brute)
4. Biome & Environment Props: roman_trireme.glb (Coastal naval galley), pine_tree.glb (Arcadian forest), volcanic_rock.glb (Tartarus chasm)
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
                bsdf.inputs["Emission Strength"].default_value = 2.0
    return mat

def assign_vg(obj, group_name):
    vg = obj.vertex_groups.new(name=group_name)
    indices = [v.index for v in obj.data.vertices]
    if indices:
        vg.add(indices, 1.0, 'REPLACE')

def create_humanoid_armature(prefix="Char", height_scale=1.0):
    arm_data = bpy.data.armatures.new(f"{prefix}ArmatureData")
    arm_obj = bpy.data.objects.new(f"{prefix}Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    s = height_scale
    root = eb.new("Root")
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.2 * s)

    hips = eb.new("Hips")
    hips.parent = root
    hips.head = (0, 0, 0.95 * s)
    hips.tail = (0, 0, 1.10 * s)

    spine = eb.new("Spine")
    spine.parent = hips
    spine.head = (0, 0, 1.10 * s)
    spine.tail = (0, 0, 1.30 * s)

    chest = eb.new("Chest")
    chest.parent = spine
    chest.head = (0, 0, 1.30 * s)
    chest.tail = (0, 0, 1.55 * s)

    neck = eb.new("Neck")
    neck.parent = chest
    neck.head = (0, 0, 1.55 * s)
    neck.tail = (0, 0, 1.65 * s)

    head = eb.new("Head")
    head.parent = neck
    head.head = (0, 0, 1.65 * s)
    head.tail = (0, 0, 1.95 * s)

    # Left Arm
    uarm_l = eb.new("UpperArm.L")
    uarm_l.parent = chest
    uarm_l.head = (0.24 * s, 0, 1.50 * s)
    uarm_l.tail = (0.48 * s, 0, 1.45 * s)

    farm_l = eb.new("Forearm.L")
    farm_l.parent = uarm_l
    farm_l.head = (0.48 * s, 0, 1.45 * s)
    farm_l.tail = (0.72 * s, 0.12 * s, 1.45 * s)

    hand_l = eb.new("Hand.L")
    hand_l.parent = farm_l
    hand_l.head = (0.72 * s, 0.12 * s, 1.45 * s)
    hand_l.tail = (0.84 * s, 0.18 * s, 1.45 * s)

    # Right Arm
    uarm_r = eb.new("UpperArm.R")
    uarm_r.parent = chest
    uarm_r.head = (-0.24 * s, 0, 1.50 * s)
    uarm_r.tail = (-0.48 * s, 0, 1.45 * s)

    farm_r = eb.new("Forearm.R")
    farm_r.parent = uarm_r
    farm_r.head = (-0.48 * s, 0, 1.45 * s)
    farm_r.tail = (-0.72 * s, 0.12 * s, 1.45 * s)

    hand_r = eb.new("Hand.R")
    hand_r.parent = farm_r
    hand_r.head = (-0.72 * s, 0.12 * s, 1.45 * s)
    hand_r.tail = (-0.84 * s, 0.18 * s, 1.45 * s)

    # Left Leg
    thigh_l = eb.new("Thigh.L")
    thigh_l.parent = hips
    thigh_l.head = (0.16 * s, 0, 0.95 * s)
    thigh_l.tail = (0.16 * s, 0, 0.50 * s)

    shin_l = eb.new("Shin.L")
    shin_l.parent = thigh_l
    shin_l.head = (0.16 * s, 0, 0.50 * s)
    shin_l.tail = (0.16 * s, 0, 0.10 * s)

    # Right Leg
    thigh_r = eb.new("Thigh.R")
    thigh_r.parent = hips
    thigh_r.head = (-0.16 * s, 0, 0.95 * s)
    thigh_r.tail = (-0.16 * s, 0, 0.50 * s)

    shin_r = eb.new("Shin.R")
    shin_r.parent = thigh_r
    shin_r.head = (-0.16 * s, 0, 0.50 * s)
    shin_r.tail = (-0.16 * s, 0, 0.10 * s)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# ==============================================================
# 1. 3D GOD MODELS: ZEUS, POSEIDON, HADES, ARES (Colossal 3.0m)
# ==============================================================
def build_god_model(god_name):
    clear_scene()
    s = 1.6  # Colossal scale ~3.0 meters tall!
    arm_obj = create_humanoid_armature(f"God{god_name.capitalize()}", height_scale=s)
    mesh_parts = []

    if god_name == "zeus":
        mat_robe = create_mat("ZeusWhite", (0.95, 0.95, 0.98, 1.0), metallic=0.1, roughness=0.4)
        mat_gold = create_mat("ZeusGold", (0.95, 0.82, 0.22, 1.0), metallic=0.95, roughness=0.2, emission=(0.95, 0.82, 0.22, 1.0))
        mat_skin = create_mat("ZeusSkin", (0.86, 0.70, 0.56, 1.0), metallic=0.0, roughness=0.6)
        mat_hair = create_mat("ZeusWhiteHair", (0.96, 0.96, 0.96, 1.0), metallic=0.0, roughness=0.7)
        mat_lightning = create_mat("ZeusLightning", (0.40, 0.85, 1.0, 1.0), metallic=0.2, roughness=0.1, emission=(0.40, 0.85, 1.0, 1.0))
    elif god_name == "poseidon":
        mat_robe = create_mat("PoseidonAzure", (0.05, 0.35, 0.55, 1.0), metallic=0.2, roughness=0.4)
        mat_gold = create_mat("PoseidonGold", (0.90, 0.75, 0.20, 1.0), metallic=0.92, roughness=0.25)
        mat_skin = create_mat("PoseidonSkin", (0.82, 0.68, 0.54, 1.0), metallic=0.0, roughness=0.6)
        mat_hair = create_mat("PoseidonAquaHair", (0.30, 0.75, 0.85, 1.0), metallic=0.1, roughness=0.5)
        mat_lightning = create_mat("OceanWater", (0.15, 0.85, 0.90, 1.0), metallic=0.1, roughness=0.1, emission=(0.15, 0.85, 0.90, 1.0))
    elif god_name == "hades":
        mat_robe = create_mat("HadesObsidian", (0.10, 0.08, 0.14, 1.0), metallic=0.3, roughness=0.5)
        mat_gold = create_mat("HadesDarkMetal", (0.35, 0.25, 0.40, 1.0), metallic=0.85, roughness=0.3)
        mat_skin = create_mat("HadesPaleSkin", (0.75, 0.72, 0.75, 1.0), metallic=0.0, roughness=0.7)
        mat_hair = create_mat("HadesShadowHair", (0.15, 0.12, 0.18, 1.0), metallic=0.1, roughness=0.8)
        mat_lightning = create_mat("SoulPurple", (0.65, 0.15, 0.95, 1.0), metallic=0.2, roughness=0.1, emission=(0.65, 0.15, 0.95, 1.0))
    else: # ares
        mat_robe = create_mat("AresCrimson", (0.75, 0.08, 0.08, 1.0), metallic=0.1, roughness=0.5)
        mat_gold = create_mat("AresBronze", (0.85, 0.50, 0.18, 1.0), metallic=0.92, roughness=0.3)
        mat_skin = create_mat("AresSkin", (0.84, 0.65, 0.50, 1.0), metallic=0.0, roughness=0.6)
        mat_hair = create_mat("AresRedCrest", (0.90, 0.12, 0.12, 1.0), metallic=0.1, roughness=0.6)
        mat_lightning = create_mat("BloodFlame", (1.0, 0.25, 0.05, 1.0), metallic=0.2, roughness=0.2, emission=(1.0, 0.25, 0.05, 1.0))

    # Torso (Muscled Divine Chiton or Cuirass)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.40 * s))
    torso = bpy.context.active_object
    torso.scale = (0.28 * s, 0.20 * s, 0.28 * s)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_gold if god_name in ["zeus", "ares"] else mat_robe)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Robe / Chiton lower garment
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32 * s, depth=0.65 * s, location=(0, 0, 0.90 * s))
    robe = bpy.context.active_object
    robe.data.materials.append(mat_robe)
    assign_vg(robe, "Hips")
    mesh_parts.append(robe)

    # Divine Cape / Mantle
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22 * s, 1.15 * s))
    cape = bpy.context.active_object
    cape.scale = (0.36 * s, 0.05 * s, 0.70 * s)
    bpy.ops.object.transform_apply(scale=True)
    cape.data.materials.append(mat_robe)
    assign_vg(cape, "Chest")
    mesh_parts.append(cape)

    # Divine Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17 * s, location=(0, 0, 1.80 * s))
    head = bpy.context.active_object
    head.scale = (0.95, 1.05, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mat_skin)
    assign_vg(head, "Head")
    mesh_parts.append(head)

    # Beard & Hair
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19 * s, location=(0, 0.06 * s, 1.72 * s))
    beard = bpy.context.active_object
    beard.scale = (0.8, 0.8, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    beard.data.materials.append(mat_hair)
    assign_vg(beard, "Head")
    mesh_parts.append(beard)

    # Crown / Helm / Laurel
    if god_name == "zeus":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.20 * s, minor_radius=0.03 * s, location=(0, 0, 1.90 * s))
        crown = bpy.context.active_object
        crown.data.materials.append(mat_gold)
        assign_vg(crown, "Head")
        mesh_parts.append(crown)
    elif god_name == "poseidon":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18 * s, depth=0.12 * s, location=(0, 0, 1.95 * s))
        crown = bpy.context.active_object
        crown.data.materials.append(mat_gold)
        assign_vg(crown, "Head")
        mesh_parts.append(crown)
    elif god_name == "hades":
        bpy.ops.mesh.primitive_cone_add(radius1=0.22 * s, depth=0.35 * s, location=(0, 0, 2.0 * s))
        helm = bpy.context.active_object
        helm.data.materials.append(mat_gold)
        assign_vg(helm, "Head")
        mesh_parts.append(helm)
    elif god_name == "ares":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.02 * s, 2.05 * s))
        crest = bpy.context.active_object
        crest.scale = (0.05 * s, 0.35 * s, 0.16 * s)
        bpy.ops.object.transform_apply(scale=True)
        crest.data.materials.append(mat_hair)
        assign_vg(crest, "Head")
        mesh_parts.append(crest)

    # Arms
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08 * s, depth=0.32 * s, location=(sign * 0.38 * s, 0, 1.48 * s))
        uarm = bpy.context.active_object
        uarm.rotation_euler = (0, math.radians(sign * 80), 0)
        bpy.ops.object.transform_apply(rotation=True)
        uarm.data.materials.append(mat_skin)
        assign_vg(uarm, f"UpperArm.{side}")
        mesh_parts.append(uarm)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.075 * s, depth=0.30 * s, location=(sign * 0.65 * s, 0.10 * s, 1.45 * s))
        farm = bpy.context.active_object
        farm.data.materials.append(mat_gold)
        assign_vg(farm, f"Forearm.{side}")
        mesh_parts.append(farm)

    # Legs (under robes)
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09 * s, depth=0.45 * s, location=(sign * 0.18 * s, 0, 0.35 * s))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_gold)
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Divine Weapon in Right Hand
    if god_name == "zeus":
        # Master Thunderbolt: jagged celestial bolt
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03 * s, depth=2.2 * s, location=(-0.82 * s, 0.30 * s, 1.45 * s))
        bolt = bpy.context.active_object
        bolt.rotation_euler = (math.radians(20), math.radians(15), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bolt.data.materials.append(mat_lightning)
        assign_vg(bolt, "Hand.R")
        mesh_parts.append(bolt)
    elif god_name == "poseidon":
        # Golden Trident
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035 * s, depth=2.8 * s, location=(-0.82 * s, 0.30 * s, 1.45 * s))
        shaft = bpy.context.active_object
        shaft.data.materials.append(mat_gold)
        assign_vg(shaft, "Hand.R")
        mesh_parts.append(shaft)

        for pr in [-0.14 * s, 0, 0.14 * s]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.025 * s, depth=0.45 * s, location=(-0.82 * s + pr, 0.30 * s, 2.7 * s))
            prong = bpy.context.active_object
            prong.data.materials.append(mat_lightning)
            assign_vg(prong, "Hand.R")
            mesh_parts.append(prong)
    elif god_name == "hades":
        # Underworld Bident
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035 * s, depth=2.7 * s, location=(-0.82 * s, 0.30 * s, 1.45 * s))
        shaft = bpy.context.active_object
        shaft.data.materials.append(mat_gold)
        assign_vg(shaft, "Hand.R")
        mesh_parts.append(shaft)

        for pr in [-0.12 * s, 0.12 * s]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.03 * s, depth=0.50 * s, location=(-0.82 * s + pr, 0.30 * s, 2.65 * s))
            prong = bpy.context.active_object
            prong.data.materials.append(mat_lightning)
            assign_vg(prong, "Hand.R")
            mesh_parts.append(prong)
    elif god_name == "ares":
        # Giant Two-Handed Battleaxe / Broadsword
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.84 * s, 0.40 * s, 1.50 * s))
        axe = bpy.context.active_object
        axe.scale = (0.05 * s, 0.40 * s, 0.90 * s)
        bpy.ops.object.transform_apply(scale=True)
        axe.data.materials.append(mat_lightning)
        assign_vg(axe, "Hand.R")
        mesh_parts.append(axe)

    # Join meshes
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    god_mesh = bpy.context.active_object
    god_mesh.name = f"God_{god_name.capitalize()}_Mesh"

    mod = god_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    god_mesh.parent = arm_obj

    # Animations: Idle (celestial levitation/sway), Bless (radiant praise), Cast (divine thrust)
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

    # 1. Idle (Celestial levitation)
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset()
    keyframe(1)
    pb["Root"].location = (0, 0, 0.08 * s)
    pb["Chest"].rotation_euler = (math.radians(3), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(-10), 0, math.radians(15))
    pb["UpperArm.R"].rotation_euler = (math.radians(-10), 0, math.radians(-15))
    keyframe(20)
    reset()
    keyframe(40)

    # 2. Bless (Raises celestial weapon to skies)
    act_bless = bpy.data.actions.new(name="Bless")
    arm_obj.animation_data.action = act_bless
    reset()
    keyframe(1)
    pb["UpperArm.R"].rotation_euler = (math.radians(110), 0, math.radians(-20))
    pb["Forearm.R"].rotation_euler = (math.radians(20), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(45), 0, math.radians(30))
    pb["Chest"].rotation_euler = (math.radians(-10), 0, 0)
    pb["Head"].rotation_euler = (math.radians(-15), 0, 0)
    pb["Root"].location = (0, 0, 0.15 * s)
    keyframe(15)
    keyframe(35)
    reset()
    keyframe(50)

    # 3. Cast (Thrusts weapon forward with divine blast)
    act_cast = bpy.data.actions.new(name="Cast")
    arm_obj.animation_data.action = act_cast
    reset()
    keyframe(1)
    # Wind up back
    pb["UpperArm.R"].rotation_euler = (math.radians(-40), math.radians(-20), 0)
    pb["Chest"].rotation_euler = (math.radians(10), 0, math.radians(10))
    keyframe(10)
    # Powerful strike forward
    pb["UpperArm.R"].rotation_euler = (math.radians(85), 0, 0)
    pb["Forearm.R"].rotation_euler = (math.radians(-10), 0, 0)
    pb["Chest"].rotation_euler = (math.radians(20), 0, math.radians(-15))
    pb["Root"].location = (0, 0, -0.05 * s)
    keyframe(18)
    reset()
    keyframe(36)

    bpy.ops.object.mode_set(mode='OBJECT')

    out_file = os.path.join(OUT_DIR, f"god_{god_name}.glb")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    god_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported God:", out_file)

# ==============================================================
# 2. PLAYABLE ARCHER (Cretan Toxotes: Bow, Quiver, Arrows)
# ==============================================================
def build_archer(is_roman=False):
    clear_scene()
    prefix = "RomanArcher" if is_roman else "Archer"
    mat_tunic = create_mat("ArchRed", (0.78, 0.12, 0.12, 1.0), metallic=0.0) if is_roman else create_mat("ArchGreen", (0.15, 0.45, 0.25, 1.0), metallic=0.0)
    mat_armor = create_mat("ArchMail", (0.65, 0.67, 0.70, 1.0), metallic=0.8) if is_roman else create_mat("ArchLeather", (0.42, 0.25, 0.14, 1.0), metallic=0.1)
    mat_skin = create_mat("ArchSkin", (0.84, 0.66, 0.52, 1.0), metallic=0.0, roughness=0.6)
    mat_wood = create_mat("BowWood", (0.35, 0.20, 0.10, 1.0), metallic=0.0, roughness=0.7)
    mat_string = create_mat("BowString", (0.9, 0.9, 0.9, 1.0), metallic=0.1, roughness=0.3)
    mat_feather = create_mat("ArrowFeather", (0.9, 0.85, 0.2, 1.0), metallic=0.0)

    arm_obj = create_humanoid_armature(prefix)
    mesh_parts = []

    # Torso
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.35))
    torso = bpy.context.active_object
    torso.scale = (0.24, 0.16, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_armor)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Skirt / Tunic
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.28, location=(0, 0, 1.05))
    skirt = bpy.context.active_object
    skirt.data.materials.append(mat_tunic)
    assign_vg(skirt, "Hips")
    mesh_parts.append(skirt)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 1.78))
    head = bpy.context.active_object
    head.scale = (0.95, 1.05, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mat_armor if is_roman else mat_skin)
    assign_vg(head, "Head")
    mesh_parts.append(head)

    # Headband / Helmet
    if not is_roman:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.02, location=(0, 0, 1.84))
        band = bpy.context.active_object
        band.data.materials.append(mat_tunic)
        assign_vg(band, "Head")
        mesh_parts.append(band)

    # Quiver on Back
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.55, location=(0.08, -0.18, 1.45))
    quiver = bpy.context.active_object
    quiver.rotation_euler = (math.radians(-25), 0, math.radians(20))
    bpy.ops.object.transform_apply(rotation=True)
    quiver.data.materials.append(mat_armor)
    assign_vg(quiver, "Chest")
    mesh_parts.append(quiver)

    # Arrows in quiver
    for off in [-0.03, 0.0, 0.03]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.3, location=(0.08 + off, -0.22, 1.70))
        arrow_f = bpy.context.active_object
        arrow_f.data.materials.append(mat_feather)
        assign_vg(arrow_f, "Chest")
        mesh_parts.append(arrow_f)

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
        farm.data.materials.append(mat_armor)  # Leather bracers
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
        shin.data.materials.append(mat_armor)  # Leather greaves/boots
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Recurve Bow (Left Hand) - curved arc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.3, location=(0.78, 0.20, 1.45))
    bow_body = bpy.context.active_object
    bow_body.rotation_euler = (math.radians(10), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    bow_body.data.materials.append(mat_wood)
    assign_vg(bow_body, "Hand.L")
    mesh_parts.append(bow_body)

    # Bowstring
    bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=1.2, location=(0.78, 0.12, 1.45))
    b_str = bpy.context.active_object
    b_str.data.materials.append(mat_string)
    assign_vg(b_str, "Hand.L")
    mesh_parts.append(b_str)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    arch_mesh = bpy.context.active_object
    arch_mesh.name = f"{prefix}Mesh"

    mod = arch_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    arch_mesh.parent = arm_obj

    # Build Animations for Archer: Idle, Run, Aim, Shoot, Dodge, Hit, Death
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

    # Idle
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset()
    keyframe(1)
    pb["Chest"].location = (0, 0, -0.015)
    keyframe(15)
    reset()
    keyframe(30)

    # Run
    act_run = bpy.data.actions.new(name="Run")
    arm_obj.animation_data.action = act_run
    reset()
    keyframe(1)
    pb["Thigh.R"].rotation_euler = (math.radians(-35), 0, 0)
    pb["Shin.R"].rotation_euler = (math.radians(25), 0, 0)
    pb["Thigh.L"].rotation_euler = (math.radians(35), 0, 0)
    pb["Shin.L"].rotation_euler = (math.radians(30), 0, 0)
    keyframe(6)
    reset()
    keyframe(12)
    pb["Thigh.L"].rotation_euler = (math.radians(-35), 0, 0)
    pb["Shin.L"].rotation_euler = (math.radians(25), 0, 0)
    pb["Thigh.R"].rotation_euler = (math.radians(35), 0, 0)
    pb["Shin.R"].rotation_euler = (math.radians(30), 0, 0)
    keyframe(18)
    reset()
    keyframe(24)

    # Aim: Left arm straight out holding bow, Right arm pulls back to cheek
    act_aim = bpy.data.actions.new(name="Aim")
    arm_obj.animation_data.action = act_aim
    reset()
    keyframe(1)
    pb["UpperArm.L"].rotation_euler = (math.radians(80), 0, math.radians(-35))
    pb["Forearm.L"].rotation_euler = (math.radians(-10), 0, 0)
    pb["UpperArm.R"].rotation_euler = (math.radians(50), 0, math.radians(65))
    pb["Forearm.R"].rotation_euler = (math.radians(95), 0, 0)
    pb["Chest"].rotation_euler = (0, 0, math.radians(-25))
    pb["Head"].rotation_euler = (0, 0, math.radians(25))
    keyframe(10)
    keyframe(30)

    # Shoot / Attack: Release string, recoil
    act_shoot = bpy.data.actions.new(name="Attack")
    arm_obj.animation_data.action = act_shoot
    reset()
    pb["UpperArm.L"].rotation_euler = (math.radians(80), 0, math.radians(-35))
    pb["Forearm.L"].rotation_euler = (math.radians(-10), 0, 0)
    pb["UpperArm.R"].rotation_euler = (math.radians(50), 0, math.radians(65))
    pb["Forearm.R"].rotation_euler = (math.radians(95), 0, 0)
    keyframe(1)
    # Release snap
    pb["UpperArm.R"].rotation_euler = (math.radians(40), 0, math.radians(30))
    pb["Forearm.R"].rotation_euler = (math.radians(20), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(85), 0, math.radians(-30))
    keyframe(6)
    # Recover
    reset()
    keyframe(18)

    # Dodge
    act_dodge = bpy.data.actions.new(name="Dodge")
    arm_obj.animation_data.action = act_dodge
    reset()
    keyframe(1)
    pb["Root"].location = (0, -0.6, 0.4)
    pb["Spine"].rotation_euler = (math.radians(-40), 0, 0)
    keyframe(8)
    reset()
    keyframe(16)

    # Hit
    act_hit = bpy.data.actions.new(name="Hit")
    arm_obj.animation_data.action = act_hit
    reset()
    keyframe(1)
    pb["Chest"].rotation_euler = (math.radians(-25), 0, 0)
    pb["Head"].rotation_euler = (math.radians(20), 0, 0)
    keyframe(5)
    reset()
    keyframe(14)

    # Death
    act_death = bpy.data.actions.new(name="Death")
    arm_obj.animation_data.action = act_death
    reset()
    keyframe(1)
    pb["Root"].location = (0, -0.4, -0.85)
    pb["Hips"].rotation_euler = (math.radians(-90), 0, 0)
    keyframe(15)
    keyframe(30)

    bpy.ops.object.mode_set(mode='OBJECT')

    filename = "roman_archer.glb" if is_roman else "archer.glb"
    out_file = os.path.join(OUT_DIR, filename)
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    arch_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported Archer:", out_file)

# ==============================================================
# 3. PLAYABLE & ENEMY CAVALRY (Armored Warhorse + Armed Rider)
# ==============================================================
def build_cavalry(is_roman=False):
    clear_scene()
    prefix = "RomanCavalry" if is_roman else "Cavalry"
    mat_horse_coat = create_mat("HorseBlack", (0.12, 0.10, 0.09, 1.0), roughness=0.6) if is_roman else create_mat("HorseChestnut", (0.38, 0.20, 0.10, 1.0), roughness=0.6)
    mat_saddle = create_mat("CavRed", (0.75, 0.10, 0.10, 1.0)) if is_roman else create_mat("CavBlue", (0.10, 0.35, 0.80, 1.0))
    mat_armor = create_mat("CavIron", (0.70, 0.72, 0.75, 1.0), metallic=0.9) if is_roman else create_mat("CavBronze", (0.82, 0.55, 0.22, 1.0), metallic=0.9)
    mat_skin = create_mat("CavSkin", (0.84, 0.66, 0.52, 1.0), roughness=0.6)
    mat_wood = create_mat("LanceWood", (0.32, 0.20, 0.10, 1.0), roughness=0.7)

    # Armature for Cavalry (Root -> HorseBody -> Neck/Head, 4 Legs, RiderTorso, Arms)
    arm_data = bpy.data.armatures.new(f"{prefix}ArmData")
    arm_obj = bpy.data.objects.new(f"{prefix}Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    # Horse Bones
    root = eb.new("Root")
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.3)

    h_body = eb.new("HorseBody")
    h_body.parent = root
    h_body.head = (0, 0, 1.2)
    h_body.tail = (0, 0.6, 1.3)

    h_neck = eb.new("HorseNeck")
    h_neck.parent = h_body
    h_neck.head = (0, 0.6, 1.3)
    h_neck.tail = (0, 1.1, 1.8)

    h_head = eb.new("HorseHead")
    h_head.parent = h_neck
    h_head.head = (0, 1.1, 1.8)
    h_head.tail = (0, 1.4, 1.6)

    # 4 Horse Legs
    for side, sign in [("FL", 1), ("FR", -1)]:
        leg = eb.new(f"Leg.{side}")
        leg.parent = h_body
        leg.head = (sign * 0.35, 0.5, 1.1)
        leg.tail = (sign * 0.35, 0.5, 0.1)

    for side, sign in [("BL", 1), ("BR", -1)]:
        leg = eb.new(f"Leg.{side}")
        leg.parent = h_body
        leg.head = (sign * 0.35, -0.5, 1.1)
        leg.tail = (sign * 0.35, -0.5, 0.1)

    # Rider Bones
    r_torso = eb.new("RiderTorso")
    r_torso.parent = h_body
    r_torso.head = (0, 0.05, 1.5)
    r_torso.tail = (0, 0.05, 1.95)

    r_head = eb.new("RiderHead")
    r_head.parent = r_torso
    r_head.head = (0, 0.05, 1.95)
    r_head.tail = (0, 0.05, 2.3)

    # Rider Arms
    r_arm_l = eb.new("RiderArm.L")
    r_arm_l.parent = r_torso
    r_arm_l.head = (0.28, 0.05, 1.9)
    r_arm_l.tail = (0.55, 0.35, 1.8)

    r_arm_r = eb.new("RiderArm.R")
    r_arm_r.parent = r_torso
    r_arm_r.head = (-0.28, 0.05, 1.9)
    r_arm_r.tail = (-0.55, 0.35, 1.8)

    bpy.ops.object.mode_set(mode='OBJECT')

    mesh_parts = []

    # 1. Horse Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.5, location=(0, 0, 1.25))
    h_barrel = bpy.context.active_object
    h_barrel.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    h_barrel.data.materials.append(mat_horse_coat)
    assign_vg(h_barrel, "HorseBody")
    mesh_parts.append(h_barrel)

    # 2. Horse Neck & Head
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, location=(0, 0.85, 1.6))
    h_neck_m = bpy.context.active_object
    h_neck_m.rotation_euler = (math.radians(45), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    h_neck_m.data.materials.append(mat_horse_coat)
    assign_vg(h_neck_m, "HorseNeck")
    mesh_parts.append(h_neck_m)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.25, 1.7))
    h_head_m = bpy.context.active_object
    h_head_m.scale = (0.20, 0.45, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    h_head_m.data.materials.append(mat_armor)  # Chamfron armor
    assign_vg(h_head_m, "HorseHead")
    mesh_parts.append(h_head_m)

    # 3. Horse 4 Legs
    for side, sign, y_pos in [("FL", 1, 0.5), ("FR", -1, 0.5), ("BL", 1, -0.5), ("BR", -1, -0.5)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=1.0, location=(sign * 0.35, y_pos, 0.6))
        leg_m = bpy.context.active_object
        leg_m.data.materials.append(mat_horse_coat)
        assign_vg(leg_m, f"Leg.{side}")
        mesh_parts.append(leg_m)

    # 4. Saddle / Caparison
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 1.45))
    saddle = bpy.context.active_object
    saddle.scale = (0.50, 0.65, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    saddle.data.materials.append(mat_saddle)
    assign_vg(saddle, "HorseBody")
    mesh_parts.append(saddle)

    # 5. Mounted Rider Torso & Armor
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 1.8))
    r_body_m = bpy.context.active_object
    r_body_m.scale = (0.26, 0.18, 0.28)
    bpy.ops.object.transform_apply(scale=True)
    r_body_m.data.materials.append(mat_armor)
    assign_vg(r_body_m, "RiderTorso")
    mesh_parts.append(r_body_m)

    # Rider Head & Crested Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0.05, 2.15))
    r_head_m = bpy.context.active_object
    r_head_m.data.materials.append(mat_armor)
    assign_vg(r_head_m, "RiderHead")
    mesh_parts.append(r_head_m)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 2.32))
    r_crest = bpy.context.active_object
    r_crest.scale = (0.04, 0.25, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    r_crest.data.materials.append(mat_saddle)
    assign_vg(r_crest, "RiderHead")
    mesh_parts.append(r_crest)

    # Rider Arms & Long Cavalry Lance (Xyston)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.5, location=(0.42, 0.2, 1.85))
    l_arm_m = bpy.context.active_object
    l_arm_m.rotation_euler = (math.radians(30), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    l_arm_m.data.materials.append(mat_armor)
    assign_vg(l_arm_m, "RiderArm.L")
    mesh_parts.append(l_arm_m)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.5, location=(-0.42, 0.2, 1.85))
    r_arm_m = bpy.context.active_object
    r_arm_m.rotation_euler = (math.radians(30), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    r_arm_m.data.materials.append(mat_armor)
    assign_vg(r_arm_m, "RiderArm.R")
    mesh_parts.append(r_arm_m)

    # 3.2m Cavalry Lance in Right Hand pointing forward
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=3.2, location=(-0.55, 1.2, 1.85))
    lance = bpy.context.active_object
    lance.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    lance.data.materials.append(mat_wood)
    assign_vg(lance, "RiderArm.R")
    mesh_parts.append(lance)

    bpy.ops.mesh.primitive_cone_add(radius1=0.06, depth=0.4, location=(-0.55, 2.8, 1.85))
    lance_tip = bpy.context.active_object
    lance_tip.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    lance_tip.data.materials.append(mat_armor)
    assign_vg(lance_tip, "RiderArm.R")
    mesh_parts.append(lance_tip)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    cav_mesh = bpy.context.active_object
    cav_mesh.name = f"{prefix}Mesh"

    mod = cav_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    cav_mesh.parent = arm_obj

    # Cavalry Animations: Idle, Walk, Gallop, Charge/Attack, Hit, Death
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

    # Idle
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset()
    keyframe(1)
    pb["HorseBody"].location = (0, 0, -0.03)
    pb["HorseNeck"].rotation_euler = (math.radians(5), 0, 0)
    keyframe(15)
    reset()
    keyframe(30)

    # Gallop / Run: Legs alternating, horse pitching forward/back
    act_gallop = bpy.data.actions.new(name="Run")
    arm_obj.animation_data.action = act_gallop
    reset()
    keyframe(1)

    # Phase 1: Front legs reach forward, back legs gather
    pb["Leg.FL"].rotation_euler = (math.radians(-35), 0, 0)
    pb["Leg.FR"].rotation_euler = (math.radians(-25), 0, 0)
    pb["Leg.BL"].rotation_euler = (math.radians(35), 0, 0)
    pb["Leg.BR"].rotation_euler = (math.radians(25), 0, 0)
    pb["HorseBody"].rotation_euler = (math.radians(8), 0, 0)
    pb["HorseBody"].location = (0, 0, 0.08)
    keyframe(6)

    reset()
    keyframe(12)

    # Phase 2: Back legs push back, front legs compress
    pb["Leg.FL"].rotation_euler = (math.radians(35), 0, 0)
    pb["Leg.FR"].rotation_euler = (math.radians(25), 0, 0)
    pb["Leg.BL"].rotation_euler = (math.radians(-35), 0, 0)
    pb["Leg.BR"].rotation_euler = (math.radians(-25), 0, 0)
    pb["HorseBody"].rotation_euler = (math.radians(-8), 0, 0)
    pb["HorseBody"].location = (0, 0, 0.05)
    keyframe(18)

    reset()
    keyframe(24)

    # Charge / Attack: Couched lance lowered for deadly piercing run
    act_charge = bpy.data.actions.new(name="Attack")
    arm_obj.animation_data.action = act_charge
    reset()
    keyframe(1)
    # Lower lance horizontally and lean rider forward
    pb["RiderTorso"].rotation_euler = (math.radians(25), 0, 0)
    pb["RiderArm.R"].rotation_euler = (math.radians(35), 0, 0)
    pb["HorseNeck"].rotation_euler = (math.radians(-10), 0, 0)
    keyframe(8)
    keyframe(20)
    reset()
    keyframe(28)

    # Hit
    act_hit = bpy.data.actions.new(name="Hit")
    arm_obj.animation_data.action = act_hit
    reset()
    keyframe(1)
    pb["HorseNeck"].rotation_euler = (math.radians(25), 0, 0)
    pb["HorseBody"].rotation_euler = (math.radians(-15), 0, 0)
    keyframe(6)
    reset()
    keyframe(15)

    # Death
    act_death = bpy.data.actions.new(name="Death")
    arm_obj.animation_data.action = act_death
    reset()
    keyframe(1)
    pb["Root"].location = (0, 0, -0.9)
    pb["HorseBody"].rotation_euler = (0, math.radians(80), 0)
    keyframe(18)
    keyframe(32)

    bpy.ops.object.mode_set(mode='OBJECT')

    filename = "roman_cavalry.glb" if is_roman else "cavalry.glb"
    out_file = os.path.join(OUT_DIR, filename)
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    cav_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported Cavalry:", out_file)

# ==============================================================
# 4. MYTHIC UNDERWORLD MINOTAUR (3.2m Horned Beast with Stone Maul)
# ==============================================================
def build_minotaur():
    clear_scene()
    s = 1.7  # Towering 3.2m
    mat_fur = create_mat("MinoFur", (0.22, 0.15, 0.12, 1.0), roughness=0.8)
    mat_horn = create_mat("MinoHorn", (0.75, 0.70, 0.60, 1.0), roughness=0.4)
    mat_hoof = create_mat("MinoHoof", (0.10, 0.08, 0.06, 1.0), roughness=0.5)
    mat_stone = create_mat("MinoMaulStone", (0.45, 0.45, 0.48, 1.0), roughness=0.9)
    mat_wood = create_mat("MaulWood", (0.35, 0.22, 0.12, 1.0), roughness=0.7)
    mat_eye = create_mat("MinoEye", (1.0, 0.1, 0.05, 1.0), emission=(1.0, 0.1, 0.05, 1.0))

    arm_obj = create_humanoid_armature("Minotaur", height_scale=s)
    mesh_parts = []

    # Massive Muscular Torso
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.45 * s))
    torso = bpy.context.active_object
    torso.scale = (0.38 * s, 0.28 * s, 0.35 * s)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_fur)
    assign_vg(torso, "Chest")
    mesh_parts.append(torso)

    # Bull Head & Snout
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.12 * s, 1.85 * s))
    head = bpy.context.active_object
    head.scale = (0.24 * s, 0.32 * s, 0.26 * s)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mat_fur)
    assign_vg(head, "Head")
    mesh_parts.append(head)

    # Glowing Red Eyes
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03 * s, location=(sign * 0.14 * s, 0.32 * s, 1.90 * s))
        eye = bpy.context.active_object
        eye.data.materials.append(mat_eye)
        assign_vg(eye, "Head")
        mesh_parts.append(eye)

    # Massive Curved Horns
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.08 * s, depth=0.70 * s, location=(sign * 0.35 * s, 0.15 * s, 2.10 * s))
        horn = bpy.context.active_object
        horn.rotation_euler = (math.radians(-25), math.radians(sign * 65), 0)
        bpy.ops.object.transform_apply(rotation=True)
        horn.data.materials.append(mat_horn)
        assign_vg(horn, "Head")
        mesh_parts.append(horn)

    # Heavy Arms
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12 * s, depth=0.38 * s, location=(sign * 0.46 * s, 0, 1.48 * s))
        uarm = bpy.context.active_object
        uarm.rotation_euler = (0, math.radians(sign * 80), 0)
        bpy.ops.object.transform_apply(rotation=True)
        uarm.data.materials.append(mat_fur)
        assign_vg(uarm, f"UpperArm.{side}")
        mesh_parts.append(uarm)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.11 * s, depth=0.35 * s, location=(sign * 0.78 * s, 0.12 * s, 1.45 * s))
        farm = bpy.context.active_object
        farm.data.materials.append(mat_fur)
        assign_vg(farm, f"Forearm.{side}")
        mesh_parts.append(farm)

    # Cloven Hoof Legs
    for side, sign in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14 * s, depth=0.50 * s, location=(sign * 0.20 * s, 0, 0.75 * s))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_fur)
        assign_vg(thigh, f"Thigh.{side}")
        mesh_parts.append(thigh)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.12 * s, depth=0.45 * s, location=(sign * 0.20 * s, 0, 0.30 * s))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_hoof)
        assign_vg(shin, f"Shin.{side}")
        mesh_parts.append(shin)

    # Gigantic Stone War Maul (in Right Hand)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05 * s, depth=2.4 * s, location=(-0.95 * s, 0.40 * s, 1.50 * s))
    shaft = bpy.context.active_object
    shaft.data.materials.append(mat_wood)
    assign_vg(shaft, "Hand.R")
    mesh_parts.append(shaft)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.95 * s, 0.40 * s, 2.50 * s))
    head_m = bpy.context.active_object
    head_m.scale = (0.35 * s, 0.55 * s, 0.35 * s)
    bpy.ops.object.transform_apply(scale=True)
    head_m.data.materials.append(mat_stone)
    assign_vg(head_m, "Hand.R")
    mesh_parts.append(head_m)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    mino_mesh = bpy.context.active_object
    mino_mesh.name = "MinotaurMesh"

    mod = mino_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    mino_mesh.parent = arm_obj

    # Animations: Idle, Walk, Attack (Ground Slam), Roar, Hit, Death
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

    # Idle
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset()
    keyframe(1)
    pb["Spine"].rotation_euler = (math.radians(5), 0, 0)
    pb["Head"].rotation_euler = (math.radians(-5), 0, 0)
    keyframe(15)
    reset()
    keyframe(30)

    # Walk / Run
    act_walk = bpy.data.actions.new(name="Run")
    arm_obj.animation_data.action = act_walk
    reset()
    keyframe(1)
    pb["Thigh.R"].rotation_euler = (math.radians(-30), 0, 0)
    pb["Thigh.L"].rotation_euler = (math.radians(30), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(-25), 0, 0)
    pb["UpperArm.R"].rotation_euler = (math.radians(25), 0, 0)
    keyframe(8)
    reset()
    keyframe(16)
    pb["Thigh.L"].rotation_euler = (math.radians(-30), 0, 0)
    pb["Thigh.R"].rotation_euler = (math.radians(30), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(25), 0, 0)
    pb["UpperArm.R"].rotation_euler = (math.radians(-25), 0, 0)
    keyframe(24)
    reset()
    keyframe(32)

    # Attack: Massive two-handed earth shattering ground slam
    act_slam = bpy.data.actions.new(name="Attack")
    arm_obj.animation_data.action = act_slam
    reset()
    keyframe(1)
    # Wind up high overhead
    pb["UpperArm.R"].rotation_euler = (math.radians(110), 0, math.radians(-15))
    pb["UpperArm.L"].rotation_euler = (math.radians(100), 0, math.radians(25))
    pb["Chest"].rotation_euler = (math.radians(-25), 0, 0)
    keyframe(12)
    # Violent ground slam
    pb["UpperArm.R"].rotation_euler = (math.radians(-40), 0, 0)
    pb["UpperArm.L"].rotation_euler = (math.radians(-40), 0, 0)
    pb["Chest"].rotation_euler = (math.radians(45), 0, 0)
    pb["Root"].location = (0, 0, -0.2 * s)
    keyframe(18)
    reset()
    keyframe(36)

    # Hit
    act_hit = bpy.data.actions.new(name="Hit")
    arm_obj.animation_data.action = act_hit
    reset()
    keyframe(1)
    pb["Chest"].rotation_euler = (math.radians(-20), 0, 0)
    keyframe(5)
    reset()
    keyframe(15)

    # Death
    act_death = bpy.data.actions.new(name="Death")
    arm_obj.animation_data.action = act_death
    reset()
    keyframe(1)
    pb["Root"].location = (0, 0, -0.85 * s)
    pb["Hips"].rotation_euler = (math.radians(-85), 0, 0)
    keyframe(18)
    keyframe(35)

    bpy.ops.object.mode_set(mode='OBJECT')

    out_file = os.path.join(OUT_DIR, "minotaur.glb")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mino_mesh.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB',
        export_animations=True
    )
    print("Exported Minotaur:", out_file)

# ==============================================================
# 5. ENVIRONMENT & BIOME PROPS: TRIREME, PINE TREE, VOLCANIC ROCK
# ==============================================================
def build_environment_props():
    # 1. Roman War Trireme (Coastal Biome)
    clear_scene()
    mat_hull = create_mat("TriremeWood", (0.38, 0.22, 0.12, 1.0), roughness=0.7)
    mat_sail = create_mat("TriremeSail", (0.85, 0.15, 0.15, 1.0), roughness=0.6) # Red Roman Sail
    mat_bronze = create_mat("TriremeBronze", (0.85, 0.60, 0.20, 1.0), metallic=0.9)

    mesh_parts = []
    # Ship Hull
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
    hull = bpy.context.active_object
    hull.scale = (3.5, 12.0, 2.5)
    bpy.ops.object.transform_apply(scale=True)
    hull.data.materials.append(mat_hull)
    mesh_parts.append(hull)

    # Bronze Ram Prow
    bpy.ops.mesh.primitive_cone_add(radius1=1.2, depth=3.0, location=(0, 7.2, 0.8))
    ram = bpy.context.active_object
    ram.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    ram.data.materials.append(mat_bronze)
    mesh_parts.append(ram)

    # Mast & Sail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=9.0, location=(0, 0, 6.0))
    mast = bpy.context.active_object
    mast.data.materials.append(mat_hull)
    mesh_parts.append(mast)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.2, 7.0))
    sail = bpy.context.active_object
    sail.scale = (5.5, 0.1, 4.0)
    bpy.ops.object.transform_apply(scale=True)
    sail.data.materials.append(mat_sail)
    mesh_parts.append(sail)

    # Join and export
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    trireme = bpy.context.active_object
    trireme.name = "RomanTrireme"
    out_file = os.path.join(OUT_DIR, "roman_trireme.glb")
    bpy.ops.export_scene.gltf(filepath=out_file, use_selection=True, export_format='GLB')
    print("Exported Trireme:", out_file)

    # 2. Pine Tree (Arcadia Valley)
    clear_scene()
    mat_trunk = create_mat("PineTrunk", (0.35, 0.22, 0.12, 1.0), roughness=0.8)
    mat_leaves = create_mat("PineNeedles", (0.12, 0.35, 0.16, 1.0), roughness=0.6)
    mesh_parts = []

    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=5.0, location=(0, 0, 2.5))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_trunk)
    mesh_parts.append(trunk)

    # 3 tiers of pine cones
    for i, (r, z) in enumerate([(2.2, 4.0), (1.7, 5.8), (1.2, 7.2)]):
        bpy.ops.mesh.primitive_cone_add(radius1=r, depth=2.4, location=(0, 0, z))
        foliage = bpy.context.active_object
        foliage.data.materials.append(mat_leaves)
        mesh_parts.append(foliage)

    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    pine = bpy.context.active_object
    pine.name = "PineTree"
    out_file = os.path.join(OUT_DIR, "pine_tree.glb")
    bpy.ops.export_scene.gltf(filepath=out_file, use_selection=True, export_format='GLB')
    print("Exported Pine Tree:", out_file)

    # 3. Volcanic Basalt Rock (Tartarus Chasm)
    clear_scene()
    mat_basalt = create_mat("BasaltRock", (0.15, 0.14, 0.16, 1.0), roughness=0.8)
    mat_magma = create_mat("MagmaVein", (1.0, 0.35, 0.05, 1.0), emission=(1.0, 0.35, 0.05, 1.0))
    mesh_parts = []

    for off, rot in [((0, 0, 2.0), 0), ((1.0, 0.5, 1.6), 15), ((-0.8, -0.6, 1.4), -20)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=4.0, location=off)
        rock = bpy.context.active_object
        rock.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        rock.data.materials.append(mat_basalt)
        mesh_parts.append(rock)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.2, 0.2, 1.2))
    magma = bpy.context.active_object
    magma.scale = (0.2, 0.2, 1.8)
    bpy.ops.object.transform_apply(scale=True)
    magma.data.materials.append(mat_magma)
    mesh_parts.append(magma)

    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    v_rock = bpy.context.active_object
    v_rock.name = "VolcanicRock"
    out_file = os.path.join(OUT_DIR, "volcanic_rock.glb")
    bpy.ops.export_scene.gltf(filepath=out_file, use_selection=True, export_format='GLB')
    print("Exported Volcanic Rock:", out_file)

if __name__ == "__main__":
    print("=== Generating 3D Gods ===")
    for god in ["zeus", "poseidon", "hades", "ares"]:
        build_god_model(god)

    print("=== Generating Archer (Playable & Roman) ===")
    build_archer(is_roman=False)
    build_archer(is_roman=True)

    print("=== Generating Cavalry (Playable & Roman) ===")
    build_cavalry(is_roman=False)
    build_cavalry(is_roman=True)

    print("=== Generating Minotaur Boss ===")
    build_minotaur()

    print("=== Generating Environment & Biome Props ===")
    build_environment_props()

    print("=== ALL ASSETS GENERATED SUCCESSFULLY! ===")
