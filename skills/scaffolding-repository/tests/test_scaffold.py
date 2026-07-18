import json, subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "scaffold.py"

BASE_CONFIG = {
    "name": "fieldnote", "version": "0.1.0", "license": "Apache-2.0",
    "language": "python", "frontend": "astro", "container_engine": "docker",
    "components": {"database": "postgres", "object_storage": "minio", "cache": None, "queue": None},
    "services": ["fieldnote"],
}

def run_scaffold(tmp_path, config):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config))
    r = subprocess.run([sys.executable, str(SCRIPT), "--config", str(cfg), "--dest", str(tmp_path / "out")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return tmp_path / "out"

def test_emits_base_directory_layout(tmp_path):
    out = run_scaffold(tmp_path, BASE_CONFIG)
    for p in ["VERSION.txt", "docs/adr", "e2e", "frontend", "backends/fieldnote"]:
        assert (out / p).exists(), f"missing {p}"

def test_version_txt_is_single_source(tmp_path):
    out = run_scaffold(tmp_path, BASE_CONFIG)
    assert (out / "VERSION.txt").read_text().strip() == "0.1.0"

def test_makefile_has_mandatory_targets(tmp_path):
    out = run_scaffold(tmp_path, BASE_CONFIG)
    mk = (out / "Makefile").read_text()
    for target in ["help:", "up:", "down:"]:
        assert target in mk, f"missing target {target}"
    # docker is default, podman overridable
    assert "CONTAINER_ENGINE ?= docker" in mk

def test_makefile_help_runs(tmp_path):
    out = run_scaffold(tmp_path, BASE_CONFIG)
    import subprocess
    r = subprocess.run(["make", "-C", str(out), "help"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "up" in r.stdout and "down" in r.stdout

def test_compose_includes_approved_components(tmp_path):
    out = run_scaffold(tmp_path, BASE_CONFIG)  # postgres + minio approved
    compose = (out / "docker-compose.yml").read_text()
    assert "postgres" in compose
    assert "minio" in compose

def test_compose_omits_rejected_components(tmp_path):
    # cache and queue are null (rejected) in BASE_CONFIG
    out = run_scaffold(tmp_path, BASE_CONFIG)
    compose = (out / "docker-compose.yml").read_text().lower()
    assert "redis" not in compose, "rejected cache must not appear"
    assert "rabbitmq" not in compose and "amqp" not in compose, "rejected queue must not appear"

def test_compose_includes_cache_when_approved(tmp_path):
    cfg = dict(BASE_CONFIG); cfg["components"] = dict(BASE_CONFIG["components"], cache="redis")
    out = run_scaffold(tmp_path, cfg)
    assert "redis" in (out / "docker-compose.yml").read_text().lower()

def test_compose_config_validates(tmp_path):
    out = run_scaffold(tmp_path, BASE_CONFIG)
    # docker or podman may be absent in CI; skip the runtime check gracefully
    import shutil
    engine = "docker" if shutil.which("docker") else ("podman" if shutil.which("podman") else None)
    if not engine:
        import pytest; pytest.skip("no container engine available")
    r = subprocess.run([engine, "compose", "-f", str(out / "docker-compose.yml"), "config"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

def test_compose_valid_with_zero_infra_components(tmp_path):
    # A genuinely stateless service could reject database, object storage,
    # cache, AND queue. services:/volumes: must still be valid YAML mappings,
    # not dangling/null keys, or `docker compose config` fails outright.
    cfg = dict(BASE_CONFIG)
    cfg["components"] = {"database": None, "object_storage": None, "cache": None, "queue": None}
    out = run_scaffold(tmp_path, cfg)
    compose_path = out / "docker-compose.yml"
    text = compose_path.read_text()
    lines = text.splitlines()
    assert "services: {}" in lines, "services: must be an explicit empty mapping, not dangling/null"
    for line in lines:
        assert line.strip() != "services:", "bare 'services:' with no children parses as null"
        assert line.strip() != "volumes:", "bare 'volumes:' with no children parses as null"
    import shutil
    engine = "docker" if shutil.which("docker") else ("podman" if shutil.which("podman") else None)
    if not engine:
        import pytest; pytest.skip("no container engine available")
    r = subprocess.run([engine, "compose", "-f", str(compose_path), "config"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
