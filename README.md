# reference-designs

Real-world layouts used by [gdsfill](https://github.com/aesc-silicon/gdsfill) and
[gdscheck](https://github.com/aesc-silicon/gdscheck) as CI test inputs. The
designs are not golden references: they exercise the tools on realistic data to
catch crashes, regressions, and density rule violations.

## Layout

Designs are grouped by PDK process, one directory per process, any number of
designs per directory:

```text
<process>/<design-name>.gds.gz
```

## Manifest

`designs.json` lists every design. `name` must be unique across the whole
manifest, and `tools` selects which consumers run the design. An empty `tools`
list keeps a design in the manifest without any consumer running it, for example
while gdscheck does not support its process yet:

```json
{
  "name": "ihp-sg13g2",
  "process": "ihp-sg13g2",
  "path": "ihp-sg13g2/ihp-sg13g2.gds.gz",
  "topcell": "ihp-sg13g2",
  "tools": ["gdscheck", "gdsfill"],
  "source": "",
  "license": "CERN-OHL-W-2.0",
  "notes": ""
}
```

`designs.py` reads the manifest (stdlib only, no dependencies):

```text
./designs.py                          # all designs as TSV: name process path topcell
./designs.py --process ihp-sg13g2     # only one PDK
./designs.py --tool gdsfill           # only designs enabled for gdsfill
./designs.py --json --absolute        # JSON with absolute paths
./designs.py --check                  # validate the manifest
```

## Running gdscheck manually

```text
./designs.py --tool gdscheck --absolute | while IFS=$'\t' read -r name process path topcell; do
  gdscheck run --process "$process" --suite main --topcell "$topcell" --input "$path"
done
```
