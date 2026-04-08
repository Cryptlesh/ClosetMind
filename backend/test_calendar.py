"""Quick test: verify Google Calendar API credentials and create a test event."""
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
print(f"Token path: {token_path}")
print(f"Exists: {os.path.exists(token_path)}")

creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar.events'])
print(f"Valid: {creds.valid}, Expired: {creds.expired}")

if not creds.valid:
    if creds.expired and creds.refresh_token:
        print("Refreshing token...")
        creds.refresh(Request())
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        print("Token refreshed and saved.")
    else:
        print("ERROR: Credentials invalid and cannot refresh!")
        exit(1)

service = build('calendar', 'v3', credentials=creds)
print("Calendar service created OK")

# Create a test event
event_body = {
    'summary': 'ClosetMind Test Event',
    'description': 'Auto-test from ClosetMind backend',
    'start': {'date': '2026-04-15'},
    'end': {'date': '2026-04-15'},
}
result = service.events().insert(calendarId='primary', body=event_body).execute()
print(f"SUCCESS! Event created: {result.get('htmlLink')}")

# Clean up - delete test event
service.events().delete(calendarId='primary', eventId=result['id']).execute()
print("Test event cleaned up (deleted).")
