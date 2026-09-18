# H12 Board Template

KiCad-installable project template for new boards in the H12 season.

## What you get

- `HL-Board.kicad_pro` / `.kicad_sch` / `.kicad_pcb` — KiCad 10 defaults
  (design rules, ERC/DRC severities, BOM settings) with `${PROJECTNAME}`
  substitution in the project filename and top-level sheet filename.
- `sym-lib-table` / `fp-lib-table` — project-local library tables pointing
  at the shared `libraries/symbols/` and `libraries/footprints/` folders
  at the repo root, via `${KIPRJMOD}/../../libraries/...`.

## Install (once per machine)

KiCad → **Preferences → Configure Paths → User Templates → Add**, point at
this `templates/h12-board/` folder. KiCad picks it up immediately.

## Create a new board from the template

KiCad → **File → New Project from Template → h12-board** → enter your
project name (e.g. `LPU-v2`). KiCad copies the template, renames the
files to `LPU-v2.kicad_*` and substitutes `${PROJECTNAME}` inside them.
Commit the new folder under `H12/<your-board>/` so the library paths
resolve to `../../libraries/`.

## Layout assumption

The library tables use `${KIPRJMOD}/../../libraries/...` — that is,
**two directory levels under the repo root**. That matches the current
convention `H12/<board>/`. If you place a project elsewhere (e.g.
`extras/<board>/`), edit `sym-lib-table` / `fp-lib-table` after creation
to add or remove `..` segments.

## Files

| File | Committed? | Purpose |
|---|---|---|
| `HL-Board.kicad_pro` | yes | Project settings |
| `HL-Board.kicad_sch` | yes | Root schematic |
| `HL-Board.kicad_pcb` | yes | PCB layout |
| `sym-lib-table` | yes | Project symbol libraries |
| `fp-lib-table` | yes | Project footprint libraries |
| `meta/info.html` | yes | Description shown in template selector |
| `*.kicad_prl` | **no** (ignored) | Per-user UI state |
| `.history/` | **no** (ignored) | KiCad local snapshots |