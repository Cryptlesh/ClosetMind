import json
with open("test_output.txt", "rb") as f:
    raw = f.read()
try:
    text = raw.decode("utf-8")
except:
    text = raw.decode("utf-16")

json_start = text.index("{")
data = json.loads(text[json_start:])

weather = data["data"]["weather_context"]
if "[CALENDAR SYNC RESULTS]" in weather:
    results = weather.split("[CALENDAR SYNC RESULTS]")[1].strip()
    lines = results.split("\n")
    for line in lines:
        print(line)
    print(f"\nTotal lines: {len(lines)}")
else:
    print("No calendar sync results found")
