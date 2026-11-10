"""
Blender script to generate 4 dedicated architectural Greek Temples for each deity:
1. temple_zeus.glb - The High Olympian Sky Sanctuary (White marble, gold trims, lightning pediment)
2. temple_poseidon.glb - The Pelagic Ocean Promontory Temple (Sea-stone, teal roof, trident pediment)
3. temple_hades.glb - The Stygian Necromanteion Crypt Temple (Obsidian, purple trims, bident/skull pediment)
4. temple_ares.glb - The Citadel of War (Red granite, bronze armor plates, crossed blades pediment)
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
                bsdf.inputs["Emission Strength"].default_value = 2.5
    return mat

def build_dedicated_temple(god_id):
    clear_scene()
    mesh_parts = []

    # Configure deity-specific palettes & materials
    if god_id == "zeus":
        mat_stone = create_mat("ZeusMarble", (0.95, 0.95, 0.97, 1.0), metallic=0.1, roughness=0.3)
        mat_trim = create_mat("ZeusGoldLeaf", (0.95, 0.82, 0.22, 1.0), metallic=0.95, roughness=0.2)
        mat_roof = create_mat("ZeusBlueRoof", (0.15, 0.35, 0.70, 1.0), metallic=0.1, roughness=0.5)
        mat_flame = create_mat("ZeusFlame", (0.4, 0.85, 1.0, 1.0), emission=(0.4, 0.85, 1.0, 1.0))
    elif god_id == "poseidon":
        mat_stone = create_mat("PoseidonSeaStone", (0.82, 0.88, 0.90, 1.0), metallic=0.1, roughness=0.4)
        mat_trim = create_mat("PoseidonGold", (0.90, 0.75, 0.20, 1.0), metallic=0.92, roughness=0.25)
        mat_roof = create_mat("PoseidonTealRoof", (0.10, 0.60, 0.72, 1.0), metallic=0.2, roughness=0.4)
        mat_flame = create_mat("PoseidonAquaFlame", (0.2, 0.95, 0.85, 1.0), emission=(0.2, 0.95, 0.85, 1.0))
    elif god_id == "hades":
        mat_stone = create_mat("HadesObsidian", (0.12, 0.10, 0.15, 1.0), metallic=0.3, roughness=0.4)
        mat_trim = create_mat("HadesDarkGold", (0.45, 0.32, 0.50, 1.0), metallic=0.85, roughness=0.3)
        mat_roof = create_mat("HadesPurpleRoof", (0.22, 0.12, 0.30, 1.0), metallic=0.2, roughness=0.5)
        mat_flame = create_mat("HadesSoulFlame", (0.75, 0.35, 1.0, 1.0), emission=(0.75, 0.35, 1.0, 1.0))
    else: # ares
        mat_stone = create_mat("AresRedGranite", (0.62, 0.18, 0.16, 1.0), metallic=0.2, roughness=0.5)
        mat_trim = create_mat("AresWarBronze", (0.85, 0.52, 0.20, 1.0), metallic=0.92, roughness=0.3)
        mat_roof = create_mat("AresCrimsonRoof", (0.80, 0.12, 0.10, 1.0), metallic=0.1, roughness=0.5)
        mat_flame = create_mat("AresBloodFlame", (1.0, 0.25, 0.10, 1.0), emission=(1.0, 0.25, 0.10, 1.0))

    # Temple Dimensions: Width = 15m (X: -7.5 to 7.5), Length = 22m (Y: -11 to 11), Height ~ 8m
    # 1. Crepidoma (3-Tiered Foundation Steps)
    for i, (scale_x, scale_y, z_pos) in enumerate([(16.0, 23.0, 0.2), (15.2, 22.2, 0.5), (14.4, 21.4, 0.8)]):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_pos))
        step = bpy.context.active_object
        step.scale = (scale_x, scale_y, 0.3)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(mat_stone if i < 2 else mat_trim)
        mesh_parts.append(step)

    # 2. Peristyle Colonnade (Fluted Columns around perimeter)
    # Front & Back: X = [-6.0, -3.6, -1.2, 1.2, 3.6, 6.0], Y = -9.6 (front) and Y = 9.6 (back)
    # Sides: Y = [-6.4, -3.2, 0.0, 3.2, 6.4]
    col_x_coords = [-5.8, -3.5, -1.2, 1.2, 3.5, 5.8]
    col_y_coords = [-9.4, -6.3, -3.1, 0.0, 3.1, 6.3, 9.4]
    column_positions = []

    for x in col_x_coords:
        column_positions.append((x, -9.4)) # Front row
        column_positions.append((x, 9.4))  # Back row

    for y in col_y_coords[1:-1]:
        column_positions.append((-5.8, y)) # Left row
        column_positions.append((5.8, y))  # Right row

    for cx, cy in column_positions:
        # Column Base
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 1.05))
        cb = bpy.context.active_object
        cb.scale = (0.9, 0.9, 0.2)
        bpy.ops.object.transform_apply(scale=True)
        cb.data.materials.append(mat_trim)
        mesh_parts.append(cb)

        # Fluted Column Shaft
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.38, depth=4.6, location=(cx, cy, 3.45))
        cs = bpy.context.active_object
        cs.data.materials.append(mat_stone)
        mesh_parts.append(cs)

        # Column Capital (Doric / Ionic)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 5.85))
        cc = bpy.context.active_object
        cc.scale = (0.95, 0.95, 0.2)
        bpy.ops.object.transform_apply(scale=True)
        cc.data.materials.append(mat_trim)
        mesh_parts.append(cc)

    # 3. Entablature (Architrave & Frieze spanning columns)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 6.2))
    arch = bpy.context.active_object
    arch.scale = (13.6, 21.0, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    arch.data.materials.append(mat_trim)
    mesh_parts.append(arch)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 6.6))
    frieze = bpy.context.active_object
    frieze.scale = (13.2, 20.6, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    frieze.data.materials.append(mat_stone)
    mesh_parts.append(frieze)

    # 4. Triangular Pediments (Front & Back Gables)
    for y_pos, sign in [(-9.8, 1), (9.8, -1)]:
        # Triangular Prism for Pediment
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=7.0, depth=0.8, location=(0, y_pos, 7.5))
        ped = bpy.context.active_object
        ped.rotation_euler = (math.radians(90), 0, math.radians(90))
        bpy.ops.object.transform_apply(rotation=True)
        ped.scale = (1.9, 0.5, 0.3)
        bpy.ops.object.transform_apply(scale=True)
        ped.data.materials.append(mat_stone)
        mesh_parts.append(ped)

        # Pediment border cornice
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_pos, 8.4))
        corn = bpy.context.active_object
        corn.scale = (13.8, 0.4, 0.15)
        bpy.ops.object.transform_apply(scale=True)
        corn.data.materials.append(mat_trim)
        mesh_parts.append(corn)

    # 5. Pitched Gabled Roof
    # Left slope
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.4, 0, 7.7))
    r_left = bpy.context.active_object
    r_left.scale = (7.6, 21.2, 0.2)
    r_left.rotation_euler = (0, math.radians(22), 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    r_left.data.materials.append(mat_roof)
    mesh_parts.append(r_left)

    # Right slope
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.4, 0, 7.7))
    r_right = bpy.context.active_object
    r_right.scale = (7.6, 21.2, 0.2)
    r_right.rotation_euler = (0, math.radians(-22), 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    r_right.data.materials.append(mat_roof)
    mesh_parts.append(r_right)

    # Ridge beam along peak
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 8.45))
    ridge = bpy.context.active_object
    ridge.scale = (0.4, 21.4, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    ridge.data.materials.append(mat_trim)
    mesh_parts.append(ridge)

    # 6. Inner Cella (Sanctum walls with open monumental entrance)
    # Left Wall
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.8, 1.0, 3.4))
    w_left = bpy.context.active_object
    w_left.scale = (0.5, 14.0, 4.8)
    bpy.ops.object.transform_apply(scale=True)
    w_left.data.materials.append(mat_stone)
    mesh_parts.append(w_left)

    # Right Wall
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.8, 1.0, 3.4))
    w_right = bpy.context.active_object
    w_right.scale = (0.5, 14.0, 4.8)
    bpy.ops.object.transform_apply(scale=True)
    w_right.data.materials.append(mat_stone)
    mesh_parts.append(w_right)

    # Back Wall (North/Rear of cella)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 8.0, 3.4))
    w_back = bpy.context.active_object
    w_back.scale = (8.0, 0.5, 4.8)
    bpy.ops.object.transform_apply(scale=True)
    w_back.data.materials.append(mat_stone)
    mesh_parts.append(w_back)

    # 7. Interior Sanctum Dais & High Altar
    # Elevated Dais where God stands
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 5.0, 1.2))
    dais = bpy.context.active_object
    dais.scale = (5.5, 4.5, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    dais.data.materials.append(mat_trim)
    mesh_parts.append(dais)

    # High Altar Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.5, 1.5))
    altar_b = bpy.context.active_object
    altar_b.scale = (2.2, 1.2, 0.9)
    bpy.ops.object.transform_apply(scale=True)
    altar_b.data.materials.append(mat_stone)
    mesh_parts.append(altar_b)

    # Altar Top Slab
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.5, 2.0))
    altar_s = bpy.context.active_object
    altar_s.scale = (2.4, 1.4, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    altar_s.data.materials.append(mat_trim)
    mesh_parts.append(altar_s)

    # 2 Sacred Eternal Braziers flanking the Dais
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.8, location=(sign * 2.6, 3.0, 1.4))
        br_base = bpy.context.active_object
        br_base.data.materials.append(mat_trim)
        mesh_parts.append(br_base)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(sign * 2.6, 3.0, 2.0))
        br_flame = bpy.context.active_object
        br_flame.data.materials.append(mat_flame)
        mesh_parts.append(br_flame)

    # 8. Front Pediment Sigil Carvings
    if god_id == "zeus":
        # Master Lightning Bolt on front pediment
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -9.85, 7.3))
        sigil = bpy.context.active_object
        sigil.scale = (0.2, 0.05, 1.5)
        sigil.rotation_euler = (0, math.radians(25), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        sigil.data.materials.append(mat_flame)
        mesh_parts.append(sigil)
    elif god_id == "poseidon":
        # Golden Trident on front pediment
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.8, location=(0, -9.85, 7.3))
        sigil = bpy.context.active_object
        sigil.data.materials.append(mat_trim)
        mesh_parts.append(sigil)
        for poff in [-0.3, 0.3]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.8, location=(poff, -9.85, 7.7))
            prong = bpy.context.active_object
            prong.data.materials.append(mat_flame)
            mesh_parts.append(prong)
    elif god_id == "hades":
        # Underworld Dual Prongs on front pediment
        for poff in [-0.25, 0.25]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.6, location=(poff, -9.85, 7.3))
            prong = bpy.context.active_object
            prong.data.materials.append(mat_flame)
            mesh_parts.append(prong)
    else: # ares
        # Crossed Swords / Blades on front pediment
        for rot in [-35, 35]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -9.85, 7.3))
            blade = bpy.context.active_object
            blade.scale = (0.12, 0.05, 1.7)
            blade.rotation_euler = (0, math.radians(rot), 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            blade.data.materials.append(mat_trim)
            mesh_parts.append(blade)

    # Join and Export Temple
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    temple = bpy.context.active_object
    temple.name = f"Temple_{god_id.capitalize()}"

    out_file = os.path.join(OUT_DIR, f"temple_{god_id}.glb")
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        use_selection=True,
        export_format='GLB'
    )
    print(f"Exported Dedicated Temple: {out_file}")

if __name__ == "__main__":
    for god in ["zeus", "poseidon", "hades", "ares"]:
        build_dedicated_temple(god)
    print("=== ALL 4 DEDICATED TEMPLES GENERATED SUCCESSFULLY! ===")
