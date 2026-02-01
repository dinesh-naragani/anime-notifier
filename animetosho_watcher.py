#!/usr/bin/env python3
import os
import sys
import json
import time
import tempfile
import socket
import requests
from datetime import datetime, timezone, timedelta

# ==================================================
# FORCE IPV4 (Termux / mobile fix)
# ==================================================

_original_getaddrinfo = socket.getaddrinfo
def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_only_getaddrinfo

# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTIFIED_FILE = os.path.join(BASE_DIR, "notified_episodes_engine.txt")
# ==================================================
# CONFIG
# ==================================================

ANIMETOSHO_JSON = "https://feed.animetosho.org/json"

DISCORD_MAGNET_WEBHOOK = os.getenv("DISCORD_MAGNET_WEBHOOK")
DISCORD_TORRENT_WEBHOOK = os.getenv("DISCORD_TORRENT_WEBHOOK")

DISCORD_TEST_MAGNET_WEBHOOK = os.getenv("DISCORD_TEST_MAGNET_WEBHOOK")
DISCORD_TEST_TORRENT_WEBHOOK = os.getenv("DISCORD_TEST_TORRENT_WEBHOOK")

# ==================================================
# 🔒 LOCKED IDENTITY (SOURCE OF TRUTH)
# ==================================================

ANIME_INDEX = {
    18886: {"title": "Frieren",           "anilist": 182255},
    18363: {"title": "Jujutsu Kaisen",    "anilist": 172463},
    18742: {"title": "Fire Force",        "anilist": 179062},
    18901: {"title": "Oshi no Ko",         "anilist": 182587},
    19071: {"title": "MF Ghost",           "anilist": 185753},
    18090: {"title": "Hell’s Paradise",    "anilist": 166613},
}

WHITELIST_ANIDB = set(ANIME_INDEX.keys())

# ==================================================
# STATE
# ==================================================

def load_set(path):
    if os.path.exists(path):
        return set(open(path).read().splitlines())
    return set()

def save_set(path, data):
    with open(path, "w") as f:
        f.write("\n".join(sorted(data)))

# ==================================================
# CLASSIFICATION
# ==================================================

def classify(title):
    t = title.upper()
    if "1080P" not in t:
        return None
    if "H.265" in t or "X265" in t:
        return "H265"
    if t.startswith("[SUBSPLEASE]") or t.startswith("[ERAI-RAWS]"):
        return "H264"
    return None

def extract_links(entry):
    return entry.get("magnet_uri"), entry.get("torrent_url")

def torrent_filename(name, codec):
    return f"{name.replace(' ', '.')}.{codec}.torrent"

# ==================================================
# ANILIST METADATA (MEDIA ID LOCKED)
# ==================================================

ANILIST_IMAGE_QUERY = """
query ($id: Int) {
  Media(id: $id) {
    coverImage {
      extraLarge
    }
  }
}
"""

_METADATA_CACHE = {}

def resolve_metadata(anidb_aid):
    if anidb_aid in _METADATA_CACHE:
        return _METADATA_CACHE[anidb_aid]

    anilist_id = ANIME_INDEX[anidb_aid]["anilist"]

    r = requests.post(
        "https://graphql.anilist.co",
        json={
            "query": ANILIST_IMAGE_QUERY,
            "variables": {"id": anilist_id},
        },
        timeout=20,
    )
    r.raise_for_status()

    image = r.json()["data"]["Media"]["coverImage"]["extraLarge"]
    meta = {"image": image}
    _METADATA_CACHE[anidb_aid] = meta
    return meta

# ==================================================
# DISCORD
# ==================================================

def send_release(entry, aid, codec, image, magnet_wh, torrent_wh):
    title = ANIME_INDEX[aid]["title"]
    magnet, torrent = extract_links(entry)

    embed = {
        "title": title,
        "description": codec,
        "url": entry["link"],
        "image": {"url": image},
    }

    if magnet:
        requests.post(magnet_wh, json={"embeds": [embed]}, timeout=15)
        requests.post(
            magnet_wh,
            json={"content": f"```{magnet}```"},
            timeout=15,
        )

    if torrent:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            r = requests.get(torrent, stream=True, timeout=30)
            for c in r.iter_content(8192):
                tmp.write(c)
            path = tmp.name

        r = requests.post(
            f"{torrent_wh}?wait=true",
            json={"embeds": [embed]},
            timeout=15,
        )
        mid = r.json()["id"]

        with open(path, "rb") as f:
            requests.post(
                torrent_wh,
                files={
                    "file": (
                        torrent_filename(title, codec),
                        f,
                        "application/x-bittorrent",
                    )
                },
                data={"payload_json": json.dumps({
                    "message_reference": {"message_id": mid}
                })},
                timeout=30,
            )

        os.remove(path)

# ==================================================
# MAIN
# ==================================================

def run(test=False):
    print(f"🔎 Fetching AnimeTosho JSON (test={test})")
    feed = requests.get(ANIMETOSHO_JSON, timeout=30).json()
    print(f"📦 Entries fetched: {len(feed)}")

    notified = set() if test else load_set(NOTIFIED_FILE)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    sent = 0

    for e in feed:
        aid = e.get("anidb_aid")
        eid = e.get("anidb_eid")

        if aid not in WHITELIST_ANIDB:
            continue

        # ✅ FIX 1: Skip entries without episode ID
        if eid is None:
            continue

        if test:
            ts = datetime.fromtimestamp(e["timestamp"], tz=timezone.utc)
            if ts < cutoff:
                continue

        codec = classify(e["title"])
        if not codec:
            continue

        dedupe_key = f"{aid}|{eid}|{codec}"
        if dedupe_key in notified:
            continue

        meta = resolve_metadata(aid)

        print(f"✔ SEND | {ANIME_INDEX[aid]['title']} | {codec}")

        send_release(
            e,
            aid,
            codec,
            meta["image"],
            DISCORD_TEST_MAGNET_WEBHOOK if test else DISCORD_MAGNET_WEBHOOK,
            DISCORD_TEST_TORRENT_WEBHOOK if test else DISCORD_TORRENT_WEBHOOK,
        )

        # ✅ FIX 2: Immediate persistence
        notified.add(dedupe_key)
        save_set(NOTIFIED_FILE, notified)

        sent += 1
        time.sleep(5)

    print(f"✅ Sent: {sent}")

# ==================================================
# ENTRY
# ==================================================

if __name__ == "__main__":
    run(test="--test-24h" in sys.argv)
