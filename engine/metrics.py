import json
from datetime import datetime, timezone

def write_health(
    path: str,
    *,
    last_run_time: datetime,
    sent_count: int,
    error_count: int,
):
    payload = {
        "status": "running",
        "last_run_time": last_run_time.astimezone(timezone.utc).isoformat(),
        "sent_count": sent_count,
        "error_count": error_count,
    }

    with open(path, "w") as f:
        json.dump(payload, f)
