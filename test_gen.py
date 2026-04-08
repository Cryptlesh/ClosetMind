import asyncio
from google import genai
from google.genai import types

async def test_gen():
    client = genai.Client(api_key='AIzaSyAmfCw2zwB92n4sYU5yNedXPnWghjF_l6U')
    try:
        print("Checking gemini-2.5-flash-image capabilities...")
        # Most Gemini Flash models are for analysis, but the -image suffix might be special.
        # However, Imagen 4 is the standard tool for generation.
        
        # We will use the approach of:
        # 1. Use Gemini to describe the person + outfit.
        # 2. Use Imagen 4 to generate.
        
        # But wait, the user said "i-2i API call".
        # Let's try to pass images to edit_image using imagen-4.0-generate-001 anyway.
        
        with open('uploads/selfie.png', 'rb') as f:
            selfie_bytes = f.read()
            
        print("Calling generate_images with a prompt derived from selfie...")
        # Since I can't find a dedicated i2i model for this key, 
        # I'll use Gemini to turn the images into a high-fidelity prompt.
        
        # BUT, I'll try recontext_image with source and prompt.
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_gen())
