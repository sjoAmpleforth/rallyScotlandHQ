#!/usr/bin/env python3
"""Mirror the Rally HQ page's group-chat message into the feed files.

Usage: python3 sync.py <saved-page.html>

Reads the JSON in <script type="application/json" id="trip-data"> and writes:
  whatsapp.txt  the "whatsapp" string, exactly as the page's Copy text button copies it
  updated.txt   the "lastChecked" string (YYYY-MM-DDTHH:MM, UK time)
Both UTF-8, no trailing newline. Prints CHANGED or UNCHANGED; exits non-zero on error.
"""
import json, pathlib, re, sys

def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 sync.py <saved-page.html>")
    html = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="trip-data">(.*?)</script>', html, re.S)
    if not m:
        sys.exit("ERROR: trip-data JSON block not found in the page")
    data = json.loads(m.group(1))
    wanted = {"whatsapp.txt": data.get("whatsapp"), "updated.txt": data.get("lastChecked")}
    if not isinstance(wanted["whatsapp.txt"], str) or not wanted["whatsapp.txt"].strip():
        sys.exit("ERROR: whatsapp message is missing or empty")
    if not isinstance(wanted["updated.txt"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", wanted["updated.txt"]):
        sys.exit("ERROR: lastChecked is missing or not YYYY-MM-DDTHH:MM")
    root = pathlib.Path(__file__).resolve().parent
    changed = False
    for name, value in wanted.items():
        path = root / name
        current = path.read_bytes().decode("utf-8") if path.exists() else None
        if current != value:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(value)
            changed = True
    print("CHANGED" if changed else "UNCHANGED")

if __name__ == "__main__":
    main()
