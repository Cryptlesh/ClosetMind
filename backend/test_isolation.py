"""Reproduce the exact coordinator flow to find where 'client closed' happens."""
import asyncio
import os
import json
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

async def test_flow():
    from app.core.settings import settings
    from google import genai
    import httpx
    
    log("=== Step 1: Create genai.Client ===")
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    log(f"  genai client created: {type(client)}")
    
    log("=== Step 2: Use genai client in executor (location extraction) ===")
    loop = asyncio.get_running_loop()
    def _run_loc():
        return client.models.generate_content(model='gemini-2.5-flash', contents=["Say hello in one word."])
    try:
        res = await loop.run_in_executor(None, _run_loc)
        log(f"  Location call OK: {res.text.strip()[:50]}")
    except Exception as e:
        log(f"  Location call FAILED: {e}")

    log("=== Step 3: httpx.AsyncClient for weather ===")
    try:
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get("https://geocoding-api.open-meteo.com/v1/search?name=Goa&count=1&format=json")
            log(f"  Weather call OK: status={r.status_code}")
    except Exception as e:
        log(f"  Weather call FAILED: {e}")

    log("=== Step 4: _run_trip with NEW genai client in executor ===")
    def _run_trip():
        import google.genai as genai_sync
        c = genai_sync.Client(api_key=settings.GEMINI_API_KEY)
        result = c.models.generate_content(model='gemini-2.5-flash', contents=["Return JSON: [{\"date\": \"2026-05-01\", \"title\": \"Test\"}]"])
        return result
    try:
        res = await loop.run_in_executor(None, _run_trip)
        log(f"  Trip parse OK: {res.text.strip()[:80]}")
    except Exception as e:
        import traceback
        log(f"  Trip parse FAILED: {e}")
        log(traceback.format_exc())

    log("=== Step 5: Calendar sync in executor ===")
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    
    def _sync_cal():
        token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar.events'])
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        service = build('calendar', 'v3', credentials=creds)
        events = service.events().list(calendarId='primary', maxResults=1).execute()
        return f"OK - {len(events.get('items', []))} events"
    try:
        r = await loop.run_in_executor(None, _sync_cal)
        log(f"  Calendar sync OK: {r}")
    except Exception as e:
        import traceback
        log(f"  Calendar sync FAILED: {e}")
        log(traceback.format_exc())

    log("=== Step 6: Use original genai client again (stylist) ===")
    def _run_stylist():
        return client.models.generate_content(model='gemini-2.5-flash', contents=["Say goodbye in one word."])
    try:
        res = await loop.run_in_executor(None, _run_stylist)
        log(f"  Stylist call OK: {res.text.strip()[:50]}")
    except Exception as e:
        import traceback
        log(f"  Stylist call FAILED: {e}")
        log(traceback.format_exc())

    log("=== ALL STEPS COMPLETE ===")

asyncio.run(test_flow())

with open("test_isolation_results.log", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
print("Results written to test_isolation_results.log")
