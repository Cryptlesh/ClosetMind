import asyncio
from google import genai
from google.genai import types

async def test():
    client = genai.Client(api_key='AIzaSyAmfCw2zwB92n4sYU5yNedXPnWghjF_l6U')
    try:
        model_id = 'models/gemini-2.5-flash-image'
        print(f"Testing recontext_image with {model_id}...")
        
        with open('uploads/selfie.png', 'rb') as f:
            selfie_bytes = f.read()
            
        source = types.RecontextImageSource(
             image=types.Image.from_bytes(data=selfie_bytes)
        )
        
        # Test if it works
        res = client.models.recontext_image(
            model=model_id,
            source=source,
            prompt="A person wearing a blue jacket",
            config=types.RecontextImageConfig(
                number_of_images=1
            )
        )
        if res.generated_images:
            print("Successfully generated image with recontext_image!")
            
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
