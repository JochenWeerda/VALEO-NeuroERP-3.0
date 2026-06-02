"""Background-Runner: geocodiert alle offenen gap_map_points in Etappen (resumable)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.geo_pipeline import geocode_pending

batch = int(sys.argv[1]) if len(sys.argv) > 1 else 300
while True:
    r = geocode_pending(limit=batch, sleep_seconds=1.1)
    print(r, flush=True)
    if r["remaining"] == 0 or r["processed"] == 0:
        break
print("GEOCODING DONE", flush=True)
