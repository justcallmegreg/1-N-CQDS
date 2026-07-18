#!/usr/bin/env python3
"""scaffold.py — deterministic 1-N-CQDS repository emitter.

Takes a structured config (never prose) and writes a repository skeleton.
stdlib only. The scaffolding-repository skill builds the config by reading
ARCHITECTURE.md; this script only ever sees the config.
"""
import argparse, json, sys
from pathlib import Path

def load_config(args) -> dict:
    if args.config:
        return json.loads(Path(args.config).read_text())
    return json.loads(sys.stdin.read())

def scaffold(config: dict, dest: Path) -> list[Path]:
    created = []
    def mkdir(rel):
        p = dest / rel; p.mkdir(parents=True, exist_ok=True); created.append(p)
    def write(rel, content):
        p = dest / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content); created.append(p)

    mkdir("docs/adr")
    mkdir("e2e")
    mkdir("frontend")
    for svc in config["services"]:
        mkdir(f"backends/{svc}")
    write("VERSION.txt", config["version"] + "\n")
    return created

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config"); ap.add_argument("--dest", required=True)
    args = ap.parse_args()
    config = load_config(args)
    dest = Path(args.dest); dest.mkdir(parents=True, exist_ok=True)
    created = scaffold(config, dest)
    print(f"scaffolded {len(created)} paths into {dest}")

if __name__ == "__main__":
    main()
