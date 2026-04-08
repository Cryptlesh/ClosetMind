from mcp.server import Server
import mcp.types as types
from mcp.server.stdio import stdio_server

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

app = Server("closetmind-calendar")

def get_calendar_service():
    creds = None
    # Use absolute path to ensure backend/token.json is found regardless of cwd
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    token_path = os.path.join(base_dir, "token.json")
    
    # Priority 1: token.json file (Local development)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar.events'])
    
    # Priority 2: Environment variable (Cloud Run / Secret Manager)
    elif os.environ.get("GOOGLE_CALENDAR_TOKEN"):
        import json
        token_data = json.loads(os.environ.get("GOOGLE_CALENDAR_TOKEN"))
        creds = Credentials.from_authorized_user_info(token_data, ['https://www.googleapis.com/auth/calendar.events'])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Only save back to file if it exists (local dev)
            if os.path.exists(token_path):
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
    if creds:
        return build('calendar', 'v3', credentials=creds)
    return None

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "create_calendar_events":
        raise ValueError(f"Unknown tool: {name}")

    service = get_calendar_service()
    if not service:
         return [types.TextContent(type="text", text="Failed to authenticate to Google Calendar")]

    events_data = arguments.get("events", [])
    results = []

    for event_info in events_data:
        date_str = event_info.get("date")
        title = event_info.get("title")
        description = event_info.get("description", "ClosetMind_img.png")
        
        event = {
          'summary': title,
          'description': description,
          'start': {
            'date': date_str,
          },
          'end': {
            'date': date_str,
          },
        }

        try:
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            link = event_result.get('htmlLink')
            results.append(f"Successfully created: {title} on {date_str} -> {link}")
        except Exception as e:
            results.append(f"Error creating {title}: {str(e)}")

    return [types.TextContent(type="text", text="\n".join(results))]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_calendar_events",
            description="Create all-day outfit events on the user's primary Google Calendar.",
            inputSchema={
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "Date of the event in YYYY-MM-DD format. Remember that end date is exclusive for all-day events if sending range, but for single day use same start/end."},
                                "title": {"type": "string", "description": "Title of the calendar event"},
                                "description": {"type": "string", "description": "Body of the event e.g., Outfit URL"}
                            },
                            "required": ["date", "title"]
                        }
                    }
                },
                "required": ["events"]
            }
        )
    ]

def main():
    import asyncio
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            # Pass our server instance to correctly handle standard IO stream
            await app.run(read_stream, write_stream, app.create_initialization_options())
    asyncio.run(run())

if __name__ == "__main__":
    main()
