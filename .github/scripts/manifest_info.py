#!/usr/bin/env python3
"""Print tag= and commit= of the proton-bridge git source in the manifest."""

import sys

import yaml

MANIFEST = "ch.protonmail.protonmail-bridge.yaml"
URL = "https://github.com/ProtonMail/proton-bridge"


def bridge_source(path):
    with open(path) as f:
        manifest = yaml.safe_load(f)
    for module in manifest["modules"]:
        if not isinstance(module, dict):
            continue
        for source in module.get("sources", []):
            if isinstance(source, dict) and source.get("url") == URL:
                return source
    sys.exit(f"no {URL} source in {path}")


if __name__ == "__main__":
    source = bridge_source(sys.argv[1] if len(sys.argv) > 1 else MANIFEST)
    print(f"tag={source['tag']}")
    print(f"commit={source['commit']}")
