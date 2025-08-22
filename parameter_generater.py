"""
HUGMAN Parameter Generator
=========================

Author: Musfira Aslam
Email: musfiraaslam3@gmail.com
GitHub: https://github.com/musfirakhan

Description:
    This script generates character parameters for HUGMAN using LLM and fashion model.
    It converts text descriptions into detailed character specifications including
    physical attributes, clothing, accessories, and export settings.

Version: 1.0.0
Last Updated: 2025
"""

import ollama
import json
import os
import sys
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from fuzzywuzzy import process


fashion_model_path = "fashionmodel_path"
ollama_model = "llama3.2"

# Load your fashion model
fashion_tokenizer = AutoTokenizer.from_pretrained(fashion_model_path)
fashion_model = AutoModelForCausalLM.from_pretrained(fashion_model_path)
fashion_gen = pipeline("text-generation", model=fashion_model, tokenizer=fashion_tokenizer)

# Load Ollama client
ollama_client = ollama.Client()
CLOTHES_FOLDERS = {
    "beach_poncho_rain_slicker",
    "big_desert_poncho",
    "black_laceup",
    "black_slipons",
    "blue_sneakers",
    "body_armor_shoulder_holster",
    "brown_leather",
    "cargo_pants",
    "celtic_jewelled_headdress",
    "celtic_princess1",
    "celtic_summer_skirt_and_bodice",
    "combat_boots",
    "crude_bra",
    "crude_female_t_shirt",
    "crude_female_underwear",
    "crude_hat",
    "crude_high_socks",
    "crude_leggings",
    "crude_loose_pants",
    "crude_low_socks",
    "crude_ski_mask",
    "crude_swimsuit",
    "crude_t_shirt_female",
    "cutoff_t_shirt",
    "deathnote_t_shirt",
    "fedora01",
    "female_casualsuit01",
    "female_casualsuit02",
    "female_elegantsuit01",
    "female_fingernails",
    "female_sportsuit01",
    "genie_one",
    "gi_one",
    "heart_shirt",
    "hermitess_one",
    "kiki_glasses",
    "leather_shoes",
    "loosed_t_shirt",
    "m_opticals01",
    "male_casualsuit01",
    "male_casualsuit02",
    "male_casualsuit03",
    "male_casualsuit04",
    "male_casualsuit05",
    "male_casualsuit06",
    "male_crude_t_shirt",
    "male_elegantsuit01",
    "male_polo_shirt",
    "male_worksuit01",
    "military_poncho_hood_up",
    "minoan_slave_one",
    "nose_piercing",
    "pink_fuzzy_bathrobe_with_pink_clogs",
    "renaissance_oval_veil_and_wimple",
    "sari_one",
    "scarf",
    "slave_girl_metal_bra",
    "slave_outfit",
    "sleeveless_shirt",
    "spartan_gaunlet_gloves",
    "spartan_warrior_greves",
    "spartan_warrior_woman",
    "sport_sunglasses",
    "t_shirt",
    "victorias_celtic_secret_one",
    "white_sneakers"
}

SHOES_FOLDERS = {
    "black_laceup",
    "black_slipons",
    "blue_sneakers",
    "brown_leather",
    "combat_boots",
    "leather_shoes",
    "white_sneakers"
}

HAIR_FOLDERS = {
    "afro01",
    "afro_hair_ponytail",
    "afro_ponytail_slick_down",
    "atlantean_one",
    "blondwithheadband",
    "bob01",
    "bob02",
    "braid01",
    "braid_strands",
    "brown_hair_with_bun_and_red_velvet_tie",
    "brunhilde_nibelungenlied",
    "dreads_with_taper_fade",
    "four_strand_braid",
    "french_bob_blonde",
    "hair_male_half_bald",
    "hair_male_spiky",
    "jade_hair",
    "junglebookhair",
    "littleright_hair_bobcut",
    "long01",
    "male_short_hair",
    "mermaid_seaweed_hair_and_dolphin_tail",
    "messy_bun",
    "minoan_hairdo_one",
    "ponytail01",
    "ponytail02",
    "reverse_french_braid_bun_01_variation",
    "short01",
    "short02",
    "short03",
    "short04",
    "sun_king_courtesan_one",
    "twintails",
    "two_braided_cornrows_female",
    "wig_bun_blonde_female_braids"
}


def get_fashion_fields(description):
    prompt = f"<|user|>\n{description}\n<|assistant|>\n"
    result = fashion_gen(prompt, max_length=200, do_sample=True, top_p=0.9, temperature=0.8)[0]["generated_text"]
    try:
        # Extract only the JSON part
        json_part = result.split("<|assistant|>")[-1].strip()
        json_start = json_part.find("{")
        json_end = json_part.rfind("}")
        if json_start != -1 and json_end != -1:
            json_str = json_part[json_start:json_end+1]
            return json.loads(json_str)
        else:
            print("Fashion model output did not contain valid JSON.")
    except Exception as e:
        print("Error parsing fashion model output:", e)
    return None


def clean_llm_json_response(json_str):
    json_str = re.sub(r"^```[a-zA-Z]*\n?", "", json_str.strip())
    json_str = re.sub(r"```$", "", json_str.strip())
    start = json_str.find('{')
    end = json_str.rfind('}')
    return json_str[start:end+1] if start != -1 and end != -1 else json_str

def find_closest_match(query, choices, cutoff=80):
    """Finds the closest matching item using fuzzy string matching."""
    result = process.extractOne(query, choices, score_cutoff=cutoff)
    return result[0] if result else None

def generate_core_attributes(description, fashion_fields):
    clothes = fashion_fields.get("clothes", [])
    shoes = fashion_fields.get("shoes", "")
    hair = fashion_fields.get("hair", "")
    print("Clothes", clothes)
    print("Shoes", shoes)
    print("hair", hair)
    valid_clothes = []
    invalid_clothes = []
    
    for item in clothes:
        if item in CLOTHES_FOLDERS:
            valid_clothes.append(item)
        else:
            invalid_clothes.append(item)

    invalid_shoes = shoes if shoes and shoes not in SHOES_FOLDERS else ""

    invalid_hair = hair if hair and hair not in HAIR_FOLDERS else ""

    if invalid_clothes:
        
        for i, item in enumerate(clothes):
            closest_match = find_closest_match(item, CLOTHES_FOLDERS)
            if closest_match:
                clothes[i] = closest_match

    if invalid_shoes:
        closest_shoes = find_closest_match(invalid_shoes, SHOES_FOLDERS)
        if closest_shoes:
            shoes = closest_shoes

    if invalid_hair:
        closest_hair = find_closest_match(hair, HAIR_FOLDERS)
        if closest_hair:

            hair = closest_hair

    prompt = f"""You are generating character core attributes for a 3D avatar.
    Description: "{description}"
    These items were already chosen:
    - clothes: {clothes}
    - shoes: {shoes}
    - hair: {hair}
    Now using the description, generate the following attributes:
    - name: A suitable name for the character (generate one word name only, no capital letters)
    - gender: 0 for female, 1 for male
    - age: float (0.3 for young, 0.6 for middle-aged, 0.9 for old)
    - weight: float from 0 to 1 (0 = very skinny, 1 = obese)
    - muscle: float from 0 to 1 (0 = weak, 1 = very muscular; average = 0.5)
    - height: float from 0 to 1 (0 = very short, 1 = very tall; average = 0.5)
    - caucasian: float from 0 to 1 
    - african: float from 0 to 1
    - asian: float from 0 to 1

            

    ## Select skin  (match gender + ethnicity + age):
    ["young_african_female", "young_african_male", "young_asian_female", "young_asian_male", "young_caucasian_female", "young_caucasian_male",
    "middleage_african_female", "middleage_african_male", "middleage_asian_female", "middleage_asian_male", "middleage_caucasian_female", "middleage_caucasian_male",
    "old_african_female", "old_african_male", "old_asian_female", "old_asian_male", "old_caucasian_female", "old_caucasian_male"]

   
    ## Select eyebrow (choose one):
    [
    "eyebrow001",  # for female characters — thin, soft, gentle (youthful, delicate look)
    "eyebrow002",  # for female characters — arched, expressive (elegant or royal look)
    "eyebrow003",  # for male characters — thick, straight, stoic (strong, emotionless types)
    "eyebrow004",  # for male characters — medium curve, thoughtful (balanced, intellectual)
    "eyebrow005",  # for male characters — arched, strong, alert (sharp, heroic look)
    "eyebrow006",  # for female characters — slim, curved, mystical (fantasy, mysterious look)
    "eyebrow007",  # for male characters — bold, straight, stern (intense or warrior types)
    "eyebrow008",  # for female characters — light arch, youthful (teen, playful types)
    "eyebrow009",  # for male characters — defined, straight, focused (serious or focused)
    "eyebrow010",  # for male characters — soft curve, laid-back (chill, casual guys)
    "eyebrow011",  # for male characters — sharply arched, dramatic (villains, expressive types)
    "eyebrow012"   # for male characters — dense, straight, rugged (tough, outdoorsy types)
    ]




     ## Select eyelash (choose one):
    [
    "eyelashes01",  # for male characters — short, subtle (natural, minimal look)
    "eyelashes02",  # for female characters — medium curl (casual, everyday style)
    "eyelashes03",  # for female characters — thick and long (stylish, expressive look)
    "eyelashes04"   # for female characters — thicker and longer (glamorous, dramatic look)
    ]



     ## OTHER FIELDS:

    - eyes: "low-poly"
    - teeth: "teeth_base"
    - tongue: "tongue01"
    - skeleton: "game_engine"
    - export_path: "output/[generated_name].fbx"  
    (replace [generated_name] with lowercase, no spaces)

        



    ## OUTPUT FORMAT (STRICT):

    - Return valid JSON ONLY
    - Follow this structure:

    {{
    "name": "generated_name",
    "gender": value selected above for gender,
    "age": value selected above for age,
    "weight":value selected above for weight,
    "muscle":value selected above for muscle,
    "height": value selected above for height,
    "caucasian": value selected,
    "african": value selected above,
    "asian": value selected above,
    "skin": "selected_skin",
    "clothes": ["item1", "item2", ...],
    "shoes": "selected_shoes",
    "hair": "selected_hair",
    "eyes": "low-poly",
    "eyebrow": "selected_eyebrow",
    "eyelash": "selected_eyelash",
    "teeth": "teeth_base",
    "tongue": "tongue01",
    "skeleton": "game_engine",
    "export_path": "output/generated_name.fbx"
    }}

    ##  FINAL INSTRUCTION:

    You MUST return ONLY valid JSON — without any markdown, explanations, or comments.  
    NO extra text before or after.  
    Just the JSON object, STARTING AND ENDING WITH CURLY BRACES PLEASE.

    """


    response = ollama_client.generate(model=ollama_model, prompt=prompt)
    cleaned = clean_llm_json_response(response.response)
    return cleaned




def save_character_json(character_data, filename="character1.json"):
    if character_data:
        # Create generated_characters directory if it doesn't exist
        os.makedirs("generated_characters", exist_ok=True)
        filepath = os.path.join("generated_characters", filename)
        
        with open(filepath, 'w') as f:
            json.dump(character_data, f, indent=4)
        print(f"Character data saved to {filepath}")
    else:
        print("No character data to save")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parameter_generator.py \"description here\"")
        sys.exit(1)

    description = sys.argv[1]
    fashion_data = get_fashion_fields(description)
    if not fashion_data:
        print("Failed to get fashion output.")
        sys.exit(1)


    core_json_str = generate_core_attributes(description, fashion_data)
    if not core_json_str.startswith("{"):
        core_json_str = "{" + core_json_str
    if not core_json_str.endswith("}"):
        core_json_str = core_json_str + "}"

    try:
        core_data = json.loads(core_json_str)
        save_character_json(core_data)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON from Ollama response:", e)
        print("Raw (corrected) response was:\n", core_json_str)


