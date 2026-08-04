#!/usr/bin/env python3
"""
Recompute SHA-256 over every file in vendor/ and compare against
VENDOR_HASHES.json. Optionally re-fetch each file live from GitHub at the
pinned commit and compare against that too (requires the `gh` CLI and
network access) -- pass --live to do so.

This exists so nobody has to trust that injection_chain_repro.py's copies of
potpie-ai/potpie source are unmodified. Recompute it yourself.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
MANIFEST = HERE / "VENDOR_HASHES.json"


def sha256_of(path: Path) -> str:
    """Hash normalized to LF line endings.

    VENDOR_HASHES.json was computed from the raw git blob (LF, as stored on
    GitHub). A local checkout on Windows with the common `core.autocrlf=true`
    setting silently rewrites LF to CRLF, which would make every hash below
    mismatch despite the content being identical -- normalize before hashing
    so this check reflects content, not the checking-out platform's line
    endings. (A `.gitattributes` pinning these files to `eol=lf` is also
    committed so a *fresh* clone shouldn't hit this in the first place; this
    normalization is defense in depth for whoever's git config predates that
    or ignores it.)
    """
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live", action="store_true",
        help="also re-fetch each file from GitHub at the pinned commit via `gh api` and compare"
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    commit = manifest["commit"]
    repo = manifest["repo"]

    ok = True
    for local_path, info in manifest["files"].items():
        full_path = HERE / local_path
        expected = info["sha256"]
        if not full_path.exists():
            print(f"MISSING   {local_path}")
            ok = False
            continue
        actual = sha256_of(full_path)
        status = "MATCH" if actual == expected else "MISMATCH"
        if status == "MISMATCH":
            ok = False
        print(f"{status:9s} {local_path}  ({actual[:12]}...)")

        if args.live:
            upstream = info["upstream_path"]
            try:
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo}/contents/{upstream}?ref={commit}",
                     "--jq", ".content"],
                    capture_output=True, text=True, check=True, timeout=30,
                )
                import base64
                live_bytes = base64.b64decode(result.stdout.strip())
                live_hash = hashlib.sha256(live_bytes).hexdigest()
                live_status = "MATCH" if live_hash == expected else "MISMATCH"
                if live_status == "MISMATCH":
                    ok = False
                print(f"  live vs GitHub@{commit[:8]}: {live_status}")
            except Exception as exc:  # noqa: BLE001
                print(f"  live check failed: {exc!r}")
                ok = False

    print()
    if ok:
        print(f"All files verified against commit {commit} ({manifest['commit_subject']!r}).")
        return 0
    print("One or more files did not match. Do not trust the PoC output until this is resolved.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
