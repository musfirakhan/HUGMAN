import bpy
import sys

def import_fbx_and_prepare_view(fbx_path: str):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    # Import the FBX model
    bpy.ops.import_scene.fbx(filepath=fbx_path)

def clear_scene():
    """Delete all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Read the FBX path from sys.argv (after the '--')
if len(sys.argv) > 1:
    fbx_path = sys.argv[-1]
    clear_scene()
    print("hhii", fbx_path)
    import_fbx_and_prepare_view(fbx_path)
else:
    print("No FBX path provided. Usage: blender --python blender_runner.py -- /path/to/your/file.fbx")