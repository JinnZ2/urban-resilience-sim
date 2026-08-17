# CLAUDE.md — Urban Resilience Simulator

## Project Overview

A systems-dynamics model for community resilience under infrastructure stress. Simulates how small communities (1,000–50,000 people) respond to cascading infrastructure failures — supply chain disruption, energy grid instability, water system compromise — and models recovery pathways using local ecological and human resources.

Companion to the [Fairmont Ecological Recovery](https://github.com/JinnZ2/fairmont-ecological-recovery) framework, consuming its Layer 0–4 outputs (substrate, insects, plants, water, knowledge) to inform resilience scoring.

## Tech Stack

- **Language**: Python 3 (standard library only — zero external dependencies)
- **Design constraint**: Fully offline-capable. No internet, no package manager required.
- **License**: CC0 1.0 Universal (public domain)

## Architecture

```
urban-resilience-sim/
├── community.py       — Core community model: CommunityProfile dataclass, infrastructure scoring, food security assessment
├── supply_chain.py    — Supply chain disruption scenarios and time-step simulation engine
├── food_system.py     — Crop database (Zone 4), crisis planting plans, food capacity modeling
├── energy_model.py    — Energy independence scoring, transition planning, grid-down modeling
├── water_system.py    — Water infrastructure resilience, grid-down water planning
├── network.py         — Inter-community corridor networking, trade matching, Haversine distance
├── salvage.py         — Urban salvage & material recovery: junk/waste → usable resources
├── transition.py      — Leverage analysis + governance/financial pathways from old design to new
├── claims.py          — Assumption ledger: every claim the model rests on, its test status, and its falsification record
├── simulator.py       — Interactive CLI that ties all modules together (entry point)
├── legacy/            — Superseded work, kept with the evidence that retired it
└── CLAUDE.md
```

### Module Dependency Graph

```
simulator.py
├── community.py       (no internal deps)
├── supply_chain.py    → community.py
├── food_system.py     (no internal deps)
├── energy_model.py    (no internal deps)
├── water_system.py    (no internal deps)
├── network.py         (no internal deps)
├── salvage.py         (no internal deps)
├── transition.py      → community.py
└── claims.py          (no internal deps — describes the others, imports none)
```

`community.py` is the foundational module — `CommunityProfile` is the central data structure passed to most subsystem functions.

## Running

```bash
python simulator.py        # Interactive CLI (main entry point)
python community.py        # Example community assessment (Fairmont, MN)
python supply_chain.py     # Supply chain stress scenario demo
python food_system.py      # Food system capacity report
python energy_model.py     # Energy independence report
python water_system.py     # Water infrastructure report
python network.py          # Corridor network report
python salvage.py          # Salvage & material recovery report
python transition.py       # Leverage ranking, phased transition pathway, one instrument
python claims.py           # Assumption ledger, a claim lineage, and open unknowns
```

Every module has an `if __name__ == "__main__"` block with a Fairmont, MN demo.

## Code Conventions

### Style
- **snake_case** for functions and variables
- **PascalCase** for classes and enums
- **UPPER_SNAKE_CASE** for constants
- Module-level docstrings follow the pattern: `"""module.py — Description\nUrban Resilience Simulator\nLicense: CC0"""`
- Section separators use `# ── Section Name ──` with box-drawing characters

### Patterns
- **Dataclasses** for all data models (`@dataclass`), with default values for optional fields
- **Enums** for categorical states (`Enum`, `IntEnum`) — e.g., `InfraState`, `GridState`, `WaterSystemState`
- **Scoring functions** return `dict` with numeric scores and classification enums
- **Report functions** return formatted `str` (not print directly), named `*_report()`
- **Pure functions** — no global mutable state; all state passed via arguments
- Imports use `from module import SpecificThing` (not `import module`)

### Key Data Structures
- `CommunityProfile` (community.py) — central dataclass with 30+ fields covering food, water, energy, medical, communication, transportation, social capacity
- `SupplyDisruption` / `TimeStep` (supply_chain.py) — scenario definition and simulation state
- `CropSpec` / `CROP_DB` (food_system.py) — crop database with caloric yields, storage life, zone compatibility
- `EnergyProfile` (energy_model.py) — generation capacity, storage, critical loads
- `WaterInfrastructure` (water_system.py) — municipal system, backup sources, contamination risks
- `CorridorNetwork` / `CommunityNode` / `Connection` (network.py) — graph of inter-community links
- `SalvageProfile` / `SalvageSource` / `SALVAGE_DB` (salvage.py) — urban salvage inventory, material recovery, reuse planning
- `Lever` / `LEVER_DB` / `InstrumentSpec` / `INSTRUMENT_DB` (transition.py) — modifications and the legal/financial vehicles that deliver them
- `Claim` / `Observation` / `CLAIM_LEDGER` / `OBSERVATIONS` (claims.py) — the model's assertions, their test status, and the runs filed against them

### Constants
- `CALORIES_PER_PERSON_DAY = 2000`
- `GALLONS_PER_PERSON_DAY = 80` (US average domestic)
- `GALLONS_SURVIVAL_MINIMUM = 2`
- Scoring uses additive point systems capped at 100 via `min(100, score)`

## Leverage & Transition (`transition.py`)

The model can say *what* a community should change. `transition.py` answers the
two questions that follow: which changes are worth the most per dollar, and what
institutional steps actually deliver them.

### Leverage is computed, not asserted

`evaluate_lever()` applies each `Lever` to a real copy of the profile and
re-scores it through `community.score_infrastructure()`. Nothing in `LEVER_DB`
stores a benefit figure. This means the ranking inherits every `SCORE-*` claim
wholesale — if the domain weights are wrong, the ranking is wrong with them and
the leverage calculation cannot detect it. That is claim `TRANS-03`, and it is
the most load-bearing untested assumption in the repo.

Ranking sorts levers that raise the **floor** (the binding constraint) ahead of
levers that only raise the mean. Sorting by mean alone inverts the advice — see
`legacy/2026-08-15-averaging-hid-the-binding-constraint.md`.

### Zero-delta levers are a scoring limit, not a finding

A lever whose domain term is already capped scores zero while still changing the
community. These are flagged `SCORE SATURATED` in the report. Do not read them
as "no benefit"; read them as "the score stopped counting". See `SCORE-02`.

### Instruments carry the governance model

`INSTRUMENT_DB` maps each `Instrument` to its procedural `steps`, `typical_months`,
`money_source`, `reversibility`, and `fails_when`. The `fails_when` field is the
most useful and least verifiable part of each entry — it is practitioner lore,
not statute, and is claimed as such under `TRANS-05`.

`Reversibility.LOW` instruments (GO bonds, revenue bonds, special assessments,
TIF) are surfaced in a **lock-in warning**. Debt service is a fixed claim on
future budgets; it narrows what a future council can respond to, which is a
resilience cost the infrastructure score does not measure. Keep that warning
whenever adding a long-horizon instrument.

### Adding a lever

Give it real `changes` against `CommunityProfile` fields, honest `cost_low` /
`cost_high`, the `instruments` that could actually carry it, and any
`prerequisites`. Then register its cost and lead-time basis under the `TRANS-*`
claims — the same rule as any other number in this repo.

## Assumption Ledger & the Precedence Rule

This project follows the "practical over precise" principle, which means most of
its numbers are estimates. `claims.py` is the accounting for that: it names every
assumption the model rests on, records what happened when one was tested, and
keeps the falsified versions readable.

### The loop

```
hypothesize  →  claim enters CLAIM_LEDGER as UNTESTED
run          →  module executed or output inspected
falsified    →  Observation filed with verdict CONTRADICTS;
                claim marked FALSIFIED — never edited in place
edit claim   →  NEW claim written, revision_of points back,
                superseded_by points forward
unknowns     →  what would be needed to test the successor goes
                into its unknowns list
rerun        →  the successor is observed in turn
```

### The precedence rule

**A falsified claim keeps its precedence.** Wrong versions are not overwritten —
they stay in the ledger with the evidence that killed them, and their ids are
never reused. `lineage(claim_id)` walks any claim back through every version it
replaced, so the history of an idea stays reachable from the working code.
Longer-form records go in `legacy/`, one file per falsification, named
`YYYY-MM-DD-short-slug.md`. See `legacy/README.md` for the archival protocol.

### Working with the ledger

- Statements and observations are **append-only**. To change what a claim says,
  write a new claim — do not edit the old one.
- `audit_ledger()` checks the record's own integrity: duplicate ids, dangling
  `revision_of` / `superseded_by` links, one-way supersession, and claims whose
  declared status disagrees with the observations filed against them. It is
  printed at the foot of `ledger_report()`. Keep it clean.
- `open_unknowns()` / `unknowns_report()` are the "search for unknowns" step —
  the list of what would have to be found out next.
- Constants in the modules carry their claim id in a trailing comment, e.g.
  `CALORIES_PER_PERSON_DAY = 2000  # [FOOD-01] untested`.

### When you change a number

If you change any constant, threshold, or formula in this repo, update the
ledger in the same commit. A number that changes without a claim record is the
one thing this structure is meant to prevent. If a change is prompted by a real
observation, file the `Observation` too — including the date and how it was
observed.

### When a claim is only partly wrong

Use `STRAINED`, not `FALSIFIED`. `STRAINED` means contradicted but not yet
revised — it marks a known problem that has no fix on record. Do not silently
pick a resolution to make the status look better; an open question annotated in
place is more useful than a guess buried in code. `ENERGY-01` is the worked
example.

## Testing

No formal test suite exists. Each module can be run standalone to verify output. When adding tests, use `unittest` from the standard library (no external test runners) to maintain the zero-dependency constraint.

## Adding New Modules

1. Create `new_module.py` with the standard docstring header
2. Define dataclasses for the domain model
3. Add scoring/assessment functions returning `dict`
4. Add a `*_report()` function returning formatted `str`
5. Add `if __name__ == "__main__"` demo using Fairmont, MN data
6. Import and integrate in `simulator.py` if it needs a menu entry
7. **Register every estimate the module introduces as a `Claim` in `claims.py`**,
   with its `basis`, its `falsifier`, and its `unknowns`. Tag the constant in
   the source with its claim id. A new module that adds numbers without adding
   claims is not finished.

## Important Design Principles

- **Zero dependencies** — only Python 3 standard library. This is intentional: the tool is designed for conditions where package managers may be unavailable.
- **Offline-first** — no network calls, no API keys, no cloud services.
- **Practical over precise** — models use simplified math with documented assumptions. The goal is actionable community planning, not academic precision.
- **All reports are text-based** — designed for terminal output, potentially without Unicode support beyond basic block characters.
