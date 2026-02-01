import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "anime_index.csv")


def load_anime_index():
    anime_index = {}

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("enabled") != "1":
                continue

            aid = int(row["anidb_aid"])
            anime_index[aid] = {
                "title": row["title"],
                "anilist": int(row["anilist_id"]),
            }

    return anime_index


ANIME_INDEX = load_anime_index()
WHITELIST_ANIDB = set(ANIME_INDEX.keys())
