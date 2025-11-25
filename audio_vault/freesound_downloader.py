#!/usr/bin/env python3
# audio_vault/freesound_downloader.py
"""
Download samples from Freesound.org for use in DAiW.

Requires a Freesound API key. Get one at:
https://freesound.org/apiv2/apply/

Usage:
    export FREESOUND_API_KEY=your_key_here
    python -m audio_vault.freesound_downloader --query "kick drum" --count 5
    python -m audio_vault.freesound_downloader --query "industrial noise" --license cc0
"""

import argparse
import os
import urllib.request
import json
from pathlib import Path
from typing import List, Dict, Optional

DEFAULT_OUTPUT = Path(__file__).parent / "samples" / "freesound"

# Freesound API base URL
API_BASE = "https://freesound.org/apiv2"


def get_api_key() -> Optional[str]:
    """Get API key from environment."""
    return os.environ.get("FREESOUND_API_KEY")


def search_sounds(
    query: str,
    api_key: str,
    count: int = 10,
    license_filter: Optional[str] = None,
) -> List[Dict]:
    """Search Freesound for sounds."""

    params = {
        "query": query,
        "page_size": min(count, 150),
        "fields": "id,name,previews,license,duration,username",
        "token": api_key,
    }

    if license_filter:
        # Map friendly names to Freesound license codes
        license_map = {
            "cc0": "Creative Commons 0",
            "cc-by": "Attribution",
            "cc-by-nc": "Attribution Noncommercial",
        }
        if license_filter in license_map:
            params["license"] = license_map[license_filter]

    query_string = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    url = f"{API_BASE}/search/text/?{query_string}"

    try:
        import urllib.parse
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data.get("results", [])
    except Exception as e:
        print(f"Search error: {e}")
        return []


def download_sound(sound: Dict, output_dir: Path, api_key: str) -> Optional[Path]:
    """Download a sound's preview."""

    previews = sound.get("previews", {})
    # Prefer HQ preview
    preview_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")

    if not preview_url:
        print(f"  No preview available for {sound['name']}")
        return None

    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in sound["name"])
    safe_name = safe_name[:50]  # Limit length
    filename = f"{sound['id']}_{safe_name}.mp3"
    output_path = output_dir / filename

    try:
        print(f"  Downloading: {sound['name'][:40]}...")
        urllib.request.urlretrieve(preview_url, output_path)
        return output_path
    except Exception as e:
        print(f"  Download error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Download samples from Freesound.org"
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Search query (e.g., 'kick drum', 'ambient pad')"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=10,
        help="Number of sounds to download"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory"
    )
    parser.add_argument(
        "--license", "-l",
        choices=["cc0", "cc-by", "cc-by-nc"],
        help="Filter by license type"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Freesound API key (or set FREESOUND_API_KEY env var)"
    )
    args = parser.parse_args()

    api_key = args.api_key or get_api_key()

    if not api_key:
        print("ERROR: No API key provided.")
        print()
        print("Get a free API key at: https://freesound.org/apiv2/apply/")
        print()
        print("Then either:")
        print("  1. Set environment variable: export FREESOUND_API_KEY=your_key")
        print("  2. Pass it as argument: --api-key your_key")
        return

    print(f"Searching Freesound for: '{args.query}'")
    print(f"License filter: {args.license or 'any'}")
    print()

    sounds = search_sounds(args.query, api_key, args.count, args.license)

    if not sounds:
        print("No sounds found.")
        return

    print(f"Found {len(sounds)} sounds")
    print()

    args.output.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    for sound in sounds[:args.count]:
        result = download_sound(sound, args.output, api_key)
        if result:
            downloaded += 1
            print(f"    → {result.name}")
            print(f"       by {sound.get('username', 'unknown')} | {sound.get('license', 'unknown')}")

    print()
    print(f"Downloaded {downloaded} sounds to {args.output}")


if __name__ == "__main__":
    main()
