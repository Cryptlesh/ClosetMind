"""Direct test of the trip planning flow - writes full output to file."""
import requests
import json

resp = requests.post(
    'http://localhost:8000/api/v1/agents/plan-outfits',
    json={'prompt': 'Plan a 3 day trip to Goa starting May 1st', 'user_id': 'user_123'},
    timeout=120
)

data = resp.json()

with open('test_output.txt', 'w') as f:
    f.write(f"Status: {resp.status_code}\n\n")
    f.write(json.dumps(data, indent=2))

print(f"Status: {resp.status_code}")
print("Full output written to test_output.txt")
