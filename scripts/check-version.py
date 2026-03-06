#!/usr/bin/env python3
"""Detect the latest Proton Authenticator RPM from the official version JSON.

API: https://proton.me/download/authenticator/linux/version.json

Outputs shell-eval-able lines to stdout:
  VERSION=1.1.4-1
  URL=https://proton.me/download/authenticator/linux/ProtonAuthenticator-1.1.4-1.x86_64.rpm
  SIZE=18627078

Exits with code 1 if detection fails.
"""

import json
import re
import sys
import urllib.request

VERSION_JSON = "https://proton.me/download/authenticator/linux/version.json"
RPM_IDENTIFIER = ".rpm"
VERSION_RE = re.compile(r'ProtonAuthenticator-([\d.]+-\d+)\.x86_64\.rpm')


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get_remote_size(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        length = r.headers.get("Content-Length")
        return int(length) if length else 0


def find_latest_rpm(releases: list) -> tuple[str, str] | tuple[None, None]:
    """Return (version, url) for the latest stable RPM release."""
    for release in releases:
        if release.get("CategoryName") != "Stable":
            continue
        for f in release.get("File", []):
            if RPM_IDENTIFIER in f.get("Identifier", ""):
                url = f["Url"]
                m = VERSION_RE.search(url)
                if m:
                    return m.group(1), url
    return None, None


def main() -> None:
    try:
        data = fetch_json(VERSION_JSON)
    except Exception as e:
        print(f"Error fetching version JSON: {e}", file=sys.stderr)
        sys.exit(1)

    releases = data.get("Releases", [])
    if not releases:
        print("Empty releases list in version JSON.", file=sys.stderr)
        sys.exit(1)

    version, url = find_latest_rpm(releases)
    if not version:
        print("No stable RPM release found in version JSON.", file=sys.stderr)
        sys.exit(1)

    try:
        size = get_remote_size(url)
    except Exception as e:
        print(f"Warning: could not determine file size: {e}", file=sys.stderr)
        size = 0

    print(f"VERSION={version}")
    print(f"URL={url}")
    print(f"SIZE={size}")


if __name__ == "__main__":
    main()
