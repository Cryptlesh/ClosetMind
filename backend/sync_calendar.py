"""Standalone calendar sync script - run as subprocess to avoid httpx conflicts.
Usage: python sync_calendar.py '[ {"date":"2026-05-01", "title":"Goa Day 1"}, ... ]'
Prints JSON results to stdout.
"""
import sys
import os
import json

def sync_events(events_json_str):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
    
    creds = None
    # Priority 1: token.json file
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar.events'])
    
    # Priority 2: Env Var
    elif os.environ.get("GOOGLE_CALENDAR_TOKEN"):
        token_data = json.loads(os.environ.get("GOOGLE_CALENDAR_TOKEN"))
        creds = Credentials.from_authorized_user_info(token_data, ['https://www.googleapis.com/auth/calendar.events'])

    if not creds:
        return {"error": "No Google Calendar credentials found (token.json or env var)"}

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if os.path.exists(token_path):
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
        else:
            return {"error": "Invalid credentials, cannot refresh."}

    service = build('calendar', 'v3', credentials=creds)
    
    try:
        events = json.loads(events_json_str)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON input: {e}"}

    results = []
    for ev in events:
        event_body = {
            'summary': ev.get('title', 'ClosetMind Event'),
            'description': ev.get('description', 'Planned by ClosetMind'),
            'start': {'date': ev.get('date')},
            'end': {'date': ev.get('date')},
        }
        try:
            created = service.events().insert(calendarId='primary', body=event_body).execute()
            results.append({
                "status": "created",
                "title": ev.get('title'),
                "date": ev.get('date'),
                "link": created.get('htmlLink')
            })
        except Exception as e:
            results.append({
                "status": "error",
                "title": ev.get('title'),
                "date": ev.get('date'),
                "error": str(e)
            })
    
    return {"results": results}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No events JSON provided"}))
        sys.exit(1)
    
    output = sync_events(sys.argv[1])
    print(json.dumps(output))
