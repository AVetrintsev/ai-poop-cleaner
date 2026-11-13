#!/usr/bin/env python3
"""Check selected ephemeral services from effective Compose JSON on stdin."""

import argparse
import json
import re
import sys


def check(config, selected):
    failures = []
    services = config.get("services", {})
    for name in selected:
        service = services.get(name)
        if not isinstance(service, dict):
            failures.append(f"{name}: service missing")
            continue
        if service.get("restart", "no") != "no":
            failures.append(f"{name}: ephemeral restart must be no")
        labels = service.get("labels") or {}
        if not isinstance(labels, dict):
            failures.append(f"{name}: expected normalized label mapping")
        else:
            for key in ("project", "run-id"):
                if not labels.get("io.ai-poop-cleaner." + key):
                    failures.append(f"{name}: missing lifecycle label {key}")
            if labels.get("io.ai-poop-cleaner.purpose") != "ephemeral-test":
                failures.append(f"{name}: purpose must be ephemeral-test")
        logging = service.get("logging") or {}
        options = logging.get("options") or {}
        if logging.get("driver") not in ("json-file", "local"):
            failures.append(f"{name}: configure a bounded local logging driver")
        if not re.fullmatch(r"[1-9][0-9]*[kmgKMG]?", str(options.get("max-size", ""))):
            failures.append(f"{name}: max-size must be a positive finite size")
        if not re.fullmatch(r"[1-9][0-9]*", str(options.get("max-file", ""))):
            failures.append(f"{name}: max-file must be a positive integer")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", action="append", required=True,
                        help="Exact temporary service; repeat for multiple services")
    args = parser.parse_args()
    try:
        failures = check(json.load(sys.stdin), args.service)
    except (ValueError, AttributeError, TypeError):
        print("Invalid effective Compose JSON", file=sys.stderr)
        return 2
    for failure in failures:
        print(failure)
    if not failures:
        print("Selected ephemeral services: policy OK (teardown still needs a lifecycle test)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
