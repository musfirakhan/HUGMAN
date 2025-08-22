import os
import json
import sys
import subprocess
import ollama 
import re
import subprocess
ollama_model = "llama3.2"
ollama_client = ollama.Client()

# Use current working directory
SCRIPT_DIR = os.getcwd()
BLENDER_RUNNER = os.path.join(SCRIPT_DIR, "animations", "blender_retargetting.py")
CHARACTER_JSON = os.path.join(SCRIPT_DIR, "generated_characters", "character1.json")

# Import the animation generator
from animation_generator import generate_bvh_animation

def clean_llm_json_response(json_str):
    json_str = re.sub(r"^```[a-zA-Z]*\n?", "", json_str.strip())
    json_str = re.sub(r"```$", "", json_str.strip())
    start = json_str.find('{')
    end = json_str.rfind('}')
    cleaned = json_str[start:end+1] if start != -1 and end != -1 else json_str
    if not cleaned.startswith("{"):
        cleaned = "{" + cleaned
    if not cleaned.endswith("}"):
        cleaned = cleaned + "}"
    return cleaned

def detect_action_or_return_no(prompt):
    llama_prompt = f"""
    Analyze this user input: "{prompt}"

    Strict Rules:
    1. Look for EXPLICIT physical actions like: walking, running, jumping, waving, dancing, sitting, standing, pointing, etc.
    2. If the prompt contains a CLEAR physical action, return a SHORT prompt to generate that specific animation.
    3. If the prompt is just describing appearance (hair, clothes, age, etc.) with NO physical action, return "no".
    4. If the prompt is ambiguous or doesn't clearly specify a physical action, return "no".

    Examples:
    - "A girl with blue hair" → "no" (no action)
    - "A man in a suit" → "no" (no action)  
    - "A girl waving" → "create animation for waving"
    - "A man walking" → "create animation for walking"
    - "A person dancing" → "create animation for dancing"

    Respond ONLY with valid JSON in this exact format:
    {{
        "answer": "generation_prompt_string" OR "no"
    }}
    DO NOT include any extra text, comments, or formatting.

    """
    response = ollama_client.generate(model=ollama_model, prompt=llama_prompt)
    cleaned = clean_llm_json_response(response.response)

    try:
        result = json.loads(cleaned)
        answer = result.get("answer")
        
        if answer and answer != "no":  # If we have an action prompt
            return answer  # Return the prompt string directly
        else:
            return None  # Return None for "no" or invalid responses
            
    except json.JSONDecodeError:
        print("JSON Error. Raw output:", cleaned)
        return None 

def run_blender(blender_path, action_prompt):
    """Run Blender with the Blender runner script"""
    # Read the character JSON to get the export path
    if not os.path.exists(CHARACTER_JSON):
        print(f"Error: Character JSON file not found: {CHARACTER_JSON}")
        return False
    
    with open(CHARACTER_JSON, 'r') as f:
        character_data = json.load(f)
    
    # Get data from JSON
    dae_path = character_data.get('export_path')
    name = character_data.get('name')

    
    # Validate JSON fields
    if not dae_path:
        print("Error: No export path found in character JSON")
        return False
    if not name:
        print("Error: No character name found in character JSON")
        return False
    
    # Ensure .dae extension
    base_path = os.path.splitext(dae_path)[0]
    dae_path = base_path + '.dae'

    if action_prompt:
        action=True
        animation_path = os.path.join(SCRIPT_DIR, "animations", f"{name}_action.bvh")
        # Use animation generator instead of client script
        result = generate_bvh_animation(action_prompt, f"{name}_action")
        if not result:
            print(f"Error: Failed to generate animation for '{action_prompt}'")
            return False
    else:
        action=False
        animation_path = ""  # No animation path when no action

    if not os.path.exists(dae_path):
        print(f"Error: .dae file not found: {dae_path}")
        return False
    
    # Only check for animation file if we're doing an action
    if action_prompt and not os.path.exists(animation_path):
        print(f"Error: .bvh file not found: {animation_path}")
        return False
    
    if not os.path.exists(BLENDER_RUNNER):
        print(f"Error: Blender runner script not found: {BLENDER_RUNNER}")
        return False
    
    print(f"\nRunning Blender: {blender_path}")
    print(f"Using runner script: {BLENDER_RUNNER}")

    try:
        subprocess.run([
            blender_path, 
            "--background",	
            "--python", BLENDER_RUNNER,
            "--",  
            f"C:/Users/KHAN/Desktop/assets-mhc/game/RunTheBridge/HUGMAN/output/{name}.dae",
            name,
            f"C:/Users/KHAN/Desktop/assets-mhc/game/RunTheBridge/HUGMAN/animations/{name}_action.bvh",
            str(bool(action_prompt))
        ], check=True)
        print("Blender processing completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Blender: {e}")
        return False
    except FileNotFoundError as e:
        print(f"Error: Blender executable not found: {e}")
        return False



def main(prompt: str):
   
    print(f"Analyzing prompt: '{prompt}'")
    action_prompt = detect_action_or_return_no(prompt)
    
    if action_prompt:
        print(f"Action detected: '{action_prompt}'")
    else:
        print("No action detected - will generate static character only")
    
    run_blender(r"C:\Program Files\Blender Foundation\Blender 2.82\blender.exe", action_prompt)
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python text2animations.py <prompt>")
        sys.exit(1)

    prompt = sys.argv[1]
    main(prompt)