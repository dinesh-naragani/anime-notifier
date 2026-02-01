import requests

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

def resolve_metadata(anidb_aid: int, anime_index: dict):
    """
    Resolve metadata for a given AniDB ID using AniList.
    anime_index must contain an 'anilist' key for the given anidb_aid.
    """
    if anidb_aid in _METADATA_CACHE:
        return _METADATA_CACHE[anidb_aid]

    anilist_id = anime_index[anidb_aid]["anilist"]

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
