import os
import json
import sys
import subprocess

# Define constant paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_SCRIPT = os.path.join(SCRIPT_DIR, "llm.py")
MAKEHUMAN_SCRIPT = os.path.join(SCRIPT_DIR, "makehuman.py")
BLENDER_RUNNER = os.path.join(SCRIPT_DIR, "blender_runner.py")
CHARACTER_JSON = os.path.join(SCRIPT_DIR, "generated_characters", "character1.json")

def run_llm(description):
    """Run the LLM script with the given description"""
    print(f"\nRunning LLM script with description: {description}")
    try:
        subprocess.run(["python", LLM_SCRIPT, description], check=True)
        print("LLM script completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running LLM script: {e}")
        return False

def run_blender(blender_path):
    """Run Blender with the Blender runner script"""
    # Read the character JSON to get the export path
    with open(CHARACTER_JSON, 'r') as f:
        character_data = json.load(f)
        print("\nCharacter data from JSON:")
        print(json.dumps(character_data, indent=2))
    
    # Get the export path from the JSON
    fbx_path = character_data.get('export_path')
    if not fbx_path:
        print("Error: No export path found in character JSON")
        return False
    
    print(f"\nRunning Blender: {blender_path}")
    print(f"Using runner script: {BLENDER_RUNNER}")
    print(f"Processing file: {fbx_path}")
    
    try:
        subprocess.run([
            blender_path,
            "--python", BLENDER_RUNNER,
            "--", fbx_path
        ], check=True)
        print("Blender processing completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Blender: {e}")
        return False

def run_character_pipeline(description, blender_path):
    """Run the complete character generation pipeline"""
    print("\n=== Starting Character Generation Pipeline ===")
    
    # Step 1: Run LLM to generate character JSON
    print("\n1. Generating character data...")
    if not run_llm(description):
        return False
    
    # Step 2: Run MakeHuman (ignore if it crashes)
    print("\n2. Running MakeHuman...")
    try:
        subprocess.run(["python", MAKEHUMAN_SCRIPT], check=False)
        print("MakeHuman script completed")
    except Exception as e:
        print(f"MakeHuman script ended (this is expected): {e}")
    
    # Step 3: Run Blender
    print("\n3. Running Blender processing...")
    if not run_blender(blender_path):
        return False
    
    print("\n=== Character Generation Pipeline Completed Successfully ===")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python character_pipeline.py \"character description\" \"path/to/blender\"")
        print("Example: python character_pipeline.py \"A tall woman\" \"/Applications/Blender.app/Contents/MacOS/Blender\"")
        sys.exit(1)
    
    # Get description and Blender path from command line arguments
    description = sys.argv[1]
    blender_path = sys.argv[2]
    
    # Run the pipeline
    success = run_character_pipeline(description, blender_path)
    
    if success:
        print("\nCharacter generation completed successfully!")
    else:
        print("\nCharacter generation failed. Please check the error messages above.") 