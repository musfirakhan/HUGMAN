"""
HUGMAN Blender Retargeting
==========================

Author: Musfira Aslam
Email: musfiraaslam3@gmail.com
GitHub: https://github.com/musfirakhan

Description:
    This script handles animation retargeting in Blender for HUGMAN characters.
    It loads BVH animations and retargets them to character rigs using Rokoko
    addon, then exports the final animated models in GLB format.

Version: 1.0.0
Last Updated: 2025
"""

import bpy
from mathutils import Vector
import os
import sys

def clear_scene():

    if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT':
        bpy.ops.object.editmode_toggle()
        
    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False
        
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
        
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.data.scenes[0].timeline_markers.clear()
    
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_post.clear()


def retarget_rokoko(source_armature, target_armature):
    def enable_addon(addon_name):
        if addon_name not in bpy.context.preferences.addons:
            bpy.ops.preferences.addon_enable(module=addon_name)

    # Enable the Rokoko Addon
    #enable_addon('rokoko_studio_live_blender_master')

    # Function to build bone list
    def build_bone_list():
        if source_armature:
            bpy.context.scene.rsl_retargeting_armature_source = target_armature
        else:
            print("Source Armature not found")
        if target_armature:
            bpy.context.scene.rsl_retargeting_armature_target = source_armature
        else:
            print("Target Armature not found")
        bpy.ops.rsl.build_bone_list()
    
    build_bone_list()

    # Function to retarget using the Rokoko addon
    def retarget_animation():
        bpy.ops.rsl.retarget_animation()
    
    retarget_animation()



def load_rig(filepath: str, name: str):
    """Load a rig from an FBX file"""
    bpy.ops.wm.collada_import(filepath=filepath)
    rig = bpy.context.active_object
    #rig.name = name
    return rig


def load_animation(filepath: str, name: str):
    """Load a rig from an FBX file"""
    bpy.ops.import_anim.bvh(filepath=filepath)
    rig = bpy.context.active_object
    rig.name = name
    rig.animation_data.action.name = f'{name}_action'
    return rig

def push_action_to_nla(armature, action_name):
    """Push down action to NLA"""
    action = bpy.data.actions.get(action_name)
    if action is None:
        raise ValueError(f"Action '{action_name}' not found")
    if not armature.animation_data:
        armature.animation_data_create()
    armature.animation_data.action = None
    nla_tracks = armature.animation_data.nla_tracks
    nla_track = nla_tracks.new()
    nla_track.name = action_name
    nla_strip = nla_track.strips.new(name=action_name , start=0, action=action)
    return nla_strip.frame_end
 
def export_glb(export_path, name):
    bpy.ops.export_scene.gltf(
        filepath=f"{export_path}/character.glb"
    )

def export_animation(end_time, export_path, name, action):
    bpy.context.scene.frame_end=int(end_time)
    bpy.ops.export_scene.gltf(
        filepath=f"{export_path}/{action}.glb"
    )

def load_fbx(filepath: str):
    """Load a rig from an FBX file"""
    base, _ = os.path.splitext(filepath)
    path=base + ".fbx"
    bpy.ops.import_scene.fbx(filepath=path)
    rig = bpy.context.active_object
    rig.name = "lala"
    rig.show_in_front = True
    return rig

def main(character_path, character_name, animation_path, action):
    animation_name="action"
    export_path= os.path.join(os.getcwd(), "animations")
    # clear_scene()
    # load_fbx(character_path)
    # bpy.ops.object.select_all(action='DESELECT')
    # eye=bpy.data.objects[f"high-polyMesh"]
    # eye.select_set(True)
    # bpy.ops.object.delete()
    # export_glb(export_path,character_name) # saving character only 
    if action:
        clear_scene()
        target_armature = load_rig(character_path, character_name)
        target_armature = bpy.data.objects[character_name]
        action_armature = load_animation(animation_path, animation_name)
        retarget_rokoko(target_armature,action_armature)
        eye=bpy.data.objects[f"{character_name}-highpolyeyes"]
        eye.select_set(True)
        bpy.ops.object.delete()
        action_armature.hide_set(True)
        end_frame=push_action_to_nla(target_armature, f'{animation_name}_action')
        retarget_rokoko(target_armature,action_armature)
        export_animation(end_frame, export_path, character_name, animation_name)
    else: 
        target_armature = load_rig(character_path, character_name)
        target_armature = bpy.data.objects[character_name]
        eye=bpy.data.objects[f"{character_name}-highpolyeyes"]
        eye.select_set(True)
        bpy.ops.object.delete()
        export_glb(export_path,character_name)
    bpy.ops.wm.quit_blender()



if __name__ == "__main__":
    # Parse arguments from command line
    args = sys.argv
    if "--" in args:
        idx = args.index("--")
        args = args[idx + 1:]
    else:
        args = []

    if len(args) != 4:
        print("Usage: blender --background --python blender_retargetting.py -- <character_path> <character_name> <animation_path> <action>")
        sys.exit(1)

    character_path = args[0]
    character_name = args[1]
    animation_path = args[2]
    action = args[3].lower() == "true"

    main(character_path, character_name, animation_path, action)