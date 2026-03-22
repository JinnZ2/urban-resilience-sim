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
├── simulator.py       — Interactive CLI that ties all modules together (entry point)
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
└── salvage.py         (no internal deps)
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

### Constants
- `CALORIES_PER_PERSON_DAY = 2000`
- `GALLONS_PER_PERSON_DAY = 80` (US average domestic)
- `GALLONS_SURVIVAL_MINIMUM = 2`
- Scoring uses additive point systems capped at 100 via `min(100, score)`

## Testing

No formal test suite exists. Each module can be run standalone to verify output. When adding tests, use `unittest` from the standard library (no external test runners) to maintain the zero-dependency constraint.

## Adding New Modules

1. Create `new_module.py` with the standard docstring header
2. Define dataclasses for the domain model
3. Add scoring/assessment functions returning `dict`
4. Add a `*_report()` function returning formatted `str`
5. Add `if __name__ == "__main__"` demo using Fairmont, MN data
6. Import and integrate in `simulator.py` if it needs a menu entry

## Important Design Principles

- **Zero dependencies** — only Python 3 standard library. This is intentional: the tool is designed for conditions where package managers may be unavailable.
- **Offline-first** — no network calls, no API keys, no cloud services.
- **Practical over precise** — models use simplified math with documented assumptions. The goal is actionable community planning, not academic precision.
- **All reports are text-based** — designed for terminal output, potentially without Unicode support beyond basic block characters.
