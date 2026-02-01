#!/data/data/com.termux/files/usr/bin/bash

cd ~/anime_watcher || exit 1

source ~/serverenv/bin/activate

while true
do
  python animetosho_watcher.py
  sleep 60
done
