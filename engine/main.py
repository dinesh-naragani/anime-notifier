import os
import sys

from engine.engine import run

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NOTIFIED_FILE = os.path.join(BASE_DIR, "notified_episodes_engine.txt")

DISCORD_MAGNET_WEBHOOK = os.getenv("DISCORD_MAGNET_WEBHOOK")
DISCORD_TORRENT_WEBHOOK = os.getenv("DISCORD_TORRENT_WEBHOOK")

DISCORD_TEST_MAGNET_WEBHOOK = os.getenv("DISCORD_TEST_MAGNET_WEBHOOK")
DISCORD_TEST_TORRENT_WEBHOOK = os.getenv("DISCORD_TEST_TORRENT_WEBHOOK")


if __name__ == "__main__":
    test_mode = "--test-24h" in sys.argv

    run(
        notified_file=NOTIFIED_FILE,
        magnet_webhook=(
            DISCORD_TEST_MAGNET_WEBHOOK
            if test_mode
            else DISCORD_MAGNET_WEBHOOK
        ),
        torrent_webhook=(
            DISCORD_TEST_TORRENT_WEBHOOK
            if test_mode
            else DISCORD_TORRENT_WEBHOOK
        ),
        test=test_mode,
    )
