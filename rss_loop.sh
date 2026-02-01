#!/data/data/com.termux/files/usr/bin/bash

cd ~/anime_watcher || exit 1

source ~/serverenv/bin/activate

while true
do
  echo "▶️ Running new engine..."
  python -m engine.main || {
    echo "⚠️ Engine failed — falling back to legacy watcher"
    python animetosho_watcher.py
  }

  sleep 60
done
