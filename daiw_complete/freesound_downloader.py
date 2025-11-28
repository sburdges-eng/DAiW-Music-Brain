#!/usr/bin/env python3
"""
Very simple Freesound downloader stub for DAiW.

You MUST:
    - Export FREESOUND_API_KEY in your environment, or
    - Hardcode it below (not recommended).
"""

import os
from pathlib import Path
import requests

API_KEY = os.getenv("FREESOUND_API_KEY", "")

BASE_URL = "https://freesound.org/apiv2/search/text/"


def download_pack_by_tags(queries, output_dir, limit=10):
    if not API_KEY:
        print("❌ FREESOUND_API_KEY not set; skipping download.")
        print("   Get a key at https://freesound.org/apiv2/apply/")
        return

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    headers = {"Authorization": f"Token {API_KEY}"}

    for q in queries:
        print(f"Searching: {q}")
        params = {"query": q, "fields": "id,name,previews", "page_size": limit}
        r = requests.get(BASE_URL, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        for res in data.get("results", []):
            sound_id = res["id"]
            name = res["name"]
            # Preview HQ if present; fallback to first preview
            previews = res.get("previews", {})
            url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
            if not url:
                continue

            safe_name = f"{sound_id}_{name}".replace(" ", "_")[:50]
            out_path = output_dir / f"{safe_name}.mp3"
            if out_path.exists():
                continue

            print(f"  ↳ downloading {name}")
            sr = requests.get(url, timeout=30)
            sr.raise_for_status()
            out_path.write_bytes(sr.content)

    print(f"✅ Done. Files in {output_dir}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        query = sys.argv[1]
    else:
        query = "glitch industrial"
    
    download_pack_by_tags(
        [query],
        "./audio_vault/raw/Downloaded_Samples",
        limit=8
    )
