import os
import asyncio
from google import genai
from google.genai import types

async def test_recontext():
    client = genai.Client(api_key='AIzaSyAmfCw2zwB92n4sYU5yNedXPnWghjF_l6U')
    try:
        # Load selfie
        with open('uploads/selfie.png', 'rb') as f:
            selfie_bytes = f.read()
            
        # For item, just use selfie for testing or find an item
        item_path = 'uploads/20358750-02-FT-XL.jpg'
        if not os.path.exists(item_path):
            with open('uploads/selfie.png', 'rb') as f:
                item_bytes = f.read()
        else:
            with open(item_path, 'rb') as f:
                item_bytes = f.read()
        
        # Trying a simple generate_images with a more complex prompt derived from images
        # OR check if edit_image works with the generate model (sometimes they are multi-task)
        
        print("Testing recontext_image...")
        # recontext_image usually takes a base image and a prompt or more images.
        # signature check:
        import inspect
        print(f"Signature: {inspect.signature(client.models.recontext_image)}")
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_recontext())
