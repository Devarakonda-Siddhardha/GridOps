"""
Blender script to generate a fully rigged and animated Greek Hoplite Warrior.
Exports warrior.glb with embedded mesh, materials, armature, and animations:
- Idle
- Run
- Attack1
- Attack2
- Pray
- Dodge
- Hit
- Death
"""

import bpy
import math
from mathutils import Vector, Euler, Matrix

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_material(name, base_color, metallic=0.0, roughness=0.5, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            # Blender 4.x emission color
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 1.0
    return mat

def create_warrior():
    clear_scene()

    # Materials
    mat_bronze = create_material("BronzeArmor", (0.82, 0.54, 0.22, 1.0), metallic=0.9, roughness=0.3)
    mat_gold = create_material("GoldTrim", (0.95, 0.75, 0.15, 1.0), metallic=0.95, roughness=0.25)
    mat_skin = create_material("Skin", (0.86, 0.68, 0.53, 1.0), metallic=0.0, roughness=0.6)
    mat_red = create_material("SpartanRed", (0.75, 0.08, 0.08, 1.0), metallic=0.0, roughness=0.5)
    mat_white = create_material("TunicWhite", (0.9, 0.9, 0.88, 1.0), metallic=0.0, roughness=0.7)
    mat_iron = create_material("IronBlade", (0.6, 0.65, 0.7, 1.0), metallic=0.95, roughness=0.2)
    mat_leather = create_material("Leather", (0.28, 0.16, 0.08, 1.0), metallic=0.1, roughness=0.7)

    # 1. Create Armature
    arm_data = bpy.data.armatures.new("WarriorArmatureData")
    arm_obj = bpy.data.objects.new("WarriorArmature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = arm_data.edit_bones

    # Bones hierarchy
    root = edit_bones.new("Root")
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.2)

    hips = edit_bones.new("Hips")
    hips.parent = root
    hips.head = (0, 0, 0.95)
    hips.tail = (0, 0, 1.1)

    spine = edit_bones.new("Spine")
    spine.parent = hips
    spine.head = (0, 0, 1.1)
    spine.tail = (0, 0, 1.3)

    chest = edit_bones.new("Chest")
    chest.parent = spine
    chest.head = (0, 0, 1.3)
    chest.tail = (0, 0, 1.55)

    neck = edit_bones.new("Neck")
    neck.parent = chest
    neck.head = (0, 0, 1.55)
    neck.tail = (0, 0, 1.65)

    head = edit_bones.new("Head")
    head.parent = neck
    head.head = (0, 0, 1.65)
    head.tail = (0, 0, 1.95)

    # Left Arm (Shield)
    uarm_l = edit_bones.new("UpperArm.L")
    uarm_l.parent = chest
    uarm_l.head = (0.24, 0, 1.5)
    uarm_l.tail = (0.50, 0, 1.45)

    farm_l = edit_bones.new("Forearm.L")
    farm_l.parent = uarm_l
    farm_l.head = (0.50, 0, 1.45)
    farm_l.tail = (0.75, 0.15, 1.45)

    hand_l = edit_bones.new("Hand.L")
    hand_l.parent = farm_l
    hand_l.head = (0.75, 0.15, 1.45)
    hand_l.tail = (0.85, 0.20, 1.45)

    # Right Arm (Sword)
    uarm_r = edit_bones.new("UpperArm.R")
    uarm_r.parent = chest
    uarm_r.head = (-0.24, 0, 1.5)
    uarm_r.tail = (-0.50, 0, 1.45)

    farm_r = edit_bones.new("Forearm.R")
    farm_r.parent = uarm_r
    farm_r.head = (-0.50, 0, 1.45)
    farm_r.tail = (-0.75, 0.10, 1.45)

    hand_r = edit_bones.new("Hand.R")
    hand_r.parent = farm_r
    hand_r.head = (-0.75, 0.10, 1.45)
    hand_r.tail = (-0.85, 0.15, 1.45)

    # Left Leg
    thigh_l = edit_bones.new("Thigh.L")
    thigh_l.parent = hips
    thigh_l.head = (0.16, 0, 0.95)
    thigh_l.tail = (0.16, 0, 0.5)

    shin_l = edit_bones.new("Shin.L")
    shin_l.parent = thigh_l
    shin_l.head = (0.16, 0, 0.5)
    shin_l.tail = (0.16, 0, 0.1)

    foot_l = edit_bones.new("Foot.L")
    foot_l.parent = shin_l
    foot_l.head = (0.16, 0, 0.1)
    foot_l.tail = (0.16, 0.2, 0)

    # Right Leg
    thigh_r = edit_bones.new("Thigh.R")
    thigh_r.parent = hips
    thigh_r.head = (-0.16, 0, 0.95)
    thigh_r.tail = (-0.16, 0, 0.5)

    shin_r = edit_bones.new("Shin.R")
    shin_r.parent = thigh_r
    shin_r.head = (-0.16, 0, 0.5)
    shin_r.tail = (-0.16, 0, 0.1)

    foot_r = edit_bones.new("Foot.R")
    foot_r.parent = shin_r
    foot_r.head = (-0.16, 0, 0.1)
    foot_r.tail = (-0.16, 0.2, 0)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 2. Build Meshes for Warrior Parts
    parts = []

    def make_cube(name, loc, scale, mat, bone_name):
        bpy.ops.mesh.primitive_cube_add(location=loc, scale=scale)
        obj = bpy.context.active_object
        obj.name = name
        obj.data.materials.append(mat)
        parts.append((obj, bone_name))
        return obj

    def make_cylinder(name, loc, radius, depth, mat, bone_name, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        obj.data.materials.append(mat)
        parts.append((obj, bone_name))
        return obj

    def make_uv_sphere(name, loc, radius, mat, bone_name, scale=(1,1,1)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        obj.data.materials.append(mat)
        parts.append((obj, bone_name))
        return obj

    # Torso (Muscular Bronze Cuirass)
    make_cube("Cuirass_Chest", (0, 0, 1.42), (0.22, 0.14, 0.16), mat_bronze, "Chest")
    make_cube("Cuirass_Abdomen", (0, 0, 1.2), (0.19, 0.12, 0.13), mat_bronze, "Spine")
    make_cube("Hips_Pteruges", (0, 0, 1.0), (0.21, 0.15, 0.12), mat_leather, "Hips")

    # Red Spartan Cape
    cape = make_cube("Spartan_Cape", (0, -0.16, 1.15), (0.24, 0.02, 0.38), mat_red, "Chest")

    # Head & Corinthian Helmet
    make_uv_sphere("Head_Face", (0, 0, 1.76), 0.12, mat_skin, "Head")
    make_cube("Helmet_Dome", (0, 0.01, 1.80), (0.14, 0.15, 0.14), mat_bronze, "Head")
    make_cube("Helmet_NoseGuard", (0, 0.15, 1.74), (0.02, 0.02, 0.07), mat_gold, "Head")
    make_cube("Helmet_Cheeks", (0, 0.11, 1.70), (0.13, 0.05, 0.06), mat_bronze, "Head")
    # Iconic Red Crest / Plume
    crest = make_cube("Helmet_Crest", (0, 0, 1.98), (0.03, 0.18, 0.09), mat_red, "Head")

    # Arms
    make_cylinder("Shoulder_L", (0.26, 0, 1.50), 0.08, 0.16, mat_bronze, "UpperArm.L", rot=(0, math.radians(90), 0))
    make_cylinder("Arm_L", (0.38, 0, 1.48), 0.06, 0.22, mat_skin, "UpperArm.L", rot=(0, math.radians(90), 0))
    make_cylinder("Forearm_L", (0.62, 0.08, 1.45), 0.06, 0.24, mat_bronze, "Forearm.L", rot=(math.radians(30), 0, math.radians(90)))

    make_cylinder("Shoulder_R", (-0.26, 0, 1.50), 0.08, 0.16, mat_bronze, "UpperArm.R", rot=(0, math.radians(-90), 0))
    make_cylinder("Arm_R", (-0.38, 0, 1.48), 0.06, 0.22, mat_skin, "UpperArm.R", rot=(0, math.radians(-90), 0))
    make_cylinder("Forearm_R", (-0.62, 0.05, 1.45), 0.06, 0.24, mat_bronze, "Forearm.R", rot=(math.radians(15), 0, math.radians(-90)))

    # Legs (Bronze Greaves + Thighs)
    make_cylinder("Thigh_L", (0.16, 0, 0.72), 0.08, 0.38, mat_skin, "Thigh.L")
    make_cylinder("Greave_L", (0.16, 0, 0.30), 0.07, 0.36, mat_bronze, "Shin.L")
    make_cube("Sandal_L", (0.16, 0.08, 0.05), (0.07, 0.13, 0.05), mat_leather, "Foot.L")

    make_cylinder("Thigh_R", (-0.16, 0, 0.72), 0.08, 0.38, mat_skin, "Thigh.R")
    make_cylinder("Greave_R", (-0.16, 0, 0.30), 0.07, 0.36, mat_bronze, "Shin.R")
    make_cube("Sandal_R", (-0.16, 0.08, 0.05), (0.07, 0.13, 0.05), mat_leather, "Foot.R")

    # Greek Aspis (Round Hoplon Shield) attached to Hand.L
    # Shield face is a flattened cylinder
    shield_rim = make_cylinder("Shield_Rim", (0.86, 0.35, 1.45), 0.44, 0.04, mat_gold, "Hand.L", rot=(math.radians(90), 0, 0))
    shield_face = make_cylinder("Shield_Face", (0.86, 0.37, 1.45), 0.40, 0.05, mat_bronze, "Hand.L", rot=(math.radians(90), 0, 0))
    # Lambda emblem in center of shield (Spartan Λ)
    lambda1 = make_cube("Shield_Lambda1", (0.83, 0.40, 1.45), (0.03, 0.02, 0.18), mat_red, "Hand.L")
    lambda1.rotation_euler = (0, math.radians(25), 0)
    lambda2 = make_cube("Shield_Lambda2", (0.89, 0.40, 1.45), (0.03, 0.02, 0.18), mat_red, "Hand.L")
    lambda2.rotation_euler = (0, math.radians(-25), 0)

    # Greek Xiphos Sword attached to Hand.R
    blade = make_cube("Sword_Blade", (-0.85, 0.45, 1.45), (0.04, 0.38, 0.015), mat_iron, "Hand.R")
    guard = make_cube("Sword_Guard", (-0.85, 0.08, 1.45), (0.10, 0.03, 0.03), mat_bronze, "Hand.R")
    hilt = make_cylinder("Sword_Hilt", (-0.85, -0.02, 1.45), 0.025, 0.14, mat_leather, "Hand.R", rot=(math.radians(90), 0, 0))
    pommel = make_uv_sphere("Sword_Pommel", (-0.85, -0.10, 1.45), 0.04, mat_gold, "Hand.R")

    # Assign exact vertex groups to each part before joining
    for obj, bone_name in parts:
        vg = obj.vertex_groups.new(name=bone_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')

    # Join all mesh parts into a single character mesh
    bpy.ops.object.select_all(action='DESELECT')
    for obj, _ in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0][0]
    bpy.ops.object.join()
    warrior_mesh = bpy.context.active_object
    warrior_mesh.name = "WarriorMesh"

    # Add Armature Modifier and parent
    mod = warrior_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    warrior_mesh.parent = arm_obj

    # 3. Create Skeletal Animations
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = arm_obj.pose.bones
    for pb in pose_bones:
        pb.rotation_mode = 'XYZ'

    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    def reset_pose():
        for pb in pose_bones:
            pb.location = (0, 0, 0)
            pb.rotation_euler = (0, 0, 0)

    # Helper to insert keyframe
    def keyframe_all(frame):
        for pb in pose_bones:
            pb.keyframe_insert(data_path="location", frame=frame)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    actions = []

    # --- ACTION 1: IDLE ---
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset_pose()

    # Shield held forward defensively, sword held forward ready to strike
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(-35), math.radians(20), math.radians(-30))
    pose_bones["Forearm.L"].rotation_euler = (math.radians(-45), math.radians(35), math.radians(40))
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-25), math.radians(-15), math.radians(-40))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-40), math.radians(10), math.radians(30))

    # Frame 1
    keyframe_all(1)
    # Frame 15: slight breath rise
    pose_bones["Chest"].location = (0, 0, 0.03)
    pose_bones["Chest"].rotation_euler = (math.radians(2), 0, 0)
    keyframe_all(15)
    # Frame 30: return to 1
    pose_bones["Chest"].location = (0, 0, 0)
    pose_bones["Chest"].rotation_euler = (0, 0, 0)
    keyframe_all(30)
    actions.append(act_idle)

    # --- ACTION 2: RUN ---
    act_run = bpy.data.actions.new(name="Run")
    arm_obj.animation_data.action = act_run
    reset_pose()

    # Stride 1: Left leg forward, right leg back, torso leans forward
    pose_bones["Hips"].rotation_euler = (math.radians(15), 0, 0)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(-35), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(20), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(35), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(45), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(-40), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(35), 0, 0)
    keyframe_all(1)

    # Passing frame (frame 7)
    pose_bones["Hips"].location = (0, 0, 0.06)
    pose_bones["Thigh.L"].rotation_euler = (0, 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (0, 0, 0)
    keyframe_all(7)

    # Stride 2: Right leg forward, left leg back (frame 14)
    pose_bones["Hips"].location = (0, 0, 0)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(35), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(45), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(-35), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(20), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(30), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-40), 0, 0)
    keyframe_all(14)

    # Passing frame (frame 20)
    pose_bones["Hips"].location = (0, 0, 0.06)
    pose_bones["Thigh.L"].rotation_euler = (0, 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (0, 0, 0)
    keyframe_all(20)

    # Loop back (frame 26)
    pose_bones["Hips"].location = (0, 0, 0)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(-35), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(20), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(35), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(45), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(-40), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(35), 0, 0)
    keyframe_all(26)
    actions.append(act_run)

    # --- ACTION 3: ATTACK 1 (Horizontal Slash) ---
    act_atk1 = bpy.data.actions.new(name="Attack1")
    arm_obj.animation_data.action = act_atk1
    reset_pose()

    # Frame 1: Anticipation / windup
    pose_bones["Spine"].rotation_euler = (0, 0, math.radians(-35))
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(40), math.radians(20), math.radians(50))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-60), 0, math.radians(-20))
    keyframe_all(1)

    # Frame 7: Peak Slash across
    pose_bones["Spine"].rotation_euler = (math.radians(10), 0, math.radians(45))
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-50), math.radians(-30), math.radians(-60))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-10), 0, 0)
    keyframe_all(7)

    # Frame 18: Recovery
    reset_pose()
    keyframe_all(18)
    actions.append(act_atk1)

    # --- ACTION 4: ATTACK 2 (Overhead Cleave) ---
    act_atk2 = bpy.data.actions.new(name="Attack2")
    arm_obj.animation_data.action = act_atk2
    reset_pose()

    # Frame 1: Raise sword high
    pose_bones["Spine"].rotation_euler = (math.radians(-20), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-90), math.radians(20), math.radians(20))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-70), 0, 0)
    keyframe_all(1)

    # Frame 8: Slam downwards
    pose_bones["Spine"].rotation_euler = (math.radians(30), 0, 0)
    pose_bones["Hips"].location = (0, 0, -0.15)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(45), 0, 0)
    pose_bones["Forearm.R"].rotation_euler = (math.radians(10), 0, 0)
    keyframe_all(8)

    # Frame 20: Recovery
    reset_pose()
    keyframe_all(20)
    actions.append(act_atk2)

    # --- ACTION 5: PRAY (Kneeling with Sword Held in Reverence) ---
    act_pray = bpy.data.actions.new(name="Pray")
    arm_obj.animation_data.action = act_pray
    reset_pose()

    # Frame 1: Begin kneeling
    keyframe_all(1)

    # Frame 12: Kneel on right knee, lower shield, raise right arm/sword to heaven
    pose_bones["Hips"].location = (0, 0, -0.42)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(70), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(90), 0, 0)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(-60), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(45), 0, 0)
    pose_bones["Spine"].rotation_euler = (math.radians(-15), 0, 0)
    pose_bones["Head"].rotation_euler = (math.radians(-40), 0, 0)  # Looking up at Olympus

    # Both arms raised in prayer / holding blade upwards
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-75), math.radians(-20), math.radians(10))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-40), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(-40), math.radians(10), math.radians(-10))
    pose_bones["Forearm.L"].rotation_euler = (math.radians(-60), 0, 0)
    keyframe_all(12)

    # Frame 25: Subtle devotional tremor / divine glow
    pose_bones["Head"].rotation_euler = (math.radians(-45), 0, 0)
    keyframe_all(25)

    # Frame 35: Still kneeling in prayer
    keyframe_all(35)
    actions.append(act_pray)

    # --- ACTION 6: DODGE (Combat Roll) ---
    act_dodge = bpy.data.actions.new(name="Dodge")
    arm_obj.animation_data.action = act_dodge
    reset_pose()

    keyframe_all(1)
    # Mid-roll (Frame 8): Tucked into ball, rotating forward
    pose_bones["Hips"].location = (0, 0.4, -0.35)
    pose_bones["Hips"].rotation_euler = (math.radians(160), 0, 0)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(-80), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(100), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(-80), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(100), 0, 0)
    keyframe_all(8)

    # End roll (Frame 16): Landing back on feet
    reset_pose()
    pose_bones["Hips"].location = (0, 0.8, 0)
    keyframe_all(16)
    actions.append(act_dodge)

    # --- ACTION 7: HIT (Damage Flinch) ---
    act_hit = bpy.data.actions.new(name="Hit")
    arm_obj.animation_data.action = act_hit
    reset_pose()

    keyframe_all(1)
    # Frame 4: Head and chest snapped back
    pose_bones["Chest"].rotation_euler = (math.radians(-30), 0, math.radians(15))
    pose_bones["Head"].rotation_euler = (math.radians(-25), 0, math.radians(-10))
    pose_bones["Hips"].location = (0, -0.1, 0)
    keyframe_all(4)

    # Frame 12: Recovery
    reset_pose()
    keyframe_all(12)
    actions.append(act_hit)

    # --- ACTION 8: DEATH ---
    act_death = bpy.data.actions.new(name="Death")
    arm_obj.animation_data.action = act_death
    reset_pose()

    keyframe_all(1)
    # Frame 10: Stagger and collapse to knees
    pose_bones["Hips"].location = (0, -0.1, -0.45)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(60), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(60), 0, 0)
    pose_bones["Spine"].rotation_euler = (math.radians(-20), 0, 0)
    keyframe_all(10)

    # Frame 25: Fall flat onto ground
    pose_bones["Hips"].location = (0, -0.3, -0.85)
    pose_bones["Hips"].rotation_euler = (math.radians(-85), 0, 0)
    pose_bones["Spine"].rotation_euler = (math.radians(10), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(30), 0, math.radians(-70))
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(30), 0, math.radians(70))
    keyframe_all(25)
    actions.append(act_death)

    # Return to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Push all actions onto NLA strips so the GLTF exporter bundles them all
    for act in actions:
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, 1, act)

    # Keep Idle as active action
    arm_obj.animation_data.action = act_idle

    # Export GLTF / GLB
    out_path = "/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/models/warrior.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_animations=True,
        export_nla_strips=True,
        export_def_bones=True
    )
    print(f"SUCCESS: Exported warrior to {out_path} with {len(actions)} animations!")

if __name__ == "__main__":
    create_warrior()
