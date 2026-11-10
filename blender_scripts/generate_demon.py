"""
Blender script to generate a fully rigged and animated Underworld Tartarus Demon.
Exports demon.glb with embedded mesh, materials, armature, and animations:
- Idle
- Walk
- Attack
- Hit
- Death
"""

import bpy
import math

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
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 2.5
    return mat

def create_demon():
    clear_scene()

    mat_skin = create_material("DemonSkin", (0.04, 0.03, 0.05, 1.0), metallic=0.3, roughness=0.35)
    mat_lava = create_material("DemonLava", (1.0, 0.18, 0.02, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.2, 0.02, 1.0))
    mat_horn = create_material("DemonHorn", (0.15, 0.12, 0.10, 1.0), metallic=0.5, roughness=0.3)
    mat_eye = create_material("DemonEye", (1.0, 0.0, 0.0, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.0, 0.0, 1.0))
    mat_blade = create_material("DemonBlade", (0.05, 0.05, 0.06, 1.0), metallic=0.95, roughness=0.2)

    # 1. Armature
    arm_data = bpy.data.armatures.new("DemonArmatureData")
    arm_obj = bpy.data.objects.new("DemonArmature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = arm_data.edit_bones

    root = edit_bones.new("Root")
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.2)

    hips = edit_bones.new("Hips")
    hips.parent = root
    hips.head = (0, 0, 1.05)
    hips.tail = (0, 0, 1.25)

    spine = edit_bones.new("Spine")
    spine.parent = hips
    spine.head = (0, 0, 1.25)
    spine.tail = (0, 0, 1.5)

    chest = edit_bones.new("Chest")
    chest.parent = spine
    chest.head = (0, 0, 1.5)
    chest.tail = (0, 0, 1.8)

    neck = edit_bones.new("Neck")
    neck.parent = chest
    neck.head = (0, 0, 1.8)
    neck.tail = (0, 0, 1.92)

    head = edit_bones.new("Head")
    head.parent = neck
    head.head = (0, 0, 1.92)
    head.tail = (0, 0, 2.3)

    # Left Arm
    uarm_l = edit_bones.new("UpperArm.L")
    uarm_l.parent = chest
    uarm_l.head = (0.32, 0, 1.72)
    uarm_l.tail = (0.68, 0, 1.62)

    farm_l = edit_bones.new("Forearm.L")
    farm_l.parent = uarm_l
    farm_l.head = (0.68, 0, 1.62)
    farm_l.tail = (1.02, 0.15, 1.5)

    hand_l = edit_bones.new("Hand.L")
    hand_l.parent = farm_l
    hand_l.head = (1.02, 0.15, 1.5)
    hand_l.tail = (1.18, 0.2, 1.45)

    # Right Arm (Weapon)
    uarm_r = edit_bones.new("UpperArm.R")
    uarm_r.parent = chest
    uarm_r.head = (-0.32, 0, 1.72)
    uarm_r.tail = (-0.68, 0, 1.62)

    farm_r = edit_bones.new("Forearm.R")
    farm_r.parent = uarm_r
    farm_r.head = (-0.68, 0, 1.62)
    farm_r.tail = (-1.02, 0.15, 1.5)

    hand_r = edit_bones.new("Hand.R")
    hand_r.parent = farm_r
    hand_r.head = (-1.02, 0.15, 1.5)
    hand_r.tail = (-1.18, 0.2, 1.45)

    # Left Leg
    thigh_l = edit_bones.new("Thigh.L")
    thigh_l.parent = hips
    thigh_l.head = (0.22, 0, 1.05)
    thigh_l.tail = (0.22, 0, 0.55)

    shin_l = edit_bones.new("Shin.L")
    shin_l.parent = thigh_l
    shin_l.head = (0.22, 0, 0.55)
    shin_l.tail = (0.22, 0, 0.12)

    foot_l = edit_bones.new("Foot.L")
    foot_l.parent = shin_l
    foot_l.head = (0.22, 0, 0.12)
    foot_l.tail = (0.22, 0.25, 0)

    # Right Leg
    thigh_r = edit_bones.new("Thigh.R")
    thigh_r.parent = hips
    thigh_r.head = (-0.22, 0, 1.05)
    thigh_r.tail = (-0.22, 0, 0.55)

    shin_r = edit_bones.new("Shin.R")
    shin_r.parent = thigh_r
    shin_r.head = (-0.22, 0, 0.55)
    shin_r.tail = (-0.22, 0, 0.12)

    foot_r = edit_bones.new("Foot.R")
    foot_r.parent = shin_r
    foot_r.head = (-0.22, 0, 0.12)
    foot_r.tail = (-0.22, 0.25, 0)

    bpy.ops.object.mode_set(mode='OBJECT')

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

    def make_cone(name, loc, r1, depth, mat, bone_name, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cone_add(radius1=r1, depth=depth, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        obj.data.materials.append(mat)
        parts.append((obj, bone_name))
        return obj

    # Torso (Hulking muscular demon)
    make_cube("Demon_Chest", (0, 0, 1.65), (0.30, 0.20, 0.20), mat_skin, "Chest")
    make_cube("Chest_LavaCore", (0, 0.18, 1.65), (0.16, 0.05, 0.14), mat_lava, "Chest")
    make_cube("Demon_Spine", (0, 0, 1.38), (0.24, 0.16, 0.15), mat_skin, "Spine")
    make_cube("Demon_Hips", (0, 0, 1.15), (0.26, 0.18, 0.14), mat_skin, "Hips")

    # Spine Spikes
    for i, z in enumerate([1.35, 1.5, 1.65, 1.8]):
        make_cone(f"Spike_{i}", (0, -0.22, z), 0.04, 0.18, mat_horn, "Spine", rot=(math.radians(-60), 0, 0))

    # Demonic Skull & Curved Horns
    make_cube("Demon_Head", (0, 0.05, 2.05), (0.18, 0.18, 0.16), mat_skin, "Head")
    make_cube("Demon_Jaw", (0, 0.15, 1.95), (0.14, 0.12, 0.08), mat_skin, "Head")
    # Eyes (glowing crimson)
    make_cube("Eye_L", (0.08, 0.22, 2.08), (0.04, 0.02, 0.025), mat_eye, "Head")
    make_cube("Eye_R", (-0.08, 0.22, 2.08), (0.04, 0.02, 0.025), mat_eye, "Head")

    # Curved Horns
    horn_l1 = make_cone("Horn_L1", (0.18, 0.02, 2.22), 0.07, 0.28, mat_horn, "Head", rot=(math.radians(25), math.radians(35), 0))
    horn_r1 = make_cone("Horn_R1", (-0.18, 0.02, 2.22), 0.07, 0.28, mat_horn, "Head", rot=(math.radians(25), math.radians(-35), 0))

    # Arms (Claws & Muscular)
    make_cylinder("Shoulder_L", (0.36, 0, 1.72), 0.11, 0.24, mat_skin, "UpperArm.L", rot=(0, math.radians(90), 0))
    make_cylinder("UpperArm_L", (0.52, 0, 1.68), 0.09, 0.30, mat_skin, "UpperArm.L", rot=(0, math.radians(90), 0))
    make_cylinder("Forearm_L", (0.84, 0.06, 1.56), 0.085, 0.32, mat_skin, "Forearm.L", rot=(0, math.radians(80), 0))
    make_cube("Claws_L", (1.10, 0.14, 1.48), (0.08, 0.12, 0.06), mat_horn, "Hand.L")

    make_cylinder("Shoulder_R", (-0.36, 0, 1.72), 0.11, 0.24, mat_skin, "UpperArm.R", rot=(0, math.radians(-90), 0))
    make_cylinder("UpperArm_R", (-0.52, 0, 1.68), 0.09, 0.30, mat_skin, "UpperArm.R", rot=(0, math.radians(-90), 0))
    make_cylinder("Forearm_R", (-0.84, 0.06, 1.56), 0.085, 0.32, mat_skin, "Forearm.R", rot=(0, math.radians(-80), 0))
    make_cube("Claws_R", (-1.10, 0.14, 1.48), (0.08, 0.12, 0.06), mat_horn, "Hand.R")

    # Demonic Jagged Greatsword in Hand.R
    make_cube("Demon_Blade", (-1.15, 0.55, 1.48), (0.07, 0.55, 0.02), mat_blade, "Hand.R")
    make_cube("Blade_LavaEdge", (-1.15, 0.55, 1.48), (0.02, 0.52, 0.025), mat_lava, "Hand.R")
    make_cube("Demon_Crossguard", (-1.15, 0.08, 1.48), (0.16, 0.04, 0.04), mat_horn, "Hand.R")
    make_cylinder("Demon_Hilt", (-1.15, -0.05, 1.48), 0.035, 0.22, mat_skin, "Hand.R", rot=(math.radians(90), 0, 0))

    # Legs
    make_cylinder("Thigh_L", (0.22, 0, 0.80), 0.12, 0.45, mat_skin, "Thigh.L")
    make_cylinder("Shin_L", (0.22, 0, 0.35), 0.10, 0.42, mat_skin, "Shin.L")
    make_cube("Foot_L", (0.22, 0.10, 0.06), (0.10, 0.18, 0.08), mat_horn, "Foot.L")

    make_cylinder("Thigh_R", (-0.22, 0, 0.80), 0.12, 0.45, mat_skin, "Thigh.R")
    make_cylinder("Shin_R", (-0.22, 0, 0.35), 0.10, 0.42, mat_skin, "Shin.R")
    make_cube("Foot_R", (-0.22, 0.10, 0.06), (0.10, 0.18, 0.08), mat_horn, "Foot.R")

    # Vertex groups assignment
    for obj, bone_name in parts:
        vg = obj.vertex_groups.new(name=bone_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')

    bpy.ops.object.select_all(action='DESELECT')
    for obj, _ in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0][0]
    bpy.ops.object.join()
    demon_mesh = bpy.context.active_object
    demon_mesh.name = "DemonMesh"

    mod = demon_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    demon_mesh.parent = arm_obj

    # 3. Create Demon Animations
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

    def keyframe_all(frame):
        for pb in pose_bones:
            pb.keyframe_insert(data_path="location", frame=frame)
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    actions = []

    # --- ACTION 1: IDLE ---
    act_idle = bpy.data.actions.new(name="Idle")
    arm_obj.animation_data.action = act_idle
    reset_pose()

    # Menacing hunch
    pose_bones["Spine"].rotation_euler = (math.radians(15), 0, 0)
    pose_bones["Chest"].rotation_euler = (math.radians(10), 0, 0)
    pose_bones["Head"].rotation_euler = (math.radians(-20), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(20), 0, math.radians(25))
    pose_bones["Forearm.L"].rotation_euler = (math.radians(-40), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(20), 0, math.radians(-20))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-35), 0, 0)
    keyframe_all(1)

    pose_bones["Chest"].location = (0, 0, 0.04)
    pose_bones["Chest"].rotation_euler = (math.radians(15), 0, 0)
    keyframe_all(15)

    pose_bones["Chest"].location = (0, 0, 0)
    pose_bones["Chest"].rotation_euler = (math.radians(10), 0, 0)
    keyframe_all(30)
    actions.append(act_idle)

    # --- ACTION 2: WALK ---
    act_walk = bpy.data.actions.new(name="Walk")
    arm_obj.animation_data.action = act_walk
    reset_pose()

    pose_bones["Spine"].rotation_euler = (math.radians(15), 0, 0)
    # Stride 1 (frame 1)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(-30), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(25), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(30), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(35), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(-30), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(30), 0, 0)
    keyframe_all(1)

    # Stride 2 (frame 14)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(30), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(35), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(-30), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(25), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(30), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-30), 0, 0)
    keyframe_all(14)

    # Loop back (frame 28)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(-30), 0, 0)
    pose_bones["Shin.L"].rotation_euler = (math.radians(25), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(30), 0, 0)
    pose_bones["Shin.R"].rotation_euler = (math.radians(35), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (math.radians(-30), 0, 0)
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(30), 0, 0)
    keyframe_all(28)
    actions.append(act_walk)

    # --- ACTION 3: ATTACK ---
    act_atk = bpy.data.actions.new(name="Attack")
    arm_obj.animation_data.action = act_atk
    reset_pose()

    # Wind up (frame 1)
    pose_bones["Spine"].rotation_euler = (math.radians(-10), 0, math.radians(-30))
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(-70), math.radians(20), math.radians(30))
    pose_bones["Forearm.R"].rotation_euler = (math.radians(-80), 0, 0)
    keyframe_all(1)

    # Heavy Slam (frame 9)
    pose_bones["Spine"].rotation_euler = (math.radians(35), 0, math.radians(30))
    pose_bones["UpperArm.R"].rotation_euler = (math.radians(60), 0, 0)
    pose_bones["Forearm.R"].rotation_euler = (math.radians(20), 0, 0)
    pose_bones["Hips"].location = (0, 0.15, -0.15)
    keyframe_all(9)

    # Recover (frame 22)
    reset_pose()
    keyframe_all(22)
    actions.append(act_atk)

    # --- ACTION 4: HIT ---
    act_hit = bpy.data.actions.new(name="Hit")
    arm_obj.animation_data.action = act_hit
    reset_pose()

    keyframe_all(1)
    pose_bones["Chest"].rotation_euler = (math.radians(-30), 0, math.radians(-15))
    pose_bones["Hips"].location = (0, -0.15, 0)
    keyframe_all(4)
    reset_pose()
    keyframe_all(12)
    actions.append(act_hit)

    # --- ACTION 5: DEATH ---
    act_death = bpy.data.actions.new(name="Death")
    arm_obj.animation_data.action = act_death
    reset_pose()

    keyframe_all(1)
    pose_bones["Hips"].location = (0, -0.2, -0.5)
    pose_bones["Thigh.L"].rotation_euler = (math.radians(50), 0, 0)
    pose_bones["Thigh.R"].rotation_euler = (math.radians(50), 0, 0)
    keyframe_all(8)

    pose_bones["Hips"].location = (0, -0.5, -0.95)
    pose_bones["Hips"].rotation_euler = (math.radians(-85), 0, 0)
    pose_bones["UpperArm.L"].rotation_euler = (0, 0, math.radians(-60))
    pose_bones["UpperArm.R"].rotation_euler = (0, 0, math.radians(60))
    keyframe_all(24)
    actions.append(act_death)

    bpy.ops.object.mode_set(mode='OBJECT')

    for act in actions:
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, 1, act)

    arm_obj.animation_data.action = act_idle

    out_path = "/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/models/demon.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_animations=True,
        export_nla_strips=True,
        export_def_bones=True
    )
    print(f"SUCCESS: Exported demon to {out_path} with {len(actions)} animations!")

if __name__ == "__main__":
    create_demon()
