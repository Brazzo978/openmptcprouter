#!/usr/bin/env python3
"""Bootstrap or verify exact source checkouts for OMR v0.64.2-3K.

No existing checkout is reset, cleaned or updated. Dirty local edits are
allowed after the pinned HEAD has been verified.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "source-lock-3k.json"
SHA = re.compile(r"^[0-9a-f]{40}$")

def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args],
                                   text=True, stderr=subprocess.PIPE).strip()

def validate(data):
    if data.get("schema") != 1 or data.get("target") != "x86_64" or data.get("kernel") != "6.18":
        raise ValueError("unsupported source lock")
    if not SHA.fullmatch(data.get("root_upstream_base", "")):
        raise ValueError("invalid root base commit")
    feed = data["client_feed_release"]
    if not feed.get("url") or not SHA.fullmatch(feed.get("commit") or ""):
        raise ValueError("unpublished client feed: fill exact release URL and 40-character commit before build/bootstrap")
    rows = [feed, *data["upstream"].values()]
    for row in rows:
        if not SHA.fullmatch(row["commit"]):
            raise ValueError("invalid pinned commit: " + row["path"])
        if not row["url"].startswith("https://github.com/"):
            raise ValueError("unsupported source URL: " + row["path"])
        path = (ROOT / row["path"]).resolve()
        if ROOT.resolve() not in path.parents:
            raise ValueError("checkout escapes release root: " + row["path"])
    return rows

def verify_one(row, allow_development=False):
    path = ROOT / row["path"]
    if not (path / ".git").exists():
        raise ValueError("missing pinned checkout: " + str(path))
    actual = git(path, "rev-parse", "HEAD")
    origin = git(path, "remote", "get-url", "origin")
    dirty = bool(git(path, "status", "--porcelain"))
    normalized_origin = origin.rstrip("/").removesuffix(".git").lower()
    normalized_locked = row["url"].rstrip("/").removesuffix(".git").lower()
    if actual == row["commit"] and normalized_origin == normalized_locked:
        print(f"OK {row['path']} {actual} {'(local edits retained)' if dirty else '(clean)'}")
        return
    # Explicit opt-in for this *existing* development checkout only. It may
    # not materialize a release and must never be presented as reproducible.
    if allow_development and row["path"] == "feeds/openmptcprouter":
        base = "818fa5116eefc99325e0f231e819dc51b062ef85"
        official = "https://github.com/ysurac/openmptcprouter-feeds"
        if actual == base and normalized_origin == official and dirty:
            print(f"DEVELOPMENT ONLY {row['path']} base {actual} with local edits; release pin is {row['commit']}")
            return
    if actual != row["commit"]:
        raise ValueError(f"commit mismatch {row['path']}: {actual} != {row['commit']}")
    raise ValueError(f"origin mismatch {row['path']}: {origin}")

def verify_root(data):
    if not (ROOT / ".git").exists():
        raise ValueError("release root is not a Git checkout")
    subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor",
                    data["root_upstream_base"], "HEAD"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def verify(data, rows):
    verify_root(data)
    allow_development = os.environ.get("OMR3K_ALLOW_LOCAL_EDITS") == "yes"
    for row in rows:
        verify_one(row, allow_development)

def materialize(row):
    path = ROOT / row["path"]
    if (path / ".git").exists():
        verify_one(row)
        return
    if path.exists() and any(path.iterdir()):
        raise ValueError("refusing nonempty non-Git path: " + str(path))
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(path), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(path), "remote", "add", "origin", row["url"]], check=True)
    # Fetch this object ID only. Branch tips may move but can never select a
    # different commit; a server refusing exact-SHA fetch fails closed.
    subprocess.run(["git", "-C", str(path), "fetch", "--depth=1", "origin", row["commit"]], check=True)
    subprocess.run(["git", "-C", str(path), "checkout", "--detach", "-q", row["commit"]], check=True)
    verify_one(row)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["verify", "materialize"])
    args = parser.parse_args()
    data = json.loads(LOCK.read_text())
    rows = validate(data)
    if args.action == "materialize":
        verify_root(data)
        for row in rows:
            materialize(row)
    verify(data, rows)
    if os.environ.get("OMR3K_ALLOW_LOCAL_EDITS") == "yes":
        print("DEVELOPMENT MODE: unpublished local feed edits are not a release artifact")
    else:
        print("3K release source lock verified; local edits were not reset")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError) as exc:
        print("3K source lock failure:", exc, file=sys.stderr)
        sys.exit(1)
