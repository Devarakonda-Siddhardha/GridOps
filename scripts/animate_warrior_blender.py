"""
Rig and animate sf_player_warrior.glb in Blender 4.2 with 9 combat/movement NLA actions:
Idle, Run, Attack1, Attack2, Block, Dodge, Pray, Hit, Death.
"""
import math
import os
import bpy
from mathutils import Vector, Euler

SRC = os.path.abspath("assets/models/sf_player_warrior.glb")
OUT = os.path.abspath("assets/models/sf_player_warrior.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

# 1. Remove Pedestal, Rain, Background permanently
for obj in list(bpy.data.objects):
    if any(k in obj.name for k in ("Pedestal", "Rain", "Background")):
        bpy.data.objects.remove(obj, do_unlink=True)

# Apply existing transforms to mesh objects so world coords = local coords
bpy.ops.object.select_all(action='DESELECT')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for m in meshes:
    m.select_set(True)
    bpy.context.view_layer.objects.active = m
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 2. Build Armature aligned to Spartan joint samples
arm_data = bpy.data.armatures.new("SpartanArmature")
arm_obj = bpy.data.objects.new("SpartanRig", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

def add_bone(name, head, tail, parent=None, connect=False):
    b = arm_data.edit_bones.new(name)
    b.head = Vector(head)
    b.tail = Vector(tail)
    if parent:
        b.parent = parent
        b.use_connect = connect
    return b

hips = add_bone("Hips", (0.0, 0.35, -0.45), (0.0, 0.25, 0.25))
spine = add_bone("Spine", (0.0, 0.25, 0.25), (0.0, 0.13, 1.05), hips, True)
chest = add_bone("Chest", (0.0, 0.13, 1.05), (0.0, 0.05, 1.95), spine, True)
neck = add_bone("Neck", (0.0, 0.05, 1.95), (0.0, -0.20, 2.55), chest, True)
head = add_bone("Head", (0.0, -0.20, 2.55), (0.0, -0.35, 3.70), neck, True)

# Left arm (+X, shield side)
uarm_l = add_bone("UpperArm.L", (0.80, 0.12, 1.80), (1.28, -0.15, 1.05), chest, False)
farm_l = add_bone("Forearm.L", (1.28, -0.15, 1.05), (1.35, -0.75, 0.55), uarm_l, True)
hand_l = add_bone("Hand.L", (1.35, -0.75, 0.55), (1.38, -1.05, 0.45), farm_l, True)

# Right arm (-X, spear side)
uarm_r = add_bone("UpperArm.R", (-0.90, -0.15, 1.80), (-1.40, -0.40, 1.50), chest, False)
farm_r = add_bone("Forearm.R", (-1.40, -0.40, 1.50), (-1.10, -0.85, 2.20), uarm_r, True)
hand_r = add_bone("Hand.R", (-1.10, -0.85, 2.20), (-0.95, -1.05, 2.55), farm_r, True)

# Left leg (+X, forward)
thigh_l = add_bone("Thigh.L", (0.55, 0.30, -0.50), (1.08, -0.35, -2.45), hips, False)
shin_l = add_bone("Shin.L", (1.08, -0.35, -2.45), (1.48, -0.68, -4.15), thigh_l, True)
foot_l = add_bone("Foot.L", (1.48, -0.68, -4.15), (1.60, -1.35, -4.40), shin_l, True)

# Right leg (-X, back)
thigh_r = add_bone("Thigh.R", (-0.55, 0.40, -0.50), (-1.05, 0.38, -2.45), hips, False)
shin_r = add_bone("Shin.R", (-1.05, 0.38, -2.45), (-1.42, 0.60, -4.15), thigh_r, True)
foot_r = add_bone("Foot.R", (-1.42, 0.60, -4.15), (-1.48, -0.10, -4.40), shin_r, True)

bpy.ops.object.mode_set(mode='OBJECT')

# 3. Bind organic meshes with ARMATURE_AUTO, and rigid accessories to single bones
organic_names = ("Body", "Outfit")
rigid_map = {
    "Eye": "Head",
    "Eyelash": "Head",
    "Sword": "Hips",
    "Shield": "Forearm.L",
    "Spear": "Hand.R",
}

def _assign_nearest_bone_weights(mesh_obj, rig_obj):
    segs = []
    for b in rig_obj.data.bones:
        segs.append((b.name, b.head_local.copy(), b.tail_local.copy()))
    def pt_seg_dist_sq(p, a, b):
        ab = b - a
        l2 = ab.length_squared
        if l2 < 1e-8:
            return (p - a).length_squared
        t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
        proj = a + ab * t
        return (p - proj).length_squared
    vgs = {}
    for name, _, _ in segs:
        vg = mesh_obj.vertex_groups.get(name) or mesh_obj.vertex_groups.new(name=name)
        vgs[name] = vg
    for v in mesh_obj.data.vertices:
        p = v.co
        # Lock entire head + helmet above Z=2.45 to Head bone
        if p.z >= 2.45:
            vgs["Head"].add([v.index], 1.0, 'REPLACE')
            continue
        dists = sorted(((pt_seg_dist_sq(p, a, b), name) for name, a, b in segs), key=lambda x: x[0])
        d0, n0 = dists[0]
        d1, n1 = dists[1]
        w0 = 1.0 / (d0 + 0.04)
        w1 = 1.0 / (d1 + 0.04)
        tot = w0 + w1
        vgs[n0].add([v.index], w0 / tot, 'REPLACE')
        if (w1 / tot) > 0.10:
            vgs[n1].add([v.index], w1 / tot, 'REPLACE')

for m in meshes:
    if any(k in m.name for k in organic_names):
        m.parent = arm_obj
        mod = m.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        _assign_nearest_bone_weights(m, arm_obj)
    else:
        bone_name = "Hips"
        for k, bn in rigid_map.items():
            if k in m.name:
                bone_name = bn
                break
        m.parent = arm_obj
        mod = m.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        vg = m.vertex_groups.new(name=bone_name)
        vg.add([v.index for v in m.data.vertices], 1.0, 'REPLACE')

# Ensure all pose bones use XYZ Euler for clean procedural animation
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
for pb in arm_obj.pose.bones:
    pb.rotation_mode = 'XYZ'

def reset_pose():
    for pb in arm_obj.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)

def key_all(frame):
    for pb in arm_obj.pose.bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

def set_rot(bone_name, rx_deg, ry_deg, rz_deg):
    pb = arm_obj.pose.bones[bone_name]
    pb.rotation_euler = (math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg))

def set_loc(bone_name, x, y, z):
    arm_obj.pose.bones[bone_name].location = (x, y, z)

def make_action(name, total_frames, build_fn):
    act = bpy.data.actions.new(name=name)
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act
    reset_pose()
    build_fn(total_frames)
    # Smooth interpolation
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
    # Push to NLA track so glTF exports every action cleanly
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 0, act)
    strip.action_frame_start = 0
    strip.action_frame_end = total_frames
    arm_obj.animation_data.action = None

# --- ACTION DEFINITIONS ---

def anim_idle(N):
    for f, s in [(0, 0.0), (16, 1.0), (32, -0.5), (48, 0.0)]:
        reset_pose()
        set_loc("Hips", 0, 0, 0.05 * s)
        set_rot("Chest", 3.0 * s, 0, 2.0 * s)
        set_rot("Head", -2.0 * s, 0, -2.0 * s)
        set_rot("UpperArm.L", 4.0 * s, 0, 3.0 * s)
        set_rot("UpperArm.R", -4.0 * s, 0, -3.0 * s)
        key_all(f)

def anim_run(N):
    # 24-frame full stride cycle
    keys = [
        (0,  0.0,  0.0),
        (6,  1.0,  0.12),
        (12, 0.0,  0.0),
        (18, -1.0, 0.12),
        (24, 0.0,  0.0),
    ]
    for f, p, bob in keys:
        reset_pose()
        set_loc("Hips", 0, 0, -0.15 + bob)
        set_rot("Spine", 12, 0, -6 * p)
        set_rot("Chest", 8, 0, -8 * p)
        set_rot("Head", -12, 0, 4 * p)
        # Legs alternate
        set_rot("Thigh.L", 32 * p, 0, 0)
        set_rot("Shin.L", -28 * max(0, -p) - 10, 0, 0)
        set_rot("Thigh.R", -32 * p, 0, 0)
        set_rot("Shin.R", -28 * max(0, p) - 10, 0, 0)
        # Arms counter-swing (keep shield forward)
        set_rot("UpperArm.L", -16 * p + 12, 0, 10)
        set_rot("Forearm.L", 18, 0, 0)
        set_rot("UpperArm.R", 26 * p, 0, -8)
        set_rot("Forearm.R", 14, 0, 0)
        key_all(f)

def anim_attack1(N):
    # Fast spear thrust & slash
    reset_pose()
    key_all(0)
    # Wind-up
    reset_pose()
    set_rot("Spine", -5, 0, 22)
    set_rot("Chest", -5, 0, 25)
    set_rot("UpperArm.R", -35, 10, 25)
    set_rot("Forearm.R", 25, 0, 0)
    set_rot("UpperArm.L", 15, 0, -15)
    key_all(6)
    # Strike forward
    reset_pose()
    set_loc("Hips", 0, -0.25, -0.10)
    set_rot("Spine", 18, 0, -28)
    set_rot("Chest", 14, 0, -32)
    set_rot("Thigh.L", 18, 0, 0)
    set_rot("Thigh.R", -18, 0, 0)
    set_rot("UpperArm.R", 55, -15, -20)
    set_rot("Forearm.R", -35, 0, 0)
    set_rot("UpperArm.L", -10, 0, 25)
    key_all(12)
    # Recover
    reset_pose()
    key_all(20)

def anim_attack2(N):
    # Heavy overhead cleave
    reset_pose()
    key_all(0)
    # Raise high
    reset_pose()
    set_loc("Hips", 0, 0.10, 0.15)
    set_rot("Spine", -14, 0, 15)
    set_rot("Chest", -14, 0, 15)
    set_rot("UpperArm.R", 95, 0, 15)
    set_rot("Forearm.R", -20, 0, 0)
    set_rot("UpperArm.L", 25, 0, 15)
    key_all(8)
    # Slam down
    reset_pose()
    set_loc("Hips", 0, -0.30, -0.25)
    set_rot("Spine", 28, 0, -24)
    set_rot("Chest", 22, 0, -24)
    set_rot("Thigh.L", 22, 0, 0)
    set_rot("Shin.L", -20, 0, 0)
    set_rot("UpperArm.R", -40, 0, -30)
    set_rot("Forearm.R", -15, 0, 0)
    set_rot("UpperArm.L", -15, 0, 30)
    key_all(15)
    reset_pose()
    key_all(24)

def anim_block(N):
    # Guard stance with shield raised across chest
    for f, breath in [(0, 0.0), (8, 1.0), (16, 0.0)]:
        reset_pose()
        set_loc("Hips", 0, 0.10, -0.25 + 0.02 * breath)
        set_rot("Spine", 8, 0, 14)
        set_rot("Chest", 6, 0, 16)
        set_rot("Head", -10, 0, -22)
        set_rot("Thigh.L", 16, 0, 0)
        set_rot("Shin.L", -18, 0, 0)
        set_rot("Thigh.R", -14, 0, 0)
        set_rot("Shin.R", -14, 0, 0)
        # Raise left shield arm across front
        set_rot("UpperArm.L", 42, -25, -45)
        set_rot("Forearm.L", 35, 0, -25)
        # Brace spear back
        set_rot("UpperArm.R", -18, 0, 15)
        key_all(f)

def anim_dodge(N):
    reset_pose()
    key_all(0)
    # Crouch tuck mid-dash
    reset_pose()
    set_loc("Hips", 0, -0.35, -0.95)
    set_rot("Spine", 38, 0, 0)
    set_rot("Chest", 28, 0, 0)
    set_rot("Head", -35, 0, 0)
    set_rot("Thigh.L", 55, 0, 0)
    set_rot("Shin.L", -65, 0, 0)
    set_rot("Thigh.R", 45, 0, 0)
    set_rot("Shin.R", -55, 0, 0)
    set_rot("UpperArm.L", 25, 0, -25)
    set_rot("UpperArm.R", -25, 0, 15)
    key_all(9)
    reset_pose()
    key_all(18)

def anim_pray(N):
    for f, s in [(0, 0.0), (18, 1.0), (36, 0.0)]:
        reset_pose()
        set_loc("Hips", 0, 0, -0.85)
        set_rot("Spine", 18 + 3 * s, 0, 0)
        set_rot("Chest", 12 + 3 * s, 0, 0)
        set_rot("Head", 22, 0, 0)
        set_rot("Thigh.L", 45, 0, 0)
        set_rot("Shin.L", -85, 0, 0)
        set_rot("Thigh.R", 20, 0, 0)
        set_rot("Shin.R", -65, 0, 0)
        set_rot("UpperArm.R", 70 + 5 * s, 0, 10)
        set_rot("UpperArm.L", 30, 0, -20)
        key_all(f)

def anim_hit(N):
    reset_pose()
    key_all(0)
    reset_pose()
    set_loc("Hips", 0, 0.25, -0.10)
    set_rot("Spine", -22, 0, -12)
    set_rot("Chest", -18, 0, -10)
    set_rot("Head", -20, 0, 10)
    set_rot("UpperArm.L", -15, 0, 20)
    set_rot("UpperArm.R", -20, 0, -20)
    key_all(5)
    reset_pose()
    key_all(14)

def anim_death(N):
    reset_pose()
    key_all(0)
    # Fall to knees
    reset_pose()
    set_loc("Hips", 0, 0.15, -0.95)
    set_rot("Spine", 20, 0, 0)
    set_rot("Thigh.L", 50, 0, 0)
    set_rot("Shin.L", -85, 0, 0)
    set_rot("Thigh.R", 40, 0, 0)
    set_rot("Shin.R", -80, 0, 0)
    key_all(10)
    # Collapse to ground
    reset_pose()
    set_loc("Hips", 0, -0.45, -3.45)
    set_rot("Hips", 82, 0, 12)
    set_rot("Spine", 15, 0, 0)
    set_rot("Head", -15, 0, 0)
    set_rot("UpperArm.L", 20, 0, 35)
    set_rot("UpperArm.R", 30, 0, -35)
    set_rot("Thigh.L", -10, 0, 10)
    set_rot("Thigh.R", -10, 0, -10)
    key_all(28)

make_action("Idle", 48, anim_idle)
make_action("Run", 24, anim_run)
make_action("Attack1", 20, anim_attack1)
make_action("Attack2", 24, anim_attack2)
make_action("Block", 16, anim_block)
make_action("Dodge", 18, anim_dodge)
make_action("Pray", 36, anim_pray)
make_action("Hit", 14, anim_hit)
make_action("Death", 28, anim_death)

bpy.ops.object.mode_set(mode='OBJECT')

# 4. Export as glTF Binary (.glb) with NLA animations
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format='GLB',
    export_animations=True,
    export_nla_strips=True,
    export_nla_strips_merged_animation_name="",
    export_skins=True,
    export_apply=False,
)
print("EXPORTED RIGGED & ANIMATED WARRIOR:", OUT, os.path.getsize(OUT))
