#!/usr/bin/env python3
"""Detect the latest Proton Authenticator version from the download page.

Outputs shell-eval-able lines to stdout:
  VERSION=1.1.4-1
  URL=https://proton.me/download/authenticator/linux/ProtonAuthenticator-1.1.4-1.x86_64.rpm
  SIZE=18627078

Exits with code 1 if detection fails.
"""

import re
import sys
import urllib.request

DOWNLOAD_PAGE = "https://proton.me/download/authenticator"
BASE_URL = "https://proton.me/download/authenticator/linux"
VERSION_RE = re.compile(r'ProtonAuthenticator-([\d]+\.[\d]+\.[\d]+-[\d]+)\.x86_64\.rpm')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def get_remote_size(url: str) -> int | None:
    """Return Content-Length of the URL via a HEAD request, or None."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            length = r.headers.get("Content-Length")
            return int(length) if length else None
    except Exception:
        return None


def main() -> None:
    try:
        html = fetch(DOWNLOAD_PAGE)
    except Exception as e:
        print(f"Error fetching download page: {e}", file=sys.stderr)
        sys.exit(1)

    matches = VERSION_RE.findall(html)
    if not matches:
        print("No RPM link found on the Proton Authenticator download page.", file=sys.stderr)
        print(f"Check manually: {DOWNLOAD_PAGE}", file=sys.stderr)
        sys.exit(1)

    version = matches[0]
    url = f"{BASE_URL}/ProtonAuthenticator-{version}.x86_64.rpm"

    size = get_remote_size(url)
    if size is None:
        print(f"Warning: could not determine file size for {url}", file=sys.stderr)
        size = 0

    print(f"VERSION={version}")
    print(f"URL={url}")
    print(f"SIZE={size}")


if __name__ == "__main__":
    main()
