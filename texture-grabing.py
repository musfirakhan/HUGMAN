import os
import sys
import json
import requests
from io import BytesIO
from PIL import Image
import ollama
import re

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTER_JSON = os.path.join(SCRIPT_DIR, "generated_characters", "character1.json")
UNSPLASH_ACCESS_KEY = "beNvkEhxp23Xg8GrplOv5ywLNgEEkV7DfmPywwwoACg"

# Initialize Ollama client and model
ollama_model = "llama3.2"
ollama_client = ollama.Client()

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

def analyze_prompt_with_llama(prompt):
    clothes_list = find_element_in_character_json()
    print("---- LIST OF CLOTHES IN CHARACTER JSON ----")
    print(clothes_list)
    llama_prompt = f"""
    The user has provided the following description: "{prompt}".

    Your task:
    1. Determine if the description includes a specific texture, color, or material for any item.
    2. Identify the items from the following list: {clothes_list}. 
    3. For each identified item, generate a texture search query using the provided color/material/texture and the item name.

    Respond in the following JSON format:
    {{
        "answer": True/False,
        "clothing_items": [
            {{"item": "item_name", "texture_query": "query_for_texture"}},
            ...
        ]
    }}
    You MUST return ONLY valid JSON — without any markdown, explanations, or comments.
    """

    response = ollama_client.generate(model=ollama_model, prompt=llama_prompt)
    cleaned = clean_llm_json_response(response.response)

    try:
        result = json.loads(cleaned)
        print(result)
        return result
    except json.JSONDecodeError:
        print("Error: Unable to parse LLaMA response.")
        print("Raw string received from LLaMA:", cleaned)
        return None

def find_element_in_character_json():
    if not os.path.exists(CHARACTER_JSON):
        print(f"Character JSON file not found: {CHARACTER_JSON}")
        return None
    with open(CHARACTER_JSON, "r") as f:
        character_data = json.load(f)
    clothes = character_data.get("clothes")
    return clothes

def search_unsplash(query):
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["raw"]
    return None

def replace_texture_file(old_texture_path, new_texture_url):
    response = requests.get(new_texture_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(old_texture_path)
        print(f"Replaced texture at: {old_texture_path}")
    else:
        print(f"Failed to download new texture from: {new_texture_url}")

def main(prompt):
    print(f"Processing prompt: {prompt}")

    # Step 1: Use LLaMA to analyze the prompt
    llama_result = analyze_prompt_with_llama(prompt)

    if not llama_result or not llama_result.get("answer"):
        print("No texture demand identified or LLaMA response is incomplete.")
        return

    clothing_items = llama_result.get("clothing_items", [])
    if not clothing_items:
        print("No clothing items identified in the prompt.")
        return

    for clothing in clothing_items:
        clothing_item = clothing.get("item")
        texture_query = clothing.get("texture_query")

        if not clothing_item or not texture_query:
            print(f"Invalid clothing item or texture query: {clothing}")
            continue

        print(f"Processing Clothing Item: {clothing_item}")
        print(f"Texture Query: {texture_query}")

        # Step 2: Find the .mhmat file for the clothing item
        element_path = os.path.join(SCRIPT_DIR, "data", "clothes", clothing_item)
        mhmat_file = os.path.join(element_path, f"{clothing_item}.mhmat")

        if not os.path.exists(mhmat_file):
            print(f".mhmat file not found: {mhmat_file}")
            continue

        # Step 3: Parse the .mhmat file to find the diffuse texture path
        diffuse_texture_path = None
        with open(mhmat_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("diffuseTexture"):
                    parts = line.split()
                    if len(parts) >= 2:
                        diffuse_texture_path = parts[1]
                    break

        if not diffuse_texture_path:
            print(f"No 'diffuseTexture' entry found in .mhmat file: {mhmat_file}")
            continue

        texture_name = diffuse_texture_path
        print(f"Diffuse texture file name: {texture_name}")
        texture_file = os.path.join(SCRIPT_DIR, "output", "textures", texture_name)

        # Step 4: Search Unsplash for a new texture
        new_texture_url = search_unsplash(texture_query)
        if not new_texture_url:
            print(f"No suitable texture found on Unsplash for query: {texture_query}")
            continue

        # Step 5: Replace the old texture with the new one
        replace_texture_file(texture_file, new_texture_url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python texture-grabing.py \"<prompt>\"")
        print("Example: python texture-grabing.py \"I want a purple texture for the shirt and a denim texture for the pants.\"")
        sys.exit(1)

    user_prompt = sys.argv[1]
    main(user_prompt)