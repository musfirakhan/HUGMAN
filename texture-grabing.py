import os
import sys
import json
import requests
from io import BytesIO
from PIL import Image
import ollama
import re

# Try to import Stable Diffusion dependencies, but make them optional
STABLE_DIFFUSION_AVAILABLE = False
try:
    import cv2
    import numpy as np
    import torch
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
    STABLE_DIFFUSION_AVAILABLE = True
    print("Stable Diffusion dependencies loaded successfully!")
except ImportError as e:
    print(f"Stable Diffusion dependencies not available: {e}")
    print("Will use Unsplash fallback for texture generation.")
except Exception as e:
    print(f"Error loading Stable Diffusion: {e}")
    print("Will use Unsplash fallback for texture generation.")

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTER_JSON = os.path.join(SCRIPT_DIR, "generated_characters", "character1.json")
UNSPLASH_ACCESS_KEY = "beNvkEhxp23Xg8GrplOv5ywLNgEEkV7DfmPywwwoACg"

# Initialize Ollama client and model
ollama_model = "llama3.2"
ollama_client = ollama.Client()

# Initialize Stable Diffusion pipeline (lazy loading)
stable_diffusion_pipeline = None
controlnet_model = None

def initialize_stable_diffusion():
    """Initialize Stable Diffusion ControlNet pipeline"""
    global stable_diffusion_pipeline, controlnet_model
    
    if not STABLE_DIFFUSION_AVAILABLE:
        print("Stable Diffusion not available - skipping AI generation")
        return False
    
    if stable_diffusion_pipeline is None:
        try:
            print("Initializing Stable Diffusion ControlNet...")
            controlnet_model = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float16
            )
            
            stable_diffusion_pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet_model,
                torch_dtype=torch.float16
            ).to("cuda")
            
            print("Stable Diffusion initialized successfully!")
        except Exception as e:
            print(f"Error initializing Stable Diffusion: {e}")
            return False
    return True

def generate_texture_with_stable_diffusion(image_path, texture_query, output_path):
    """Generate texture using Stable Diffusion ControlNet"""
    if not initialize_stable_diffusion():
        print("Failed to initialize Stable Diffusion")
        return False
    
    try:
        # Load and prepare input image
        input_image = cv2.imread(image_path)
        if input_image is None:
            print(f"Could not load image: {image_path}")
            return False
            
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        height, width = input_image.shape[:2]
        
        # Create edge detection for ControlNet
        gray = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        
        # Create a mask for the entire image (or specific regions)
        mask = np.ones((height, width), dtype=np.uint8) * 255
        
        # Apply mask to edges
        edges = cv2.bitwise_and(edges, mask)
        
        # Prepare prompt for texture generation
        prompt = f"high quality {texture_query} texture, detailed fabric pattern, realistic material, 4K, seamless"
        negative_prompt = "blurry, low quality, plain color, cartoon, illustration, watermark, text"
        
        # Generate texture
        generator = torch.Generator(device="cuda").manual_seed(42)
        
        output = stable_diffusion_pipeline(
            prompt,
            image=Image.fromarray(edges),
            negative_prompt=negative_prompt,
            generator=generator,
            num_inference_steps=30,
            controlnet_conditioning_scale=0.8,
            height=height,
            width=width
        ).images[0]
        
        # Save the generated texture
        output.save(output_path)
        print(f"Generated texture saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating texture with Stable Diffusion: {e}")
        return False

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
    4. Determine if the texture should be generated using AI (Stable Diffusion) or searched from Unsplash.

    Respond in the following JSON format:
    {{
        "answer": True/False,
        "clothing_items": [
            {{
                "item": "item_name", 
                "texture_query": "query_for_texture",
                "use_ai_generation": True/False,
                "ai_prompt": "detailed AI prompt for texture generation"
            }},
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

def process_texture_generation(clothing_item, texture_query, use_ai_generation, ai_prompt, texture_file):
    """Process texture generation using either AI or Unsplash"""
    
    # Always try AI generation first if available, regardless of LLM decision
    if STABLE_DIFFUSION_AVAILABLE:
        print(f"Attempting AI texture generation for: {clothing_item}")
        print(f"AI Prompt: {ai_prompt or texture_query}")
        
        # Try AI generation first
        success = generate_texture_with_stable_diffusion(
            texture_file, 
            ai_prompt or texture_query, 
            texture_file
        )
        
        if success:
            print(f"Successfully generated AI texture for: {clothing_item}")
            return True
        else:
            print(f"AI generation failed, falling back to Unsplash")
    
    # Fallback to Unsplash
    print(f"Searching Unsplash for texture: {texture_query}")
    new_texture_url = search_unsplash(texture_query)
    if new_texture_url:
        replace_texture_file(texture_file, new_texture_url)
        print(f"Successfully applied Unsplash texture for: {clothing_item}")
        return True
    else:
        print(f"No suitable texture found on Unsplash for query: {texture_query}")
        return False

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
        use_ai_generation = clothing.get("use_ai_generation", False)
        ai_prompt = clothing.get("ai_prompt", "")

        if not clothing_item or not texture_query:
            print(f"Invalid clothing item or texture query: {clothing}")
            continue

        print(f"Processing Clothing Item: {clothing_item}")
        print(f"Texture Query: {texture_query}")
        print(f"Use AI Generation: {use_ai_generation}")

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

        # Step 4: Process texture generation (AI or Unsplash)
        process_texture_generation(clothing_item, texture_query, use_ai_generation, ai_prompt, texture_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python texture-grabing.py \"<prompt>\"")
        print("Example: python texture-grabing.py \"I want a purple silk texture for the shirt and a denim texture for the pants.\"")
        sys.exit(1)

    user_prompt = sys.argv[1]
    main(user_prompt)