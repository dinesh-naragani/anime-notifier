import json
import os
import tempfile
import requests

def torrent_filename(name: str, codec: str) -> str:
    return f"{name.replace(' ', '.')}.{codec}.torrent"

def extract_links(entry: dict):
    return entry.get("magnet_uri"), entry.get("torrent_url")

def send_release(
    entry: dict,
    title: str,
    codec: str,
    image: str,
    magnet_webhook: str,
    torrent_webhook: str,
):
    magnet, torrent = extract_links(entry)

    embed = {
        "title": title,
        "description": codec,
        "url": entry["link"],
        "image": {"url": image},
    }

    if magnet:
        requests.post(
            magnet_webhook,
            json={"embeds": [embed]},
            timeout=15,
        )
        requests.post(
            magnet_webhook,
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
            f"{torrent_webhook}?wait=true",
            json={"embeds": [embed]},
            timeout=15,
        )
        mid = r.json()["id"]

        with open(path, "rb") as f:
            requests.post(
                torrent_webhook,
                files={
                    "file": (
                        torrent_filename(title, codec),
                        f,
                        "application/x-bittorrent",
                    )
                },
                data={
                    "payload_json": json.dumps(
                        {"message_reference": {"message_id": mid}}
                    )
                },
                timeout=30,
            )

        os.remove(path)
