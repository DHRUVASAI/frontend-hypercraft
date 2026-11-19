#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s\)>`'\"]+")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-external", action="store_true")
    args = parser.parse_args()

    errors = []
    md_files = sorted(ROOT.rglob("*.md"))
    external_urls = set()

    for mf in md_files:
        text = mf.read_text(encoding="utf-8")
        rel_mf = mf.relative_to(ROOT).as_posix()
        for target in MD_LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                if target.startswith(("http://", "https://")):
                    external_urls.add(target)
                continue
            path_part = target.split("#")[0]
            if not path_part:
                continue
            if not (mf.parent / path_part).resolve().exists():
                errors.append(f"[BROKEN LINK] {rel_mf} -> {target}")
        for u in URL_RE.findall(text):
            u_clean = u.rstrip(".,;:")
            if "<" in u_clean or ">" in u_clean or "localhost" in u_clean:
                continue
            if not u_clean.startswith("https://"):
                errors.append(f"[NON-HTTPS URL] {rel_mf} -> {u_clean}")
            external_urls.add(u_clean)

    manifest_path = ROOT / "evidence/pricing/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for snap in manifest.get("snapshots", []):
        fp = ROOT / snap["file"]
        if not fp.exists():
            errors.append(f"[MISSING EVIDENCE] {snap['file']}")
        elif hashlib.sha256(fp.read_bytes()).hexdigest() != snap["sha256"]:
            errors.append(f"[HASH MISMATCH] {snap['file']}")

    if args.check_external:
        for url in sorted(external_urls):
            try:
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "KB-Link-Validator/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status >= 400:
                        errors.append(f"[HTTP {resp.status}] {url}")
            except Exception as exc:
                errors.append(f"[HTTP ERR] {url} ({exc})")

    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"VALIDATION PASSED: {len(md_files)} Markdown files, {len(external_urls)} HTTPS URLs, all evidence SHA-256 valid, 0 broken links.")


if __name__ == "__main__":
    main()
