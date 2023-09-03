import io
from PIL import Image
import base64

def b64_img(image: Image):
        """Converts an image to base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = 'data:image/png;base64,' + str(base64.b64encode(buffered.getvalue()), 'utf-8')
        return img_base64

def generate_payload(file, prompt="", negative_prompt="", steps=12, seed=-1, denoising_strength=0.3, cfg_scale=7):
        """Generates the payload for the API call"""
        try:
            image = Image.open(file)
        except IOError:
            return None

        payload = {
            "init_images": [
                b64_img(image)
            ],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "width": image.width,
            "height": image.height,
            "seed": seed,
            "cfg_scale": cfg_scale,
            "denoising_strength": denoising_strength,
            "sampler_index": "Euler a",
            "controlnet_units":[
                {
                    "module": "canny",
                    "model": "control_canny-fp16 [e3fe7712]",
                }
            ]

        }

        return payload


