# Anime Watcher – RSS Notification Engine

A production-grade, self-hosted **RSS → Notification engine** designed to run as a long-lived background worker on low-resource systems (Android phone via Termux).

This system ingests the AnimeTosho feed, filters and deduplicates releases, enriches metadata via AniList, and delivers notifications to Discord — with **health reporting, monitoring, and alerting handled externally by a control-plane service**.

---

## 🚀 Key Features

- Long-running background worker
- RSS ingestion and filtering
- Stateful deduplication (exactly-once notifications)
- Codec-aware classification (H.264 / H.265, 1080p)
- External metadata enrichment (AniList GraphQL)
- Discord notifications (magnets + torrent files)
- CSV-based configuration (no code edits required)
- Self-healing execution loop
- Health reporting for monitoring and alerting
- Safe fallback to legacy runner

---

## 🧠 Architecture Overview

```text
AnimeTosho RSS
      ↓
Feed Ingestion
      ↓
Filtering & Classification
      ↓
Deduplication (persistent state)
      ↓
Metadata Enrichment (AniList)
      ↓
Discord Notification
      ↓
Health State File (JSON)
````

Health, metrics, and alerts are exposed by a **separate FastAPI control-plane service**, keeping the worker lightweight and resilient.

---

## 📁 Repository Structure

```text
anime_watcher/
├── engine/
│   ├── engine.py          # Orchestration logic
│   ├── feed.py            # RSS ingestion
│   ├── classify.py        # Release classification
│   ├── state.py           # Persistent dedupe state
│   ├── metadata.py        # AniList metadata resolver
│   ├── discord.py         # Discord transport
│   ├── metrics.py         # Health writer
│   ├── anime_index.py     # CSV loader
│   └── main.py            # Engine entrypoint
│
├── data/
│   └── anime_index.csv    # Editable anime configuration
│
├── rss_loop.sh            # Resilient execution loop
├── animetosho_watcher.py  # Legacy implementation (fallback)
└── README.md
```

---

## ⚙️ Configuration

### Anime Index (CSV)

`data/anime_index.csv`

```csv
anidb_aid,title,anilist_id,enabled
18886,Frieren,182255,1
18363,Jujutsu Kaisen,172463,1
18742,Fire Force,179062,1
18901,Oshi no Ko,182587,1
19071,MF Ghost,185753,1
18090,Hell’s Paradise,166613,1
```

* Enable or disable shows without touching code
* Git-friendly and Excel-editable

---

### Environment Variables

The engine expects the following environment variables:

```bash
DISCORD_MAGNET_WEBHOOK=...
DISCORD_TORRENT_WEBHOOK=...

# Optional (used by control-plane alerts)
DISCORD_ALERT_WEBHOOK=...
```

---

## ▶️ Running the Engine

Always run from the **project root**.

### Production run

```bash
python -m engine.main
```

### Test mode (last 24 hours only)

```bash
python -m engine.main --test-24h
```

---

## 🔁 Resilient Execution Loop

The engine is typically run via `rss_loop.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash

cd ~/anime_watcher || exit 1
source ~/serverenv/bin/activate

while true
do
  python -m engine.main || python animetosho_watcher.py
  sleep 60
done
```

* New engine runs first
* Legacy watcher is automatic fallback
* Zero downtime, no missed releases

---

## 🩺 Health Reporting

The engine writes health state to:

```text
anime_health.json
```

Example:

```json
{
  "status": "running",
  "last_run_time": "2026-02-01T18:03:38Z",
  "sent_count": 3,
  "error_count": 0
}
```

This file is consumed by an external **control-plane service** that provides:

* `/health/anime`
* `/health/summary`
* `/metrics` (Prometheus)
* Discord alerts on failures

---

## 🛡️ Reliability Guarantees

* Exactly-once notifications via persistent dedupe keys
* Immediate state persistence after each send
* Automatic recovery on crashes
* No alert spam (stateful alert deduplication)
* Safe rollback to legacy runner

---

## 🎯 Why This Exists

Most “student projects”:

* Run once
* Have no monitoring
* Break silently

This system was built to:

* Run unattended
* Detect failures
* Alert on problems
* Recover automatically

It reflects **real backend and operations engineering practices**, not toy scripts.

---

## 🔮 Future Extensions

* Generic RSS adapters (jobs, security feeds, GitHub releases)
* SQLite-backed history and analytics
* Additional notification sinks (Telegram, email)
* Per-feed alerting rules
* Dashboard UI

---

## 🧑‍💻 Author

Built and operated by **Dinesh Naragani**,
Self-hosted on a personal server using Termux.

---
