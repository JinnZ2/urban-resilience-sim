# Urban Resilience Simulator

A systems-dynamics model for community resilience under infrastructure stress.
Bridges hyper-local ecological recovery (see [Fairmont Ecological Recovery](https://github.com/JinnZ2/fairmont-ecological-recovery))
with urban/town-scale resource planning.

**Core question:** If the trucks stop coming, how long can your community feed itself,
and what does the transition path look like?

## What This Does

Simulates how a small community (1,000–50,000 people) responds to cascading
infrastructure failures and models recovery pathways using local ecological
and human resources. The simulator covers five interconnected domains:

- **Supply chain stress** — model disruption scenarios from fuel shortages to full regional collapse, with week-by-week timelines showing food, fuel, water, and medical status
- **Food system planning** — crisis planting plans optimized for Zone 4, a crop database with caloric yields and storage life, and self-sufficiency benchmarks
- **Energy independence** — score local generation capacity, model grid-down scenarios, and generate transition plans (solar, wind, biomass, battery)
- **Water infrastructure** — assess municipal system resilience, model grid-down water failure cascades, and plan emergency purification
- **Inter-community networking** — map corridor connections between towns, match surplus/need for trade, and assess regional resilience

## Running

```bash
python simulator.py        # Interactive CLI — build a community profile and run scenarios
```

Each module also runs standalone with a built-in Fairmont, MN demo:

```bash
python community.py        # Community resilience assessment
python supply_chain.py     # Supply chain stress scenario (regional collapse)
python food_system.py      # Food system capacity report
python energy_model.py     # Energy independence report
python water_system.py     # Water infrastructure report
python network.py          # Corridor network and trade matching
```

## Architecture

```
community.py         CommunityProfile dataclass — the central data model
                     Infrastructure scoring across 6 domains (water, energy,
                     medical, communication, social cohesion, transportation)
                     Food security classification (surplus → catastrophic)

supply_chain.py      5 preset disruption scenarios (fuel shortage, regional
                     collapse, winter storm, subsidy collapse, grid failure)
                     Time-step simulation engine with cascading effects

food_system.py       17-crop database optimized for Zone 4 growing conditions
                     Crisis planting plan generator (60% calorie / 25% fast / 15% storage)
                     Self-sufficiency calculator (sq ft to feed N people)

energy_model.py      Energy profile modeling (solar, wind, biomass, hydro, generators)
                     Independence scoring and grid-down state classification
                     5-priority transition plan generator

water_system.py      Municipal system resilience scoring with risk deductions
                     Grid-down water failure timeline (hour-by-hour)
                     Emergency source planning (wells, surface, rainwater)

network.py           Graph-based corridor network (communities as nodes)
                     Haversine distance calculation for geographic proximity
                     Resource surplus/need matching across communities

simulator.py         Interactive CLI tying all modules together
                     Community profile builder with guided prompts
                     Menu-driven access to all subsystem reports
```

## Zero Dependencies

Pure Python 3 standard library. No internet required. No pip, no venv, no package manager.

This is intentional — the tool is designed for the same conditions as the ecological
recovery framework. If you need this tool, you may not have package managers available.

## Integration with Ecological Recovery Framework

This simulator consumes Layer 0–4 outputs from the [Fairmont framework](https://github.com/JinnZ2/fairmont-ecological-recovery):

| Layer | Framework Output | Simulator Input |
|-------|-----------------|-----------------|
| Layer 0 (Substrate) | Soil quality mapping | Local food production potential |
| Layer 1–2 (Insects/Plants) | Ecosystem recovery timeline | Ecosystem service availability |
| Layer 3 (Water) | Water recovery modeling | Water system resilience scoring |
| Layer 4 (Knowledge) | Community knowledge mapping | Community capacity modeling |

## License

CC0 1.0 Universal — no rights reserved.
