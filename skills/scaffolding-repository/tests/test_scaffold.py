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
