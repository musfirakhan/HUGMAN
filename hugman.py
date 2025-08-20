# FOR DESKTOP
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import trimesh
import numpy as np
import os
import json
import sys
import subprocess
import ollama
import re
# Define constant paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_SCRIPT = os.path.join(SCRIPT_DIR, "parameter_generater.py")
MAKEHUMAN_SCRIPT = os.path.join(SCRIPT_DIR, "makehuman.py")
CHARACTER_JSON = os.path.join(SCRIPT_DIR, "generated_characters", "character1.json")
TEXTURE_GRABING_SCRIPT = os.path.join(SCRIPT_DIR, "texture-grabing.py")
ANIMATION_RUNNER = os.path.join(SCRIPT_DIR, "animations", "text2animations.py")
ollama_model = "llama3.2"
ollama_client = ollama.Client()

def view_model(model_path):
    # Load your mesh (OBJ, PLY, etc.)
    mesh = trimesh.load(model_path)

    # If it's a Scene, extract the first geometry
    if isinstance(mesh, trimesh.Scene):
        # Combine all geometries into a single mesh (if you want all parts)
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    # Convert to vertex/face arrays
    verts = mesh.vertices
    faces = mesh.faces

    # Center the mesh at the origin
    center = verts.mean(axis=0)
    verts_centered = verts - center
    size = np.linalg.norm(verts.max(axis=0) - verts.min(axis=0))

    ########## commented part is for showing mesh of 3d object

    # Create Qt app and 3D view widget
    # app = pg.mkQApp("3D Model Viewer")
    # w = gl.GLViewWidget()
    # w.show()
    # w.setWindowTitle('3D Model Viewer')

    # # Set background to dark grey using OpenGL directly
    # try:
    #     w.setBackgroundColor((50, 50, 50, 1))
    # except Exception:
    #     import OpenGL.GL as ogl
    #     w.paintGL = lambda: ogl.glClearColor(50, 50, 50, 1)

    # # Center the view on the origin (where the mesh is now centered)
    # w.opts['center'] = pg.Vector(0, 0, 0)
    # # Set camera distance based on model size
    # w.setCameraPosition(distance=size * 2)

    # Create mesh item
    meshdata = gl.MeshData(vertexes=verts_centered, faces=faces)
    m1 = gl.GLMeshItem(meshdata=meshdata, smooth=True, color=(1, 0, 0, 1), shader='shaded', drawEdges=True)
    # w.addItem(m1)

    mesh.show(background=[0.40, 0.40, 0.40, 1])  # Opens in browser, supports background color

    # app.exec_() 





def run_llm(description):
    """Run the LLM script with the given description"""
    print(f"\nRunning LLM script with description: {description}")
    try:
        subprocess.run([sys.executable, LLM_SCRIPT, description], check=True)
        print("LLM script completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running LLM script: {e}")
        return False


def run_character_pipeline(description):
    """Run the complete character generation pipeline"""
    print("\n=== Starting Character Generation Pipeline ===")
    
    # Step 1: Run LLM to generate character JSON
    print("\n1. Generating character data...")
    if not run_llm(description):
        return False
    
    # Step 2: Run MakeHuman (ignore if it crashes)
    print("\n2. Running MakeHuman...")
    try:
        subprocess.run([sys.executable, MAKEHUMAN_SCRIPT], check=False)
        print("MakeHuman script completed")
    except Exception as e:
        print(f"MakeHuman script ended (this is expected): {e}")
    
    requires_texture = analyze_user_input_with_llama(description)
    if requires_texture:
        print("LLaMA determined that a specific texture is required.")
        subprocess.run([sys.executable, TEXTURE_GRABING_SCRIPT, description], check=True)

    else:
        print("LLaMA determined that no specific texture is required.")

    # Step 3: Run 3D Model Viewer
    print("\n3. Running 3D Model Viewer...")

    with open(CHARACTER_JSON, 'r') as f:
        character_data = json.load(f)
        print("\nCharacter data from JSON:")
        print(json.dumps(character_data, indent=2))
    
    # Get the export path from the JSON
    export_path = character_data.get('export_path')
    if not export_path:
        print("Error: No export path found in character JSON")
        return False
    base, _ = os.path.splitext(export_path)
    obj_path = base + ".obj"
    #view_model(obj_path)

    print("\n=== Character Generation Pipeline Completed Successfully ===")
    print("=====Now Animation ========")
    subprocess.run([sys.executable, ANIMATION_RUNNER, description], check=True)

    return True
def run_texture_grabing():
    print("\nRunning texture-grabing.py...")
    result = subprocess.run(["python", TEXTURE_GRABING_SCRIPT], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running texture-grabing.py: {result.stderr}")

def clean_llm_json_response(json_str):
    json_str = re.sub(r"^```[a-zA-Z]*\n?", "", json_str.strip())
    json_str = re.sub(r"```$", "", json_str.strip())

    # Extract the content between the first { and the last }
    start = json_str.find('{')
    end = json_str.rfind('}')
    cleaned = json_str[start:end+1] if start != -1 and end != -1 else json_str

    # Brace correction in case cleaning missed something
    if not cleaned.startswith("{"):
        cleaned = "{" + cleaned
    if not cleaned.endswith("}"):
        cleaned = cleaned + "}"
    cleaned = cleaned.replace("True", "true").replace("False", "false")


    return cleaned
def analyze_user_input_with_llama(user_input):
    prompt = f"""
            Analyze the following description: '{user_input}'

            Does it mention any color (e.g., "red", "blue", "purple"), pattern (e.g., "floral", "striped", "checkered"), or material (e.g., "denim", "leather", "silk") for clothing item?
            PLEASE respond with True if you think the description explicitly requires a specific texture, color or pattern for any clothing item, otherwise respond with False.

            Respond with **ONLY** valid JSON in this exact format (with no extra text):

            {{ "answer": true }}

            or

            {{ "answer": false }}

            """

    response = ollama_client.generate(model=ollama_model, prompt=prompt)
    cleaned = clean_llm_json_response(response.response)

    try:
        result = json.loads(cleaned)
        print(result)
        if result["answer"]==True:
            print("LLaMA detected a texture requirement.")
            return True
        else:
            print("LLaMA did not detect a texture requirement.")
            return False
        
    except json.JSONDecodeError:
        print("Error: Unable to parse LLaMA response.")
        print("Raw string received from LLaMA:", cleaned)
        return None

    


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hugman.py \"character description\"")
        print("Example: python hugman.py  woman\"")
        sys.exit(1)

    description = sys.argv[1]

    # Run the pipeline
    success = run_character_pipeline(description)
    
    if success:
        print("\nCharacter generation completed successfully!")
    else:
        print("\nCharacter generation failed. Please check the error messages above.") 