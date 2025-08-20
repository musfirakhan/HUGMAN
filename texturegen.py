!pip install diffusers torch opencv-python numpy Pillow transformers accelerate

import cv2
import numpy as np
from PIL import Image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
import torch

# 1. Load the input image and prepare mask
def load_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

# Replace with your image path
input_image = load_image("C:\Users\KHAN\Desktop\assets-mhc\game\RunTheBridge\HUGMAN\data\clothes\crude_bra\CrudeBraDiffuse.jpg")

# 2. Create a mask (example - modify for your specific case)
# This creates a simple rectangular mask - replace with your actual mask
height, width = input_image.shape[:2]
mask = np.zeros((height, width), dtype=np.uint8)
cv2.rectangle(mask, (100, 200), (300, 400), 255, -1)  # Adjust coordinates for your object

# 3. Prepare ControlNet pipeline
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to("cuda")

# 4. Process the image
gray = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY)
edges = cv2.Canny(gray, 100, 200)
edges = cv2.bitwise_and(edges, mask)  # Apply mask to edges

# 5. Generate texture (modify prompt as needed)
prompt = "high quality fabric texture, detailed weave pattern, realistic material, 4K"
negative_prompt = "blurry, low quality, plain color, cartoon, illustration"

generator = torch.Generator(device="cuda").manual_seed(42)  # For reproducibility

output = pipe(
    prompt,
    image=Image.fromarray(edges),
    negative_prompt=negative_prompt,
    generator=generator,
    num_inference_steps=30,
    controlnet_conditioning_scale=0.8,
    height=height,
    width=width
).images[0]

# 6. Blend with original image
output_np = np.array(output)
background = input_image.copy()
background[mask != 0] = output_np[mask != 0]  # Only keep generated area
final_output = Image.fromarray(background)

# 7. Save results
Image.fromarray(edges).save("edges.png")
final_output.save("textured_output.png")
final_output.show()