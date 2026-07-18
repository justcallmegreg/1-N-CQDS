#!/usr/bin/env python3
"""scaffold.py — deterministic 1-N-CQDS repository emitter.

Takes a structured config (never prose) and writes a repository skeleton.
stdlib only. The scaffolding-repository skill builds the config by reading
ARCHITECTURE.md; this script only ever sees the config.
"""
import argparse, json, sys
from pathlib import Path

ASSETS = Path(__file__).parent.parent / "assets"

def load_config(args) -> dict:
    if args.config:
        return json.loads(Path(args.config).read_text())
    return json.loads(sys.stdin.read())

def render(template_name: str, mapping: dict) -> str:
    text = (ASSETS / template_name).read_text()
    for k, v in mapping.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text

def render_compose(config: dict) -> str:
    """Assemble docker-compose.yml from gate-approved component fragments only.

    Doctrine: a component the architecture ADRs rejected (component value is
    null in config) MUST NOT appear in the emitted compose file. The template
    asset holds every possible fragment; this function selects only the
    fragments whose component was actually approved.

    Edge case: if every infra component is null (permitted — a fully
    stateless service could reject database, object storage, cache, and
    queue alike), the "services:" and "volumes:" keys must still be valid
    YAML mappings. A bare "services:" with no indented children parses as
    null, which `docker compose config` rejects ("services must be a
    mapping"). When zero fragments are selected for a key, that key is
    emitted as an explicit empty mapping ("services: {}" / "volumes: {}")
    instead of being left dangling.
    """
    raw = (ASSETS / "docker-compose.tmpl.yml").read_text()
    frags = {}
    cur = None
    for line in raw.splitlines():
        if line.startswith("# --- ") and line.endswith(" ---"):
            cur = line[6:-4]; frags[cur] = []
        elif cur is not None:
            frags[cur].append(line)
    def block(name): return "\n".join(frags.get(name, []))
    comp = config["components"]
    has_db = comp.get("database") == "postgres"
    has_obj = comp.get("object_storage") == "minio"
    has_cache = comp.get("cache") == "redis"
    has_queue = comp.get("queue") == "rabbitmq"
    any_service = has_db or has_obj or has_cache or has_queue
    any_volume = has_db or has_obj

    header_lines = list(frags.get("HEADER", []))
    if not any_service and header_lines and header_lines[-1] == "services:":
        header_lines[-1] = "services: {}"

    volumes_lines = list(frags.get("VOLUMES", []))
    if not any_volume and volumes_lines and volumes_lines[-1] == "volumes:":
        volumes_lines[-1] = "volumes: {}"

    out = ["\n".join(header_lines)]
    if has_db: out.append(block("DATABASE:postgres"))
    if has_obj: out.append(block("OBJECT_STORAGE:minio"))
    if has_cache: out.append(block("CACHE:redis"))
    if has_queue: out.append(block("QUEUE:rabbitmq"))
    out.append(block("APPSTUB"))
    out.append("\n".join(volumes_lines))
    if has_db: out.append(block("VOL:db"))
    if has_obj: out.append(block("VOL:obj"))
    text = "\n".join(out)
    for k, v in {"NAME": config["name"]}.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text

def scaffold(config: dict, dest: Path) -> list[Path]:
    created = []
    def mkdir(rel):
        p = dest / rel
        p.mkdir(parents=True, exist_ok=True)
        created.append(p)
    def write(rel, content):
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        created.append(p)

    mkdir("docs/adr")
    mkdir("e2e")
    mkdir("frontend")
    for svc in config["services"]:
        mkdir(f"backends/{svc}")
    write("VERSION.txt", config["version"] + "\n")
    write("Makefile", render("Makefile.tmpl", {"NAME": config["name"]}))
    write("docker-compose.yml", render_compose(config))
    write("README.md", render("README.tmpl.md", {"NAME": config["name"]}))
    write(".gitignore", render("gitignore.tmpl", {}))
    write("CODEOWNERS", render("CODEOWNERS.tmpl", {"NAME": config["name"]}))
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
