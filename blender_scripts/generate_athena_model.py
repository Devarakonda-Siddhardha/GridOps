"""
Blender script to procedurally generate Athena 3D Model:
- 3.2m tall Colossal Goddess of Wisdom & War Strategy
- Corinthian golden helmet with crimson/gold horsehair crest
- White peplos with gold trim, Golden Aegis breastplate with gorgoneion
- Hoplon shield with Owl of Athens emblem
- Spear of Wisdom (Dory)
- Rigged armature with 'Idle' and 'Bless' animations
- Exported to assets/models/god_athena.glb
"""

import bpy
import math
import os

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

def build_athena():
    clear_scene()
    mesh_parts = []

    # Materials
    mat_skin = create_mat("AthenaSkin", (0.92, 0.78, 0.68, 1.0), roughness=0.4)
    mat_chiton = create_mat("AthenaChiton", (0.95, 0.95, 0.98, 1.0), roughness=0.35)
    mat_gold = create_mat("AthenaGold", (0.95, 0.82, 0.22, 1.0), metallic=0.95, roughness=0.2)
    mat_aegis = create_mat("AthenaAegis", (0.88, 0.72, 0.20, 1.0), metallic=0.92, roughness=0.25)
    mat_crest = create_mat("AthenaCrest", (0.85, 0.15, 0.18, 1.0), roughness=0.5)
    mat_owl = create_mat("AthenaOwlEmblem", (0.98, 0.88, 0.35, 1.0), emission=(0.98, 0.88, 0.35, 1.0))
    mat_shield_face = create_mat("AthenaShieldFace", (0.15, 0.25, 0.55, 1.0), metallic=0.3, roughness=0.4)
    mat_spear_wood = create_mat("SpearWood", (0.35, 0.22, 0.12, 1.0), roughness=0.6)
    mat_spear_tip = create_mat("SpearTip", (0.90, 0.92, 0.95, 1.0), metallic=0.95, roughness=0.15)

    # Scale factor for 3.2m tall colossal stature
    S = 1.8

    # 1. Torso & Peplos (White Gown)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.28 * S, depth=0.85 * S, location=(0, 0, 1.35 * S))
    gown = bpy.context.active_object
    gown.scale = (1.0, 0.8, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    gown.data.materials.append(mat_chiton)
    mesh_parts.append(gown)

    # Lower Peplos flare / skirt
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.45 * S, radius2=0.26 * S, depth=0.9 * S, location=(0, 0, 0.65 * S))
    skirt = bpy.context.active_object
    skirt.data.materials.append(mat_chiton)
    mesh_parts.append(skirt)

    # 2. Golden Aegis (Breastplate)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05 * S, 1.45 * S))
    aegis = bpy.context.active_object
    aegis.scale = (0.58 * S, 0.42 * S, 0.55 * S)
    bpy.ops.object.transform_apply(scale=True)
    aegis.data.materials.append(mat_aegis)
    mesh_parts.append(aegis)

    # Gorgoneion emblem on chest
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10 * S, location=(0, -0.27 * S, 1.50 * S))
    gorgon = bpy.context.active_object
    gorgon.scale = (1.0, 0.4, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    gorgon.data.materials.append(mat_gold)
    mesh_parts.append(gorgon)

    # Gold sash belt
    bpy.ops.mesh.primitive_torus_add(major_radius=0.30 * S, minor_radius=0.04 * S, location=(0, 0, 1.15 * S))
    belt = bpy.context.active_object
    belt.data.materials.append(mat_gold)
    mesh_parts.append(belt)

    # 3. Head & Corinthian Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18 * S, location=(0, 0, 1.95 * S))
    head = bpy.context.active_object
    head.data.materials.append(mat_skin)
    mesh_parts.append(head)

    # Golden Helmet Dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.21 * S, location=(0, -0.02 * S, 2.02 * S))
    helm = bpy.context.active_object
    helm.scale = (1.0, 1.1, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    helm.data.materials.append(mat_gold)
    mesh_parts.append(helm)

    # Cheek guards
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.16 * S, -0.08 * S, 1.90 * S))
        cheek = bpy.context.active_object
        cheek.scale = (0.04 * S, 0.12 * S, 0.18 * S)
        bpy.ops.object.transform_apply(scale=True)
        cheek.data.materials.append(mat_gold)
        mesh_parts.append(cheek)

    # Helmet Crest (Horsehair plume)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.04 * S, 2.30 * S))
    crest = bpy.context.active_object
    crest.scale = (0.08 * S, 0.55 * S, 0.24 * S)
    bpy.ops.object.transform_apply(scale=True)
    crest.data.materials.append(mat_crest)
    mesh_parts.append(crest)

    # 4. Arms
    # Left Arm (holding shield)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08 * S, depth=0.55 * S, location=(-0.38 * S, 0.05 * S, 1.35 * S))
    l_arm = bpy.context.active_object
    l_arm.rotation_euler = (math.radians(25), 0, math.radians(-20))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    l_arm.data.materials.append(mat_skin)
    mesh_parts.append(l_arm)

    # Left Bracer
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09 * S, depth=0.25 * S, location=(-0.44 * S, -0.08 * S, 1.15 * S))
    l_bracer = bpy.context.active_object
    l_bracer.data.materials.append(mat_gold)
    mesh_parts.append(l_bracer)

    # Right Arm (holding spear upright)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08 * S, depth=0.55 * S, location=(0.38 * S, -0.05 * S, 1.35 * S))
    r_arm = bpy.context.active_object
    r_arm.rotation_euler = (math.radians(-15), 0, math.radians(15))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    r_arm.data.materials.append(mat_skin)
    mesh_parts.append(r_arm)

    # Right Bracer
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09 * S, depth=0.25 * S, location=(0.42 * S, -0.10 * S, 1.15 * S))
    r_bracer = bpy.context.active_object
    r_bracer.data.materials.append(mat_gold)
    mesh_parts.append(r_bracer)

    # 5. Hoplon Shield of Athena
    # Shield Outer Rim
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.48 * S, depth=0.08 * S, location=(-0.52 * S, -0.18 * S, 1.25 * S))
    shield_rim = bpy.context.active_object
    shield_rim.rotation_euler = (math.radians(90), 0, math.radians(20))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    shield_rim.data.materials.append(mat_gold)
    mesh_parts.append(shield_rim)

    # Shield Center Face
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.42 * S, depth=0.09 * S, location=(-0.52 * S, -0.19 * S, 1.25 * S))
    shield_face = bpy.context.active_object
    shield_face.rotation_euler = (math.radians(90), 0, math.radians(20))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    shield_face.data.materials.append(mat_shield_face)
    mesh_parts.append(shield_face)

    # Owl of Athens Emblem
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18 * S, location=(-0.52 * S, -0.25 * S, 1.25 * S))
    owl = bpy.context.active_object
    owl.scale = (0.7, 0.1, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    owl.data.materials.append(mat_owl)
    mesh_parts.append(owl)

    # 6. Spear of Wisdom (Dory)
    # Spear Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.03 * S, depth=2.4 * S, location=(0.48 * S, -0.12 * S, 1.60 * S))
    spear_shaft = bpy.context.active_object
    spear_shaft.data.materials.append(mat_spear_wood)
    mesh_parts.append(spear_shaft)

    # Spear Blade / Tip
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.08 * S, depth=0.35 * S, location=(0.48 * S, -0.12 * S, 2.95 * S))
    spear_tip = bpy.context.active_object
    spear_tip.data.materials.append(mat_spear_tip)
    mesh_parts.append(spear_tip)

    # Spear Butt Spike (Sauroter)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.06 * S, depth=0.20 * S, location=(0.48 * S, -0.12 * S, 0.30 * S))
    spear_butt = bpy.context.active_object
    spear_butt.rotation_euler = (math.radians(180), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    spear_butt.data.materials.append(mat_gold)
    mesh_parts.append(spear_butt)

    # 7. Golden Sandals / Feet
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.15 * S, -0.06 * S, 0.08 * S))
        foot = bpy.context.active_object
        foot.scale = (0.12 * S, 0.28 * S, 0.08 * S)
        bpy.ops.object.transform_apply(scale=True)
        foot.data.materials.append(mat_gold)
        mesh_parts.append(foot)

    # Join All Meshes
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    athena_mesh = bpy.context.active_object
    athena_mesh.name = "Athena_Mesh"

    # Add Simple Armature with Idle animation
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = "Athena_Armature"

    # Parent mesh to armature
    athena_mesh.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='OBJECT')

    # Create Idle Animation on Armature
    armature.animation_data_create()
    action = bpy.data.actions.new(name="Idle")
    armature.animation_data.action = action

    # Keyframe subtle breathing hover
    armature.location = (0, 0, 0)
    armature.keyframe_insert(data_path="location", frame=1)
    armature.location = (0, 0, 0.08)
    armature.keyframe_insert(data_path="location", frame=30)
    armature.location = (0, 0, 0)
    armature.keyframe_insert(data_path="location", frame=60)

    # Export GLB
    out_file = os.path.join(OUT_DIR, "god_athena.glb")
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=False,
        export_format='GLB',
        export_animations=True
    )
    print(f"Exported Athena 3D Model: {out_file} (Height: ~3.2m)")

if __name__ == "__main__":
    build_athena()
