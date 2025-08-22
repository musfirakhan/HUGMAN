import os
import sys
import json
import requests
from io import BytesIO
from PIL import Image
import ollama
import re

# Help PyTorch reduce fragmentation on CUDA
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

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
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")
            
            controlnet_model = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            
            stable_diffusion_pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet_model,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            ).to(device)
            
            # Reduce VRAM usage
            try:
                stable_diffusion_pipeline.enable_attention_slicing()
                stable_diffusion_pipeline.enable_vae_slicing()
                stable_diffusion_pipeline.enable_vae_tiling()
                # Prefer CPU/offload and xFormers if available
                stable_diffusion_pipeline.enable_sequential_cpu_offload()
                try:
                    stable_diffusion_pipeline.enable_xformers_memory_efficient_attention()
                except Exception:
                    pass
            except Exception:
                pass
            
            print(f"Stable Diffusion initialized successfully on {device}!")
        except Exception as e:
            print(f"Error initializing Stable Diffusion: {e}")
            return False
    return True

# Add a better prompt builder
def build_prompts(texture_query: str):
	base_prompt = (
		f"{texture_query},  fabric/material texture "
		"micro-detail, high-frequency detail, neutral studio lighting, photorealistic, 4k, "
		"no logos, no text, no watermark"
	)
	negative_prompt = (
		"blurry, lowres, noisy, artifacts, watermark, text, logo, seams, stitches, wrinkles, folds, perspective, "
		"shadows, people, hands, 3d render, cartoon, illustration, stylized"
	)
	return base_prompt, negative_prompt

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
        
        # Auto-Canny edge detection (no masking)
        gray = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY)
        v = np.median(gray)
        lower = int(max(0, (1.0 - 0.33) * v))
        upper = int(min(255, (1.0 + 0.33) * v))
        edges = cv2.Canny(gray, lower, upper)
        # Thicken edges to strengthen ControlNet conditioning
        try:
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
        except Exception:
            pass
        
        # Build prompts
        prompt, negative_prompt = build_prompts(texture_query)
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Downscale generation to reduce VRAM usage
        target_max = 384  # reduce for 8GB cards; try 256 if OOM persists
        scale = min(target_max / max(height, width), 1.0)
        gen_h = int(round(height * scale))
        gen_w = int(round(width * scale))
        gen_h = max(256, (gen_h // 8) * 8)
        gen_w = max(256, (gen_w // 8) * 8)
        
        # Resize control image for generation and ensure RGB
        control_img = Image.fromarray(edges).convert("RGB").resize((gen_w, gen_h), Image.BICUBIC)
        
        # Generate texture
        generator = torch.Generator(device=device).manual_seed(42)
        output = stable_diffusion_pipeline(
            prompt,
            image=control_img,
            negative_prompt=negative_prompt,
            generator=generator,
            num_inference_steps=20,
            guidance_scale=5.5,
            controlnet_conditioning_scale=0.9,
            height=gen_h,
            width=gen_w
        ).images[0]
        
        # Upscale back to original texture size
        output = output.resize((width, height), Image.BICUBIC)
        
        # Save the generated texture
        output.save(output_path)
        print(f"Generated texture saved to: {output_path}")
        
        # Free VRAM if on CUDA
        try:
            if device == "cuda":
                torch.cuda.empty_cache()
        except Exception:
            pass
        
        return True
        
    except Exception as e:
        print(f"Error generating texture with Stable Diffusion: {e}")
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
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

    if not llama_result:
        print("LLaMA response is incomplete.")
        return
        
    # Check if we have clothing items to process, regardless of the "answer" field
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