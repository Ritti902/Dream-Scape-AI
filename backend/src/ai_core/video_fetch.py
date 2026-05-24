import requests
import uuid
import os

PEXELS_API_KEY = "pUEWPc9DMZ47hv0QJcIutbe9S561YFaYH1oiyK8PYrHrlV7QukCVM46H"

OUTPUT_DIR = "outputs/temp_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_video_from_pexels(query):
    try:
        url = "https://api.pexels.com/videos/search"

        headers = {
            "Authorization": PEXELS_API_KEY
        }

        params = {
            "query": query,
            "per_page": 1
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # ❗ safety check
        if "videos" not in data or len(data["videos"]) == 0:
            raise Exception("No video found for query")

        video_url = data["videos"][0]["video_files"][0]["link"]

        # 🔥 UNIQUE NAME (NO REPLACE ISSUE)
        video_path = os.path.join(
            OUTPUT_DIR,
            f"temp_{uuid.uuid4().hex[:8]}.mp4"
        )

        video_data = requests.get(video_url).content

        with open(video_path, "wb") as f:
            f.write(video_data)

        return video_path

    except Exception as e:
        print(f"❌ Pexels video fetch failed: {e}")
        return None