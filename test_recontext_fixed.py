import asyncio
import os
from google import genai
from google.genai import types

async def test():
    client = genai.Client(api_key='AIzaSyAmfCw2zwB92n4sYU5yNedXPnWghjF_l6U')
    try:
        model_id = 'models/gemini-2.5-flash-image'
        print(f"Testing recontext_image with {model_id}...")
        
        # Load selfie
        selfie_path = 'uploads/1.jpg'
        with open(selfie_path, 'rb') as f:
            selfie_bytes = f.read()
            
        # RecontextImageSource takes an image Part
        source = types.Image.from_bytes(data=selfie_bytes)
        
        # Test if it works
        res = client.models.recontext_image(
            model=model_id,
            source=source,
            prompt="A person wearing a blue marathon jacket",
            config=types.RecontextImageConfig(
                number_of_images=1
            )
        )
        if res.generated_images:
            print(f"Success! Generated {len(res.generated_images)} images.")
            
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
