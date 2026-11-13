#!/usr/bin/env python3
"""Check that the manifest still matches a proton-bridge checkout.

Usage: check_upstream.py <proton-bridge checkout>

Fails if upstream moved its vcpkg pin (grpc/protobuf/sentry versions may need
bumping), changed the googletest archive, or if a patch no longer applies.
"""

import glob
import os
import re
import subprocess
import sys

import yaml

MANIFEST = "ch.protonmail.protonmail-bridge.yaml"
CMAKE = "internal/frontend/bridge-gui/bridgepp/CMakeLists.txt"


def git(checkout, *args):
    return subprocess.run(["git", "-C", checkout, *args], check=True,
                          capture_output=True, text=True).stdout


def main(checkout):
    with open(MANIFEST) as f:
        modules = [m for m in yaml.safe_load(f)["modules"] if isinstance(m, dict)]
    errors = []

    grpc = next(m for m in modules if m["name"] == "grpc")
    pinned = git(checkout, "ls-tree", "HEAD", "extern/vcpkg").split()[2]
    if pinned != grpc["x-vcpkg-commit"]:
        errors.append(
            f"extern/vcpkg moved {grpc['x-vcpkg-commit']} -> {pinned}: check the "
            "grpc, protobuf and sentry-native ports there, then update "
            "x-vcpkg-commit")

    with open(f"{checkout}/{CMAKE}") as f:
        upstream_url = re.search(r"URL\s+(\S+googletest\S+)", f.read()).group(1)
    bridge = next(m for m in modules if m["name"] == "protonmail-bridge")
    urls = [s.get("url") for s in bridge["sources"] if isinstance(s, dict)]
    if upstream_url not in urls:
        errors.append(f"googletest archive changed upstream: {upstream_url}")

    # Apply as a series, in manifest order, like flatpak-builder does
    patches = [os.path.abspath(p) for s in bridge["sources"]
               if isinstance(s, dict) and s.get("type") == "patch"
               for p in s.get("paths", [s.get("path")])]
    result = subprocess.run(["git", "-C", checkout, "apply", "--check", *patches],
                            capture_output=True, text=True)
    if result.returncode != 0:
        errors.append(f"patches no longer apply:\n{result.stderr}")
    unused = set(map(os.path.abspath, glob.glob("patches/*.patch"))) - set(patches)
    for patch in sorted(unused):
        errors.append(f"{os.path.relpath(patch)} is not listed in the manifest")

    for error in errors:
        print(f"::error::{error}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
