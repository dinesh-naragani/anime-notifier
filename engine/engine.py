import time
from datetime import datetime, timezone, timedelta
import os

from engine.feed import fetch_feed
from engine.classify import classify
from engine.state import load_set, save_set
from engine.metadata import resolve_metadata
from engine.discord import send_release
from engine.anime_index import ANIME_INDEX, WHITELIST_ANIDB
from engine.metrics import write_health


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEALTH_FILE = os.path.join(BASE_DIR, "anime_health.json")


def run(
    notified_file: str,
    magnet_webhook: str,
    torrent_webhook: str,
    test: bool = False,
):
    print(f"🔎 Fetching AnimeTosho JSON (test={test})")
    feed = fetch_feed()
    print(f"📦 Entries fetched: {len(feed)}")

    notified = set() if test else load_set(notified_file)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    sent = 0
    errors = 0
    last_run = datetime.now(timezone.utc)

    for e in feed:
        try:
            aid = e.get("anidb_aid")
            eid = e.get("anidb_eid")

            if aid not in WHITELIST_ANIDB:
                continue

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

            meta = resolve_metadata(aid, ANIME_INDEX)

            print(f"✔ SEND | {ANIME_INDEX[aid]['title']} | {codec}")

            send_release(
                entry=e,
                title=ANIME_INDEX[aid]["title"],
                codec=codec,
                image=meta["image"],
                magnet_webhook=magnet_webhook,
                torrent_webhook=torrent_webhook,
            )

            notified.add(dedupe_key)
            save_set(notified_file, notified)

            sent += 1
            time.sleep(5)

        except Exception as ex:
            errors += 1
            print(f"❌ ERROR: {ex}")
            raise

        finally:
            write_health(
                path=HEALTH_FILE,
                last_run_time=last_run,
                sent_count=sent,
                error_count=errors,
            )

    print(f"✅ Sent: {sent}")
