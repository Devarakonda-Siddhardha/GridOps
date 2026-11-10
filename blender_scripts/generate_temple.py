"""
Blender script to generate Greek Temple architecture and Altar assets:
- temple_column.glb
- altar_zeus.glb
- altar_poseidon.glb
- altar_hades.glb
- altar_ares.glb
- temple_brazier.glb
"""

import bpy
import math

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_material(name, base_color, metallic=0.1, roughness=0.5, emission=None):
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
                bsdf.inputs["Emission Strength"].default_value = 3.0
    return mat

def export_object(out_path):
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB'
    )
    print(f"Exported: {out_path}")

def build_column():
    clear_scene()
    mat_marble = create_material("WhiteMarble", (0.92, 0.90, 0.88, 1.0), metallic=0.1, roughness=0.35)
    mat_gold = create_material("GoldAccent", (0.95, 0.78, 0.20, 1.0), metallic=0.9, roughness=0.25)

    # Base
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.2), scale=(0.9, 0.9, 0.2))
    b1 = bpy.context.active_object
    b1.data.materials.append(mat_marble)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.3, location=(0, 0, 0.55))
    b2 = bpy.context.active_object
    b2.data.materials.append(mat_gold)

    # Fluted Shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.6, depth=4.2, location=(0, 0, 2.8))
    shaft = bpy.context.active_object
    shaft.data.materials.append(mat_marble)

    # Capital
    bpy.ops.mesh.primitive_cylinder_add(radius=0.78, depth=0.35, location=(0, 0, 5.05))
    c1 = bpy.context.active_object
    c1.data.materials.append(mat_gold)

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 5.4), scale=(0.95, 0.95, 0.2))
    c2 = bpy.context.active_object
    c2.data.materials.append(mat_marble)

    # Join
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    export_object("/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/models/temple_column.glb")

def build_altar(god_name, base_col, rune_col, sigil_type):
    clear_scene()
    mat_base = create_material(f"AltarBase_{god_name}", base_col, metallic=0.3, roughness=0.4)
    mat_gold = create_material("GoldRims", (0.95, 0.75, 0.18, 1.0), metallic=0.9, roughness=0.2)
    mat_rune = create_material(f"RuneGlow_{god_name}", rune_col, metallic=0.0, roughness=0.1, emission=rune_col)

    # Steps / Plinth
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.15), scale=(1.2, 1.2, 0.15))
    p1 = bpy.context.active_object
    p1.data.materials.append(mat_base)

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.4), scale=(0.95, 0.95, 0.15))
    p2 = bpy.context.active_object
    p2.data.materials.append(mat_gold)

    # Main Altar Block
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1.1), scale=(0.8, 0.8, 0.6))
    block = bpy.context.active_object
    block.data.materials.append(mat_base)

    # Altar Slab
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1.75), scale=(0.92, 0.92, 0.08))
    slab = bpy.context.active_object
    slab.data.materials.append(mat_gold)

    # Central Sacred Brazier Bowl
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.18, location=(0, 0, 1.9))
    bowl = bpy.context.active_object
    bowl.data.materials.append(mat_gold)

    # Sacred Divine Flame Core (Sphere with high emission)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(0, 0, 2.15))
    flame = bpy.context.active_object
    flame.data.materials.append(mat_rune)

    # Sigils on Front Face
    if sigil_type == "lightning": # Zeus
        bpy.ops.mesh.primitive_cube_add(location=(0, 0.81, 1.15), scale=(0.04, 0.02, 0.35))
        s1 = bpy.context.active_object
        s1.rotation_euler = (0, math.radians(20), 0)
        s1.data.materials.append(mat_rune)
    elif sigil_type == "trident": # Poseidon
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.6, location=(0, 0.81, 1.15))
        s1 = bpy.context.active_object
        s1.data.materials.append(mat_rune)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.35, location=(0.12, 0.81, 1.25))
        s2 = bpy.context.active_object
        s2.data.materials.append(mat_rune)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.35, location=(-0.12, 0.81, 1.25))
        s3 = bpy.context.active_object
        s3.data.materials.append(mat_rune)
    elif sigil_type == "hades": # Hades (Bident/Skull)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.81, 1.15))
        s1 = bpy.context.active_object
        s1.data.materials.append(mat_rune)
    elif sigil_type == "ares": # Ares (Crossed Swords)
        bpy.ops.mesh.primitive_cube_add(location=(0, 0.81, 1.15), scale=(0.04, 0.02, 0.32))
        s1 = bpy.context.active_object
        s1.rotation_euler = (0, math.radians(45), 0)
        s1.data.materials.append(mat_rune)
        bpy.ops.mesh.primitive_cube_add(location=(0, 0.81, 1.15), scale=(0.04, 0.02, 0.32))
        s2 = bpy.context.active_object
        s2.rotation_euler = (0, math.radians(-45), 0)
        s2.data.materials.append(mat_rune)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    export_object(f"/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/models/altar_{god_name}.glb")

def build_brazier():
    clear_scene()
    mat_bronze = create_material("BronzeBrazier", (0.75, 0.45, 0.18, 1.0), metallic=0.85, roughness=0.3)
    mat_fire = create_material("FireCore", (1.0, 0.4, 0.05, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.5, 0.1, 1.0))

    # Tripod Legs
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        x = math.sin(rad) * 0.4
        y = math.cos(rad) * 0.4
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.2, location=(x, y, 0.6))
        leg = bpy.context.active_object
        leg.rotation_euler = (math.cos(rad)*0.15, -math.sin(rad)*0.15, 0)
        leg.data.materials.append(mat_bronze)

    # Bowl
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.25, location=(0, 0, 1.2))
    bowl = bpy.context.active_object
    bowl.data.materials.append(mat_bronze)

    # Fire Core
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0, 0, 1.4))
    fire = bpy.context.active_object
    fire.data.materials.append(mat_fire)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    export_object("/home/antigravity/Devarakonda-Siddhardha/GridOps/assets/models/temple_brazier.glb")

if __name__ == "__main__":
    build_column()
    build_altar("zeus", (0.90, 0.92, 0.98, 1.0), (0.2, 0.6, 1.0, 1.0), "lightning")
    build_altar("poseidon", (0.15, 0.35, 0.45, 1.0), (0.1, 0.9, 0.9, 1.0), "trident")
    build_altar("hades", (0.12, 0.10, 0.15, 1.0), (0.7, 0.1, 0.95, 1.0), "hades")
    build_altar("ares", (0.45, 0.12, 0.12, 1.0), (1.0, 0.15, 0.1, 1.0), "ares")
    build_brazier()
