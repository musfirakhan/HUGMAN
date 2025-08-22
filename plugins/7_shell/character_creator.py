"""
Character Creator Script for HUGMAN
==================================

Author: Musfira Aslam
Email: musfiraaslam3@gmail.com
GitHub: https://github.com/musfirakhan

Description:
    This script is part of the HUGMAN (Humanoid Understanding and Generation via 
    Multimodal AI and NLP) system. It provides automated character creation and 
    parameter application capabilities for MakeHuman integration.
    
    The script reads character parameters from JSON configuration files generated
    by the HUGMAN AI pipeline and applies them to create fully customized 3D human
    characters with clothing, accessories, and proper rigging for animation.


Version: 1.0.0
Last Updated: 2025
"""

import os
import sys
import importlib.util
from core import G
import gui3d
import material
from getpath import getSysDataPath, canonicalPath
import json 
import mh
import datetime
import time

class HumanCharacterManager:
    def __init__(self, plugins_path="plugins", data_path="data"):
        self.human = G.app.selectedHuman
        self.plugins_path = plugins_path
        self.data_path = data_path
        self.category = "Geometries"

        # Initialize required modules
        self._init_clothes_module()
        self._init_skeleton()

    def _load_module(self, file_path, module_name):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _init_clothes_module(self):
        clothes_module = self._load_module(
            os.path.join(self.plugins_path, "3_libraries_clothes_chooser.py"),
            "clothes_module"
        )
        self.clothes_view = clothes_module.ClothesTaskView(self.category)

    def _init_skeleton(self):
        sys.path.append(os.path.join(self.plugins_path, "3_libraries_skeleton"))
        import skeletonlibrary
        self.skeleton_lib = skeletonlibrary.SkeletonLibrary("Skeletons")

    def set_physical_attributes(self, gender=1.0, age=0.5, weight=0.5,
                                muscle=0.5, height=0.5, name="Default"):
        self.human.setGender(gender)
        self.human.setAge(age)
        self.human.setWeight(weight)
        self.human.setMuscle(muscle)
        self.human.setHeight(height)
        self.human.setName(name)
        self.human.applyAllTargets()

    def set_ethnicity(self, caucasian=0.33, african=0.33, asian=0.34):
        self.human.setCaucasian(caucasian)
        self.human.setAfrican(african)
        self.human.setAsian(asian)
        self.human.applyAllTargets()

    def set_material(self, material_path):
        full_path = getSysDataPath(material_path)
        self.human.material = material.fromFile(full_path)
        self.human.applyAllTargets()

    def attach_proxy(self, proxy_path):
        full_path = os.path.join(self.data_path, proxy_path)
        self.clothes_view.selectProxy(full_path)

    def set_skeleton(self, skeleton_file):
        full_path = os.path.join(self.data_path, skeleton_file)
        self.skeleton_lib.chooseSkeleton(full_path)

    def take_high_quality_screenshot(self, custom_filename=None, width=1920, height=1080, export_dir=None):
        """
        Take a high-quality screenshot using production rendering settings.
        
        Args:
            custom_filename (str, optional): Custom filename for the screenshot.
            width (int): Screenshot width (default: 1920)
            height (int): Screenshot height (default: 1080)
            export_dir (str, optional): Directory to save screenshot (same as export path)
        
        Returns:
            str: Path to the saved screenshot file, or None if failed
        """
        try:
            print(f"Taking high-quality screenshot ({width}x{height})...")
            
            # Force a redraw to ensure the scene is properly rendered
            G.app.redraw()
            
            # Small delay to ensure rendering is complete
            time.sleep(0.3)
            
            # Ensure the canvas is the current OpenGL context
            if hasattr(G.app.mainwin, 'canvas') and G.app.mainwin.canvas:
                G.app.mainwin.canvas.makeCurrent()
            
            # Determine save directory
            if export_dir:
                save_dir = export_dir
                print(f"Saving screenshot to export directory: {save_dir}")
            else:
                save_dir = mh.getPath('grab')
                print(f"Saving screenshot to default grab directory: {save_dir}")
            
            # Create directory if it doesn't exist
            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
                print(f"Created directory: {save_dir}")
            
            # Generate filename
            if custom_filename:
                if not custom_filename.endswith('.png'):
                    custom_filename += '.png'
                filename = os.path.join(save_dir, custom_filename)
            else:
                grabName = datetime.datetime.now().strftime('hq_grab_%Y-%m-%d_%H.%M.%S.png')
                filename = os.path.join(save_dir, grabName)
            
            print(f"High-quality screenshot will be saved to: {filename}")
            
            # Method 1: Use current window dimensions with production rendering
            try:
                print("Trying method 1: Current window dimensions with production rendering...")
                
                # Use current window dimensions to avoid blank screenshots
                current_width = G.windowWidth
                current_height = G.windowHeight
                
                print(f"Current window dimensions: {current_width}x{current_height}")
                
                # Set viewport to current window size
                from OpenGL.GL import glViewport
                glViewport(0, 0, current_width, current_height)
                
                # Use production rendering for better quality
                mh.grabScreen(0, 0, current_width, current_height, filename, productionRender=True)
                
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    if file_size > 0:
                        print(f"✓ Method 1 screenshot saved: {os.path.basename(filename)} ({file_size} bytes)")
                        return filename
                    else:
                        print("⚠ Method 1 screenshot file is empty")
                else:
                    print("⚠ Method 1 screenshot file not created")
                    
            except Exception as e1:
                print(f"Method 1 failed: {e1}")
            
            # Method 2: Use current window dimensions without production rendering
            try:
                print("Trying method 2: Current window dimensions without production rendering...")
                
                current_width = G.windowWidth
                current_height = G.windowHeight
                
                glViewport(0, 0, current_width, current_height)
                mh.grabScreen(0, 0, current_width, current_height, filename, productionRender=False)
                
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    if file_size > 0:
                        print(f"✓ Method 2 screenshot saved: {os.path.basename(filename)} ({file_size} bytes)")
                        return filename
                    else:
                        print("⚠ Method 2 screenshot file is empty")
                        
            except Exception as e2:
                print(f"Method 2 failed: {e2}")
            
            # Method 3: Use the original grabScreen method (most reliable)
            try:
                print("Trying method 3: Original grabScreen method...")
                G.app.grabScreen()
                
                # Check for the created file in the default grab directory
                grabPath = mh.getPath('grab')
                if os.path.exists(grabPath):
                    files = os.listdir(grabPath)
                    png_files = [f for f in files if f.endswith('.png')]
                    
                    if png_files:
                        latest_file = max(png_files, key=lambda f: os.path.getctime(os.path.join(grabPath, f)))
                        latest_path = os.path.join(grabPath, latest_file)
                        file_size = os.path.getsize(latest_path)
                        
                        if file_size > 0:
                            # Copy the file to the export directory
                            import shutil
                            try:
                                shutil.copy2(latest_path, filename)
                                print(f"✓ Method 3 screenshot copied to export directory: {os.path.basename(filename)} ({file_size} bytes)")
                                return filename
                            except Exception as copy_error:
                                print(f"Failed to copy screenshot: {copy_error}")
                                return latest_path
                        else:
                            print("⚠ Method 3 screenshot file is empty")
                            
            except Exception as e3:
                print(f"Method 3 failed: {e3}")
            
            # Method 4: Try with smaller dimensions
            try:
                print("Trying method 4: Smaller dimensions...")
                
                # Use smaller, safe dimensions
                safe_width = min(800, G.windowWidth)
                safe_height = min(600, G.windowHeight)
                
                glViewport(0, 0, safe_width, safe_height)
                mh.grabScreen(0, 0, safe_width, safe_height, filename, productionRender=False)
                
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    if file_size > 0:
                        print(f"✓ Method 4 screenshot saved: {os.path.basename(filename)} ({file_size} bytes)")
                        return filename
                        
            except Exception as e4:
                print(f"Method 4 failed: {e4}")
            
            print("✗ All screenshot methods failed")
            return None
                
        except Exception as e:
            print(f"✗ High-quality screenshot failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def take_simple_screenshot(self, custom_filename=None, export_dir=None):
        """
        Take a simple, reliable screenshot using the current window.
        
        Args:
            custom_filename (str, optional): Custom filename for the screenshot.
            export_dir (str, optional): Directory to save screenshot (same as export path)
        
        Returns:
            str: Path to the saved screenshot file, or None if failed
        """
        try:
            print("Taking simple screenshot...")
            
            # Force a redraw
            G.app.redraw()
            time.sleep(0.2)
            
            # Use the most reliable method
            G.app.grabScreen()
            
            # Get the grab directory path
            grabPath = mh.getPath('grab')
            print(f"Screenshot saved to grab directory: {grabPath}")
            
            # Check if any PNG files were created recently
            if os.path.exists(grabPath):
                files = os.listdir(grabPath)
                png_files = [f for f in files if f.endswith('.png')]
                
                if png_files:
                    # Get the most recent file
                    latest_file = max(png_files, key=lambda f: os.path.getctime(os.path.join(grabPath, f)))
                    latest_path = os.path.join(grabPath, latest_file)
                    file_size = os.path.getsize(latest_path)
                    
                    if file_size > 0:
                        # If export directory is specified, copy the file there
                        if export_dir:
                            if not os.path.exists(export_dir):
                                os.makedirs(export_dir, exist_ok=True)
                            
                            if custom_filename:
                                if not custom_filename.endswith('.png'):
                                    custom_filename += '.png'
                                target_filename = os.path.join(export_dir, custom_filename)
                            else:
                                target_filename = os.path.join(export_dir, latest_file)
                            
                            import shutil
                            try:
                                shutil.copy2(latest_path, target_filename)
                                print(f"✓ Simple screenshot copied to export directory: {os.path.basename(target_filename)} ({file_size} bytes)")
                                return target_filename
                            except Exception as copy_error:
                                print(f"Failed to copy screenshot: {copy_error}")
                                return latest_path
                        else:
                            print(f"✓ Simple screenshot saved: {latest_file} ({file_size} bytes)")
                            return latest_path
                    else:
                        print("⚠ Simple screenshot file is empty")
                        return None
                else:
                    print("✗ No PNG files found in grab directory")
                    return None
            else:
                print("✗ Grab directory does not exist")
                return None
                
        except Exception as e:
            print(f"✗ Simple screenshot failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def export_model(self, export_path, format_name=None):
        category = gui3d.app.getCategory("Pose/Animate")
        pose_task = category.getTaskByName("Pose")
        pose_path = os.path.join(self.data_path, "poses", "tpose.bvh")
        pose_task.loadPose(pose_path)
        
        ext = os.path.splitext(export_path)[1].lower()
        base, _ = os.path.splitext(export_path)

        # Always export OBJ for viewing
        obj_path = base + ".obj"

        # Export OBJ
        print(f"Exporting OBJ for viewing: {obj_path}")
        category = gui3d.app.getCategory("Files")
        exporter_task = category.getTaskByName("Export")
        obj_exporter = exporter_task.getExporter('Wavefront obj')
        obj_exporter.export(self.human, lambda ext, diff=False: obj_path)

        # If the requested export is not OBJ, export the requested format too
        if ext != '.obj':
            if format_name is None:
                if format_name is None:
                    if ext == '.fbx':
                        format_name = 'Filmbox (fbx)'
                    elif ext == '.obj':
                        format_name = 'Wavefront obj'
                    elif ext == '.dae':
                        format_name = 'Collada (dae)'
                    elif ext == '.stl':
                        format_name = 'Stereolithography (stl)'
                    elif ext == '.bvh':
                        format_name = 'Biovision Hierarchy BVH'
                    else: 
                        format_name = 'Wavefront obj'
            print(f"Exporting in requested format: {export_path} ({format_name})")
            exporter = exporter_task.getExporter(format_name)
            exporter.export(self.human, lambda ext, diff=False: export_path)
            # rxporting for animations
            dae_exporter = exporter_task.getExporter('Collada (dae)')
            dae_path=  base + ".dae"
            for item in exporter_task.scaleButtons:
                if isinstance(item, tuple):
                    button, name = item
                    if name == 'meter':
                        button.setSelected(True)

            ext='.dae'
            dae_exporter.export(self.human, lambda ext, diff=False: dae_path)



def create_character(
    manager,
    name="HUMAN",
    gender=0.0,
    age=0.2,
    weight=0.4,
    muscle=0.3,
    height=0.5,
    caucasian=0.2,
    african=0.1,
    asian=0.7,
    skin="young_caucasian_female",
    clothes="female_sportsuit01",
    shoes="shoes0",
    hair="ponytail01",
    eyes="high-poly",
    eyebrow="eyebrow009",
    eyelash="eyelashes01",
    teeth="teeth_base",
    tongue="tongue01",
    skeleton="game_engine",
    export_path="/Users/musfiraaslam/Desktop/human_model.fbx"
):
    print(f"Creating character: {name}")
    
    manager.set_physical_attributes(
        gender=gender,
        age=age,
        weight=weight,
        muscle=muscle,
        height=height,
        name=name
    )

    manager.set_ethnicity(
        caucasian=caucasian,
        african=african,
        asian=asian
    )

    manager.set_material(f"skins/{skin}/{skin}.mhmat")

    if isinstance(clothes, list):
        for item in clothes:
            manager.attach_proxy(f"clothes/{item}/{item}.mhclo")
    else:
        manager.attach_proxy(f"clothes/{clothes}/{clothes}.mhclo")
    manager.attach_proxy(f"clothes/{shoes}/{shoes}.mhclo")
    manager.attach_proxy(f"hair/{hair}/{hair}.mhpxy")
    manager.attach_proxy(f"eyes/{eyes}/{eyes}.mhpxy")
    manager.attach_proxy(f"eyebrows/{eyebrow}/{eyebrow}.mhpxy")
    manager.attach_proxy(f"eyelashes/{eyelash}/{eyelash}.mhpxy")
    manager.attach_proxy(f"teeth/{teeth}/{teeth}.mhpxy")
    manager.attach_proxy(f"tongue/{tongue}/{tongue}.mhpxy")

    manager.set_skeleton(f"rigs/{skeleton}.mhskel")
    
    # Take a high-quality screenshot after character creation
    print("Taking high-quality screenshot of completed character...")
    screenshot_path = manager.take_high_quality_screenshot(f"{name}_character_hq", 1920, 1080)
    if screenshot_path:
        print(f"High-quality character screenshot saved: {screenshot_path}")
    
    manager.export_model(export_path)


def main():
    manager = HumanCharacterManager()    

    # create_character(
    #     manager=manager,
    #     name="Laila",
    #     gender=0,
    #     age=0.6,
    #     weight=0.4,
    #     muscle=0.3,
    #     height=0.6,
    #     caucasian=0.4,
    #     african=0.1,
    #     asian=0.4,
    #     skin="young_caucasian_female",
    #     clothes="female_elegantsuit01",
    #     shoes="shoes01",
    #     hair="ponytail01",
    #     eyes="low-poly",
    #     eyebrow="eyebrow009",
    #     eyelash="eyelashes01",
    #     teeth="teeth_base",
    #     tongue="tongue01",
    #     skeleton="game_engine",
    #     export_path="/Users/musfiraaslam/Desktop/girl_model.fbx"
    # )
    cwd = os.getcwd()
    config_path = os.path.join(cwd, "generated_characters", "character1.json")

 
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_path}")
        sys.exit(1)
    
    # Initialize character manager
    manager = HumanCharacterManager()
    
    # Create character using the loaded configuration
    create_character(manager, **config)


if __name__ == "__main__":
    main()