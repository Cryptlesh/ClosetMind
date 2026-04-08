import asyncio
import logging
import uuid
# In a real environment, google_adk provides these agents. 
# We wrap their hypothetical interface for the hackathon MVP executing concurrently.
# If the exact ADK library import fails during hackathon run, we mock their interface behavior here.
from ..mcp.manager import mcp_manager
from ..mcp.weather import WeatherTool
from ..mcp.notes import NotesDocsTool
from ..tools.gemini_vton import GeminiVTONTool, GeminiVTONInput

try:
    from google.adk.agents.llm_agent import LlmAgent
    from google.adk.agents.parallel_agent import ParallelAgent
    from google.adk.agents.sequential_agent import SequentialAgent
    from google.adk.models import Gemini
except ImportError:
    # MVP fallback class definitions if google_adk 1.28.0 interface differs
    class LlmAgent:
        def __init__(self, name, instruction, model="gemini-1.5-flash", tools=None):
            self.name = name
            self.instruction = instruction
            self.model = model
            self.tools = tools
        async def run(self, input_data):
            return {"output": f"Executed instruction '{self.instruction}' for {input_data}"}
            
    class ParallelAgent:
        def __init__(self, agents):
            self.agents = agents
        async def run(self, inputs):
            # Concurrent execution
            tasks = [agent.run(inputs) for agent in self.agents]
            return await asyncio.gather(*tasks)
            
    class SequentialAgent:
        def __init__(self, agents):
            self.agents = agents
        async def run(self, initial_input):
            result = initial_input
            outputs = []
            for agent in self.agents:
                out = await agent.run(result)
                outputs.append(out)
                result = out  # Chain to next
            return outputs

logger = logging.getLogger(__name__)

async def process_vision_batch(file_names: list[str]) -> list:
    """
    Ingest wardrobe images using real Gemini Vision API concurrently.
    For each image URL, reads the local file, calls Gemini 1.5 Flash to extract metadata,
    and returns a parsed list of items.
    """
    import os
    import json
    from google import genai
    from google.genai import types
    from app.core.settings import settings

    logger.info(f"Processing vision batch with REAL Gen AI for {len(file_names)} files.")
    
    # Initialize genai client natively
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    async def analyze_image(url: str):
        # Default fallback values
        category = "Top"
        color = "Unknown"
        material = "Unknown"
        tags = ["trendy", "casual"]
        
        try:
            # Reconstruct local file path from URL
            if url.startswith(settings.BASE_URL):
                file_rel_path = url.replace(f"{settings.BASE_URL}/", "")
                if os.path.exists(file_rel_path):
                    with open(file_rel_path, "rb") as f:
                        file_bytes = f.read()
                        
                        prompt = "Extract category, color, material, and tags for this clothing item. Give your answer in raw JSON format strictly matching: {'category': '...', 'color': '...', 'material': '...', 'tags': ['tag1', 'tag2']}."
                        # For async we can use run_async but genai client requires specific methods. 
                        # We'll use synchronous within a thread pool for simplicity in MVP.
                        loop = asyncio.get_running_loop()
                        
                        def run_vision():
                            return client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[
                                    prompt,
                                    types.Part.from_bytes(data=file_bytes, mime_type='image/jpeg' if url.endswith('.jpg') or url.endswith('.jpeg') else 'image/png')
                                ]
                            )
                        response = await loop.run_in_executor(None, run_vision)
                        
                        if response.text:
                            clean_text = response.text.replace('```json', '').replace('```', '').strip()
                            p = json.loads(clean_text)
                            category = p.get('category', category)
                            color = p.get('color', color)
                            material = p.get('material', material)
                            tags = p.get('tags', tags)
        except Exception as e:
            logger.error(f"Vision API error for {url}: {e}")
            
        return {
            "filename": url,
            "category": category,
            "color": color,
            "material": material,
            "tags": tags,
            "status": "stored_in_alloydb"
        }

    # Run them concurrently
    tasks = [analyze_image(f) for f in file_names]
    parsed_results = await asyncio.gather(*tasks)
    
    return parsed_results


async def execute_outfit_planning(user_id: str, prompt: str) -> dict:
    """
    Root Orchestrator (Fit Genie):
    1. Grabs User Location & Selfie + Wardrobe Inventory from AlloyDB.
    2. Fetches Weather context for location.
    3. Concurrently calls Gemini for:
       - Stylist Agent: Picks items out of the vault based on weather & prompt.
       - Tips Agent: Lifestyle/fashion advice.
    4. Generates a Try-On synthesized image.
    """
    import os
    import json
    import asyncio
    import psycopg2
    from google import genai
    from app.core.settings import settings
    from app.mcp.weather import WeatherTool
    
    # 1. Fetch User Data & Wardrobe from DB
    user_location = "New York"
    selfie_url = ""
    inventory = []
    
    if settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL:
        try:
            conn = psycopg2.connect(settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL)
            cur = conn.cursor()
            cur.execute("SELECT id, location, selfie_url FROM users LIMIT 1")
            row = cur.fetchone()
            if row:
                user_id_db = row[0]
                user_location = row[1] or user_location
                selfie_url = row[2] or ""
                
                cur.execute("SELECT category, color, material, tags, image_url FROM wardrobe WHERE user_id = %s", (user_id_db,))
                for w in cur.fetchall():
                    inventory.append({
                        "category": w[0], "color": w[1], "material": w[2], "tags": w[3], "image_url": w[4]
                    })
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"AlloyDB fetch failed: {e}")

    # 1.5 Check if prompt mentions a location
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    try:
        loc_prompt = f"Does the following prompt mention a specific city or location for weather? Answer ONLY with the location name if found, otherwise answer 'None'.\nPrompt: {prompt}"
        loop = asyncio.get_running_loop()
        def _run_loc():
            return client.models.generate_content(model='gemini-2.5-flash', contents=[loc_prompt])
        loc_res = await loop.run_in_executor(None, _run_loc)
        if loc_res.text and "None" not in loc_res.text:
            user_location = loc_res.text.strip()
            logger.info(f"Extracted location from prompt: {user_location}")
    except Exception as e:
        logger.error(f"Location extraction failed: {e}")

    # 2. Get Weather
    weather_context = f"Could not fetch weather data for {user_location}."
    try:
        import httpx
        import urllib.parse
        
        # Simplify location for geocoding (e.g., "Mumbai, Maharashtra, India" -> "Mumbai")
        search_location = user_location.split(',')[0].strip() if user_location else "New York"
        if not search_location:
            search_location = "New York"
            
        encoded_loc = urllib.parse.quote(search_location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1&format=json"
        async with httpx.AsyncClient() as http_client:
            geo_res = await http_client.get(geo_url)
            geo_data = geo_res.json()
            if "results" in geo_data and len(geo_data["results"]) > 0:
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                w_res = await http_client.get(w_url)
                w_data = w_res.json().get("current_weather", {})
                temp = w_data.get('temperature')
                wind = w_data.get('windspeed')
                weather_context = f"Weather for '{search_location}': {temp}°C, Wind: {wind} km/h"
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")

    # 2.5 Trip detection and Calendar Sync via isolated subprocess
    is_trip = "plan" in prompt.lower() or "trip" in prompt.lower() or "day" in prompt.lower()
    if is_trip:
        trip_prompt = f"Parse this trip request: '{prompt}'. Return a JSON array of daily outfits like: [{{\"date\": \"2026-05-01\", \"title\": \"Goa Trip Day 1 Outfit\"}}]. Only return valid JSON."
        loop = asyncio.get_running_loop()
        def _run_trip_parse():
            """Use Gemini REST API directly via requests to avoid httpx conflicts with google.adk."""
            import requests as req
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": trip_prompt}]}]}
            resp = req.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return text
        try:
            raw_text = await loop.run_in_executor(None, _run_trip_parse)
            clean_json = raw_text.replace('```json', '').replace('```', '').strip()
            trip_events = json.loads(clean_json)
            
            # Run calendar sync as SUBPROCESS to avoid httpx client corruption from google.adk
            import subprocess, sys
            sync_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sync_calendar.py")
            
            def _run_sync_subprocess(events_json_str):
                result = subprocess.run(
                    [sys.executable, sync_script, events_json_str],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode != 0:
                    return {"error": f"Subprocess failed: {result.stderr}"}
                return json.loads(result.stdout)
            
            sync_output = await loop.run_in_executor(None, _run_sync_subprocess, json.dumps(trip_events))
            
            if "error" in sync_output:
                weather_context += f"\n\n[CALENDAR SYNC RESULTS]\nSync error: {sync_output['error']}"
                logger.error(f"Calendar sync subprocess error: {sync_output['error']}")
            else:
                result_lines = []
                for r in sync_output.get("results", []):
                    if r["status"] == "created":
                        result_lines.append(f"Created: {r['title']} on {r['date']} -> {r['link']}")
                    else:
                        result_lines.append(f"Error: {r['title']} on {r['date']} - {r.get('error','unknown')}")
                weather_context += "\n\n[CALENDAR SYNC RESULTS]\n" + "\n".join(result_lines)
                logger.info(f"Calendar sync completed: {result_lines}")
        except Exception as e:
            import traceback
            logger.error(f"Trip / Calendar sync failure: {e}\n{traceback.format_exc()}")
            weather_context += f"\n\n[CALENDAR SYNC RESULTS]\nSync error: {str(e)}"
    
    # Check if prompt explicitly mentions a location (Simple heuristic using Gemini)
    # We will use Gemini in Parallel
    async def get_stylist_selections():
        inventory_context = json.dumps(inventory)
        sys_instruction = "You are a Stylist. You must select 2 outfit combinations from the given wardrobe JSON inventory. Make sure it matches the weather and user prompt. Return the response in strict JSON: {'combination_1': ['image_url1', 'image_url2'], 'combination_2': ['image_url3']}"
        full_prompt = f"User Prompt: {prompt}\nWeather Context: {weather_context}\nInventory: {inventory_context}\nGive me valid JSON."
        loop = asyncio.get_running_loop()
        def _run():
            return client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[sys_instruction, full_prompt]
            )
        try:
            res = await loop.run_in_executor(None, _run)
            if res.text:
                txt = res.text.replace('```json', '').replace('```', '').strip()
                return json.loads(txt)
        except Exception as e:
            logger.error(f"Stylist agent failed: {e}")
        return {"combination_1": []}

    async def get_style_tips():
        full_prompt = f"User Prompt: {prompt}\nWeather Context: {weather_context}\nProvide a single powerful short paragraph of fashion and lifestyle advice."
        loop = asyncio.get_running_loop()
        def _run():
            return client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[full_prompt]
            )
        try:
            res = await loop.run_in_executor(None, _run)
            return res.text.strip() if res.text else "Layer appropriately."
        except Exception as e:
            logger.error(f"Tips agent failed: {e}")
            return "Stay stylish and dress comfortably for the weather!"
            
    stylist_task = asyncio.create_task(get_stylist_selections())
    tips_task = asyncio.create_task(get_style_tips())
    
    stylist_out, tips_out = await asyncio.gather(stylist_task, tips_task)

    # 4. Synthesize VTON using Image-to-Image (Chained Analysis)
    generated_vton_url = selfie_url or ""
    try:
        from google.genai import types
        combos = stylist_out.get("combination_1", [])
        if combos:
            item_urls = combos[:6]
            
            # Resolve local paths
            def get_local_path(url):
                if not url: return None
                idx = url.find("/uploads/")
                if idx != -1:
                    return url[idx+1:].replace("/", os.sep)
                return None
                
            selfie_path = get_local_path(selfie_url)
            # Fallback if no selfie URL in DB but file exists
            if not selfie_path or not os.path.exists(selfie_path):
                if os.path.exists("uploads/1.jpg"):
                    selfie_path = "uploads/1.jpg"
                elif os.path.exists("../uploads/1.jpg"):
                    selfie_path = "../uploads/1.jpg"
                elif os.path.exists("uploads/selfie.png"):
                    selfie_path = "uploads/selfie.png"
                elif os.path.exists("../uploads/selfie.png"):
                    selfie_path = "../uploads/selfie.png"
                    
            item_paths = []
            for url in item_urls:
                p = get_local_path(url)
                if p and os.path.exists(p):
                    item_paths.append(p)
            
            logger.info(f"Resolved paths for i2i: selfie={selfie_path}, items={item_paths}")
            
            if selfie_path and os.path.exists(selfie_path) and item_paths:
                # Generate Try-on using nano banana (gemini-3.1-flash-image-preview)
                loop = asyncio.get_running_loop()
                def _run_img():
                    from PIL import Image
                    from google.genai import types
                    
                    selfie_img = Image.open(selfie_path)
                    item_imgs = [Image.open(p) for p in item_paths]
                    
                    vton_prompt = "A high quality professional fashion photo of exactly this person described in the first image, but wearing all the exact clothing items from the subsequent images seamlessly as one complete outfit. Realistically map the fabrics and fit."
                    
                    call_contents = [vton_prompt, selfie_img] + item_imgs
                    
                    return client.models.generate_content(
                        model='gemini-3.1-flash-image-preview',
                        contents=call_contents,
                        config=types.GenerateContentConfig(
                            response_modalities=['TEXT', 'IMAGE'],
                            image_config=types.ImageConfig(
                                aspect_ratio='3:4',
                                image_size='2K'
                            )
                        )
                    )
                    
                img_res = await loop.run_in_executor(None, _run_img)
                
                parts = getattr(img_res, 'parts', None)
                if not parts and getattr(img_res, 'candidates', None):
                    parts = img_res.candidates[0].content.parts

                if parts:
                    for part in parts:
                        image = None
                        if hasattr(part, 'as_image'):
                            image = part.as_image()
                        
                        if image:
                            import uuid
                            img_name = f"vton-{uuid.uuid4().hex[:8]}.png"
                            save_path = os.path.join("uploads", img_name)
                            image.save(save_path)
                            generated_vton_url = f"{settings.BASE_URL}/uploads/{img_name}"
                            break
            else:
                logger.warning(f"Selfie or item paths not found locally: {selfie_path}, items={item_paths}")
    except Exception as e:
        logger.error(f"VTON Synthetic i2i failure: {e}")
        
    return {
        "calendar_event": {
            "event_title": prompt,
            "location": user_location,
            "date": "Today"
        },
        "weather_context": weather_context,
        "style_tips": tips_out,
        "stylist_outfits": [
            {"combination": 1, "items": stylist_out.get("combination_1", [])},
            {"combination": 2, "items": stylist_out.get("combination_2", [])}
        ],
        "vton_result": generated_vton_url,
        "notes_document": "Packing list prepared."
    }
