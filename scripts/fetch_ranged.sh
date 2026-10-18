#!/usr/bin/env bash
# Resumable chunked download of a public Google Drive file (HTTP range requests).
# Usage: bash scripts/fetch_ranged.sh <drive_id> <output_file> <total_bytes>
set -e
ID="$1"; OUT="$2"; TOTAL="$3"; CHUNK=$((64 * 1024 * 1024))
URL="https://drive.usercontent.google.com/download?id=${ID}&export=download&confirm=t"
touch "$OUT"
while true; do
  have=$(stat -c %s "$OUT")
  [ "$have" -ge "$TOTAL" ] && break
  end=$((have + CHUNK - 1)); [ "$end" -ge "$TOTAL" ] && end=$((TOTAL - 1))
  ok=0
  for try in 1 2 3 4 5; do
    if curl -sfL -r "${have}-${end}" "$URL" -o "${OUT}.part"; then
      sz=$(stat -c %s "${OUT}.part")
      if [ "$sz" -eq $((end - have + 1)) ]; then cat "${OUT}.part" >> "$OUT"; ok=1; break; fi
    fi
    sleep 5
  done
  rm -f "${OUT}.part"
  # stop instead of retrying forever (e.g. when the host's download quota is exhausted); rerun later to resume
  if [ "$ok" -ne 1 ]; then echo "giving up at byte $have (quota or network); rerun later to resume" >&2; exit 1; fi
done
echo "done $OUT $(stat -c %s "$OUT")"
