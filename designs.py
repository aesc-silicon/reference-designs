#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 aesc silicon
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""List reference designs from designs.json.

Default output is one tab-separated line per design:
    name  process  path  topcell
Paths are printed relative to this repository unless --absolute is given.
Designs opt into consumers via their "tools" list (gdscheck, gdsfill). An
empty list keeps a design in the manifest without any consumer running it,
e.g. while a tool does not support its process yet.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "designs.json"
FIELDS = ("name", "process", "path", "topcell")
TOOLS = ("gdscheck", "gdsfill")


def load():
    with MANIFEST.open() as f:
        return json.load(f)["designs"]


def check(designs):
    errors = []
    names = [d.get("name") for d in designs]
    for n in sorted({n for n in names if names.count(n) > 1}):
        errors.append(f"{n}: duplicate name")
    for d in designs:
        name = d.get("name", "?")
        missing = [k for k in FIELDS if not d.get(k)]
        if missing:
            errors.append(f"{name}: missing {', '.join(missing)}")
            continue
        if not (ROOT / d["path"]).is_file():
            errors.append(f"{name}: file not found: {d['path']}")
        tools = d.get("tools")
        if not isinstance(tools, list):
            errors.append(f"{name}: 'tools' must be a list")
        elif set(tools) - set(TOOLS):
            errors.append(f"{name}: unknown tool(s) {sorted(set(tools) - set(TOOLS))}")
    for e in errors:
        print(e, file=sys.stderr)
    return not errors


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--process", help="only designs for this PDK process")
    ap.add_argument("--tool", choices=TOOLS, help="only designs enabled for this tool")
    ap.add_argument("--json", action="store_true", help="print JSON instead of TSV")
    ap.add_argument("--absolute", action="store_true", help="print absolute paths")
    ap.add_argument("--check", action="store_true", help="validate the manifest and exit")
    args = ap.parse_args()

    designs = load()
    if args.check:
        sys.exit(0 if check(designs) else 1)
    if args.process:
        designs = [d for d in designs if d["process"] == args.process]
    if args.tool:
        designs = [d for d in designs if args.tool in d.get("tools", [])]
    if args.absolute:
        for d in designs:
            d["path"] = str(ROOT / d["path"])

    if args.json:
        json.dump(designs, sys.stdout, indent=2)
        print()
    else:
        for d in designs:
            print("\t".join(d[k] for k in FIELDS))


if __name__ == "__main__":
    main()
