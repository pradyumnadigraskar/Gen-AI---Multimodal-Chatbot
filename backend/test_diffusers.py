# test_diffusers.py
import torch, io
from diffusers import StableDiffusionPipeline
model_id = "stabilityai/stable-diffusion-2-1"  # small & reliable
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
img = pipe(
    "a queen cat ruleing over world having crown on head , Ultra detailed ",
    num_inference_steps=25,
    guidance_scale=7.5,
    width=768,
    height=512,
).images[0]
img.save("diffusers_test.png")
print("Wrote diffusers_test.png")
