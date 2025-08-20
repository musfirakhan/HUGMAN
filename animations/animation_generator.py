#!/usr/bin/env python3
"""
Animation Generator for HUGMAN
With proper conda environment activation and verification
"""

import os
import sys
import subprocess
import shutil
import glob
from typing import Optional
import json 
# Directory Structure Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTER_JSON = os.path.join(os.getcwd(), "generated_characters", "character1.json")
MOMASK_DIR = os.path.join(SCRIPT_DIR, "momask-codes-main")
GENERATION_DIR = os.path.join(MOMASK_DIR, "generation")
EXP_DIR = os.path.join(GENERATION_DIR, "exp1")
ANIMATIONS_OUTPUT_DIR = os.path.join(EXP_DIR, "animations/0")
FINAL_ANIMATIONS_DIR = os.path.join(SCRIPT_DIR, "files")



with open(CHARACTER_JSON, 'r') as f:
    character_data = json.load(f)

name = character_data.get('name')


def verify_conda_environment():
    """Verify momask conda environment exists and is properly set up"""
    try:
        # Check if environment exists
        env_list = subprocess.run(["conda", "env", "list"], 
                                capture_output=True, 
                                text=True).stdout
        if "momask" not in env_list:
            print("ERROR: Momask conda environment not found")
            print("Please create it with:")
            print("conda env create -f environment.yml")
            return False
        
        # Verify numpy is installed in the environment
        check_numpy = subprocess.run(
            ["conda", "run", "-n", "momask", "python", "-c", "import numpy"],
            capture_output=True,
            text=True
        )
        if check_numpy.returncode != 0:
            print("ERROR: Numpy not properly installed in momask environment")
            print("Try activating the environment and running:")
            print("conda install numpy")
            return False
            
        return True
        
    except Exception as e:
        print(f"ERROR checking conda: {e}")
        return False

def setup_directories():
    """Ensures all required directories exist with proper structure"""
    os.makedirs(ANIMATIONS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(FINAL_ANIMATIONS_DIR, exist_ok=True)

def cleanup_previous_run():
    """Clears the previous generation outputs while preserving directory structure"""
    print("Cleaning up previous run...")
    if os.path.exists(EXP_DIR):
        for f in glob.glob(os.path.join(ANIMATIONS_OUTPUT_DIR, "*")):
            try:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
            except Exception as e:
                print(f"Warning: Could not remove {f}: {e}")
    else:
        os.makedirs(ANIMATIONS_OUTPUT_DIR, exist_ok=True)
    print("Cleanup complete")

def get_latest_bvh() -> Optional[str]:
    """Returns the most recently generated BVH file"""
    bvh_files = glob.glob(os.path.join(ANIMATIONS_OUTPUT_DIR, "*.bvh"))
    return max(bvh_files, key=os.path.getmtime) if bvh_files else None

def generate_bvh_animation(prompt: str, output_name: str = None) -> Optional[str]:
    """Generate BVH animation with proper conda environment activation"""
    if not verify_conda_environment():
        return None
        
    setup_directories()
    cleanup_previous_run()
    
    if not os.path.exists(MOMASK_DIR):
        print(f"ERROR: Momask directory not found at {MOMASK_DIR}")
        return None
    
    original_dir = os.getcwd()
    os.chdir(MOMASK_DIR)
    
    try:
        cmd = [
            "conda", "run", "-n", "momask", "--no-capture-output",
            "python", "gen_t2m.py",
            "--gpu_id", "0",
            "--ext", "exp1",
            "--text_prompt", f'"{prompt}"',
            "--motion_length", "196",
            "--max_motion_length", "196"
        ]
        
        print(f"Generating: {prompt}")
        print("Running command:", " ".join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        generated_bvh = get_latest_bvh()
        if not generated_bvh:
            print("ERROR: No BVH file was generated")
            return None
            
        output_name = output_name or f"{prompt[:50].replace(' ', '_').lower()}.bvh"
        output_name = output_name if output_name.endswith('.bvh') else f"{output_name}.bvh"
        final_path = os.path.join(FINAL_ANIMATIONS_DIR, output_name)
        animation_path=os.path.join(SCRIPT_DIR, f"{name}_action.bvh")
        shutil.copy2(generated_bvh, final_path)
        shutil.copy2(generated_bvh, animation_path)
        print(f"Success! Animation saved to: {final_path}")
        return final_path
        
    except subprocess.CalledProcessError as e:
        print(f"Generation failed. Error output:\n{e.stderr}")
        return None
    finally:
        os.chdir(original_dir)

def main():
    if len(sys.argv) < 2:
        print("Usage: python animation_generator.py 'prompt' [output_name]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not generate_bvh_animation(prompt, output_name):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()