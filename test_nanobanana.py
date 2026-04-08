import asyncio
import os
from google import genai
from google.genai import types

async def test():
    client = genai.Client(api_key='AIzaSyAmfCw2zwB92n4sYU5yNedXPnWghjF_l6U')
    try:
        # Check gemini-2.5-flash-image
        print("Testing gemini-2.5-flash-image...")
        
        # Test generation capability
        # In current google-genai SDK, image generation usually uses generate_images
        # but the -image suffix Gemini models might support specialized tasks.
        
        # We will use generate_images with gemini-2.5-flash-image if it's available as an image model
        print("Models list for 'flash-image':")
        models = client.models.list()
        flash_image_models = [m.name for m in models if 'flash-image' in m.name]
        print(flash_image_models)
        
        if flash_image_models:
             model_id = flash_image_models[0]
             # Try multimodal try-on task
             with open('uploads/selfie.png', 'rb') as f:
                 selfie_part = types.Part.from_bytes(data=f.read(), mime_type='image/png')
             
             # Attempt Virtual Try-On task if supported by the SDK
             # For Gemini-Nano-Banana (Flash Image), the usage often involves generate_content returning an image Part
             # OR using specific task configs.
             
             print(f"Executing VTON task on {model_id}...")
             # Using generate_content but asking for image response
             res = client.models.generate_content(
                 model=model_id,
                 contents=["A person wearing this outfit", selfie_part],
                 # config=types.GenerateContentConfig(response_mime_type="image/jpeg") # Might not be supported
             )
             print(f"Response: {res.text[:100]}")
             if res.candidates and res.candidates[0].content.parts:
                 for part in res.candidates[0].content.parts:
                     if part.inline_data:
                         print("Found inline_data image response!")
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
