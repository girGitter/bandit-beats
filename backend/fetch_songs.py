import urllib.request
import json
import urllib.parse
import os

songs_to_fetch = [
    {
        "query": "Blinding Lights The Weeknd",
        "genre": "Synthwave", "bpm": 171,
        "tags": ["energetic", "night", "gym"],
        "contexts": {"mood": ["energetic"], "activity": ["gym"], "time": ["night", "evening"]}
    },
    {
        "query": "Cruel Summer Taylor Swift",
        "genre": "Pop", "bpm": 170,
        "tags": ["happy", "summer", "morning"],
        "contexts": {"mood": ["happy"], "activity": ["relax", "gym"], "time": ["morning", "evening"]}
    },
    {
        "query": "God's Plan Drake",
        "genre": "Hip Hop", "bpm": 77,
        "tags": ["hype", "gym"],
        "contexts": {"mood": ["energetic"], "activity": ["gym"], "time": ["evening", "night"]}
    },
    {
        "query": "Someone Like You Adele",
        "genre": "Pop/Soul", "bpm": 67,
        "tags": ["sad", "calm"],
        "contexts": {"mood": ["sad"], "activity": ["relax", "study"], "time": ["night", "evening"]}
    },
    {
        "query": "Lose Yourself Eminem",
        "genre": "Rap", "bpm": 171,
        "tags": ["gym", "aggressive"],
        "contexts": {"mood": ["energetic"], "activity": ["gym"], "time": ["morning", "evening"]}
    },
    {
        "query": "As It Was Harry Styles",
        "genre": "Indie Pop", "bpm": 174,
        "tags": ["happy", "upbeat"],
        "contexts": {"mood": ["happy"], "activity": ["relax", "study"], "time": ["morning"]}
    },
    {
        "query": "Levitating Dua Lipa",
        "genre": "Dance Pop", "bpm": 103,
        "tags": ["dance", "party", "energetic"],
        "contexts": {"mood": ["happy", "energetic"], "activity": ["gym"], "time": ["night"]}
    },
    {
        "query": "Good Days SZA",
        "genre": "R&B", "bpm": 121,
        "tags": ["calm", "focus", "study"],
        "contexts": {"mood": ["sad", "happy"], "activity": ["study", "relax"], "time": ["morning", "afternoon"]}
    },
    {
        "query": "Sweater Weather The Neighbourhood",
        "genre": "Alt Indie", "bpm": 124,
        "tags": ["sad", "chill", "night"],
        "contexts": {"mood": ["sad"], "activity": ["relax", "study"], "time": ["night", "evening"]}
    },
    {
        "query": "Sunflower Post Malone",
        "genre": "Pop Rap", "bpm": 90,
        "tags": ["happy", "chill"],
        "contexts": {"mood": ["happy"], "activity": ["relax", "study"], "time": ["morning", "evening"]}
    }
]

results = []

for i, item in enumerate(songs_to_fetch):
    query = urllib.parse.quote(item["query"])
    url = f"https://itunes.apple.com/search?term={query}&limit=1&entity=song"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if data["resultCount"] > 0:
                track = data["results"][0]
                song = {
                    "id": f"s{i+1:03d}",
                    "title": track.get("trackName", item["query"]),
                    "artist": track.get("artistName", "Unknown Artist"),
                    "genre": item["genre"],
                    "bpm": item["bpm"],
                    "tags": item["tags"],
                    "preview_url": track.get("previewUrl", ""),
                    "preferred_contexts": item["contexts"]
                }
                results.append(song)
            else:
                print(f"Not found: {item['query']}")
    except Exception as e:
        print(f"Error fetching {item['query']}: {e}")

# Save one level up in data/songs.json since we are running in backend/
os.makedirs("../data", exist_ok=True)
with open("../data/songs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Successfully updated ../data/songs.json")
