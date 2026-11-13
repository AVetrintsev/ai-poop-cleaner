#!/usr/bin/env python3
"""Read-only Docker metadata snapshot. No cleanup commands are implemented here."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


LABELS = (
    "com.docker.compose.project", "com.docker.compose.service",
    "com.docker.compose.project.working_dir", "com.docker.compose.project.config_files",
    "io.ai-poop-cleaner.project", "io.ai-poop-cleaner.purpose",
    "io.ai-poop-cleaner.run-id", "io.ai-poop-cleaner.expires-at",
)


def labels(value):
    return {key: value[key] for key in LABELS if key in (value or {})}


def project_resource(kind, item):
    """Allowlist metadata; never export env, commands, arbitrary options or labels."""
    if kind == "container":
        config = item.get("Config") or {}
        host = item.get("HostConfig") or {}
        state = item.get("State") or {}
        logging = host.get("LogConfig") or {}
        return {
            "id": item["Id"], "name": item.get("Name"), "image_id": item.get("Image"),
            "created": item.get("Created"), "labels": labels(config.get("Labels")),
            "state": {key: state.get(key) for key in (
                "Status", "Running", "Paused", "Restarting", "StartedAt", "FinishedAt")},
            "health": (state.get("Health") or {}).get("Status"),
            "restart_policy": host.get("RestartPolicy"),
            "restart_count": item.get("RestartCount"),
            "logging": {"type": logging.get("Type"), "options": {
                key: value for key, value in (logging.get("Config") or {}).items()
                if key in ("max-size", "max-file")}},
            "log_path": item.get("LogPath"),
            "mounts": [{key: mount.get(key) for key in (
                "Type", "Name", "Source", "Destination", "RW")}
                for mount in item.get("Mounts", [])],
            "networks": sorted((item.get("NetworkSettings") or {}).get("Networks", {})),
        }
    if kind == "image":
        return {"id": item["Id"], "tags": item.get("RepoTags") or [],
                "created": item.get("Created"), "size": item.get("Size"),
                "labels": labels((item.get("Config") or {}).get("Labels"))}
    if kind == "volume":
        return {"name": item["Name"], "created": item.get("CreatedAt"),
                "driver": item.get("Driver"), "labels": labels(item.get("Labels"))}
    return {"id": item["Id"], "name": item.get("Name"),
            "labels": labels(item.get("Labels")),
            "container_ids": sorted(item.get("Containers") or {})}


class Docker:
    def __init__(self, prefix, timeout=30):
        self.prefix = prefix
        self.timeout = timeout

    def run(self, *args):
        result = subprocess.run(self.prefix + list(args), capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=self.timeout, check=False)
        if result.returncode:
            # Raw stderr may contain endpoint credentials; retain the error category.
            raise RuntimeError(f"Docker {' '.join(args[:2])} exited {result.returncode}")
        return result.stdout


def collect(docker):
    report = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(),
              "complete": True, "errors": [], "resources": {}}

    def error(stage, exc):
        report["complete"] = False
        report["errors"].append({"stage": stage, "type": type(exc).__name__})

    try:
        # Server ID binds the snapshot without disclosing endpoint/auth details.
        report["engine_id"] = docker.run("info", "--format", "{{.ID}}").strip()
        if not report["engine_id"]:
            raise ValueError("Missing engine identity")
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as exc:
        error("engine", exc)
        return report

    listings = {"container": ("container", "ls", "-aq", "--no-trunc"),
                "image": ("image", "ls", "-aq", "--no-trunc"),
                "volume": ("volume", "ls", "-q"),
                "network": ("network", "ls", "-q", "--no-trunc")}
    for kind, command in listings.items():
        rows = []
        report["resources"][kind] = rows
        try:
            ids = sorted(set(docker.run(*command).split()))
            for offset in range(0, len(ids), 50):
                batch = ids[offset:offset + 50]
                items = json.loads(docker.run(kind, "inspect", *batch))
                if not isinstance(items, list):
                    raise ValueError("Unexpected inspect response")
                identity_key = "Name" if kind == "volume" else "Id"
                if {item[identity_key] for item in items} != set(batch):
                    raise ValueError("Incomplete inspect response")
                rows.extend(project_resource(kind, item) for item in items)
            # Detect additions/removals during traversal; snapshots are not transactions.
            if set(docker.run(*command).split()) != set(ids):
                raise ValueError("Inventory changed during collection")
        except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError,
                KeyError, TypeError, AttributeError) as exc:
            error(kind, exc)
    try:
        if docker.run("info", "--format", "{{.ID}}").strip() != report["engine_id"]:
            raise ValueError("Engine changed")
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as exc:
        error("engine_recheck", exc)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--context", help="Explicit Docker context")
    target.add_argument("--wsl", help="Explicit running WSL distribution; default user")
    parser.add_argument("--out", type=Path, help="New JSON file; never overwrites")
    args = parser.parse_args()
    prefix = ["docker"]
    if args.context:
        prefix += ["--context", args.context]
    if args.wsl:
        prefix = ["wsl.exe", "--distribution", args.wsl, "--exec", "docker"]
    report = collect(Docker(prefix))
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with args.out.open("x", encoding="utf-8") as output:
            output.write(encoded)
        print(json.dumps({"report": str(args.out), "complete": report["complete"],
                          "counts": {key: len(value) for key, value in
                                     report["resources"].items()}, "errors": report["errors"]}))
    else:
        print(encoded)
    return 0 if report["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
