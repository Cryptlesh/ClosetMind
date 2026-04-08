import asyncio
from google import genai

async def test():
    client = genai.Client(api_key='AIzaSyAmfCw2zwB92n4sYU5yNedXPnWghjF_l6U')
    try:
        model_id = 'models/gemini-2.5-flash-image'
        print(f"Testing generate_images with {model_id}...")
        res = client.models.generate_images(
            model=model_id,
            prompt='a stylish person',
        )
        if res.generated_images:
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
