# Urban Resilience Simulator

A systems-dynamics model for community resilience under infrastructure stress.
Bridges hyper-local ecological recovery (see [Fairmont Ecological Recovery](https://github.com/JinnZ2/fairmont-ecological-recovery))
with urban/town-scale resource planning.

**Core question:** If the trucks stop coming, how long can your community feed itself,
and what does the transition path look like?

## What This Does

Simulates how a small community (1,000–50,000 people) responds to cascading
infrastructure failures and models recovery pathways using local ecological
and human resources. The simulator covers eight interconnected domains:

- **Supply chain stress** — model disruption scenarios from fuel shortages to full regional collapse, with week-by-week timelines showing food, fuel, water, and medical status
- **Food system planning** — crisis planting plans optimized for Zone 4, a crop database with caloric yields and storage life, and self-sufficiency benchmarks
- **Energy independence** — score local generation capacity, model grid-down scenarios, and generate transition plans (solar, wind, biomass, battery)
- **Water infrastructure** — assess municipal system resilience, model grid-down water failure cascades, and plan emergency purification
- **Salvage & material recovery** — inventory urban junk, abandoned structures, and waste streams; generate prioritized reuse plans turning scrap into shelter, growing infrastructure, energy, tools, and trade goods
- **Inter-community networking** — map corridor connections between towns, match surplus/need for trade, and assess regional resilience
- **Leverage & transition** — rank modifications by resilience bought per dollar, then map each one to the ordinance, bond, co-op, grant, or loan fund that could actually deliver it
- **Stationarity checking** — record the observed climate indicators that bear on the model's historical calibration, and name which assumptions they strain

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
python salvage.py          # Salvage & material recovery report
python transition.py       # Leverage ranking + phased transition pathway
python climate.py          # Observed forcing record + stationarity check
python claims.py           # Assumption ledger — what the model claims, and what's been falsified
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

salvage.py           15-source salvage database (structures, vehicles, waste, scrap)
                     Material recovery estimation across 10 material classes
                     Prioritized reuse planning (growing → water → shelter → energy → tools)
                     Safety notes for each salvage source

transition.py        Leverage analysis — which changes buy the most per dollar
                     20 governance & financial instruments with their real
                     procedural steps, timelines, and failure modes
                     Phased transition pathway with lock-in warnings

climate.py           Observed external forcing baseline with provenance
                     Stationarity check — which claims rest on a moved baseline
                     Honest split: what reaches this model, and what doesn't

claims.py            Assumption ledger — every claim the model rests on
                     Falsification record with two-way supersession links
                     Open-unknowns list and ledger integrity audit

simulator.py         Interactive CLI tying all modules together
                     Community profile builder with guided prompts
                     Menu-driven access to all subsystem reports

legacy/              Superseded work, kept with the evidence that retired it
```

## Most Leveraged Small Modifications

The model can say *what* to change. `transition.py` answers which changes are
worth the most per dollar, and — the part that usually decides the outcome —
what institutional steps actually deliver them.

Leverage is **computed, not asserted**: every lever is applied to a real copy of
the profile and re-scored. Levers that relieve the *binding constraint* sort
ahead of levers that only raise the mean.

```
  lever            cost  pts/$10k  floor  auton  mo  notes
  HOME-SOLAR       $14k      0.59   +5.0   +0.8   9  RELIEVES BINDING
               Unlock household solar: permit guide + loan fund
  SKILLS-MAP       $200    104.00   +0.0   +2.7   3
               Inventory who can actually do things
  MUTUAL-AID       $600     26.67   +0.0   +1.7   6
  HAM-NET           $1k     11.03   +0.0   +1.7   6
```

### Somebody has to pass something

A model can say "add 1 MW of local generation." It cannot add it. `INSTRUMENT_DB`
holds the 20 governance and financial vehicles a small municipality actually has
— ordinance, zoning amendment, budget line, revolving loan fund, special
assessment, franchise fee, revenue bond, GO bond, TIF, co-op formation, joint
powers, mutual aid compact — each with its real procedural steps, how long it
runs, where the money comes from, and **what kills it**.

Transitions are phased by the least demanding instrument that could carry them:

- **Phase 0 — no appropriation.** Ordinances, resolutions, volunteer organizing,
  mutual aid compacts, unlocking private investment. Can begin at the next
  meeting. This phase is also what makes the later ones fundable: a standing
  committee can hold a grant, and a skills inventory is what turns a mutual aid
  agreement into a capability. Doing phase 0 late is the most common way a
  transition stalls.
- **Phase 1 — current budget cycle.** Budget lines, capital plans, grants,
  revolving loan funds. Timing dominates: missing the preliminary levy
  certification deadline costs a full year.
- **Phase 2 — financed.** Bonds, assessments, co-ops, rate riders.

### Lock-in is a resilience cost

Phase 2 instruments get a **lock-in warning**. Debt service and assessments are
fixed claims on future budgets — they narrow what a future council can respond
to. That is a real resilience cost, and the infrastructure score does not measure
it. The cheapest instruments are also the most reversible, which is not a
coincidence.

```bash
python transition.py       # leverage ranking, phased pathway, one instrument
```

## Is This Model Calibrated on a Baseline That Moved?

Every constant here — Zone 4 crop viability, "2 week" winter storm isolation,
grain yields per acre, days of water reserve — is a historical figure used as a
forward estimate. That's an assumption, and `climate.py` makes it one you can
read: `CLIMATE-01`, currently `STRAINED`.

The load-bearing finding in the [2025 State of the Climate
report](https://www.ncei.noaa.gov/bams-state-of-climate) isn't any single record
value. It's that 2025 ranked 2nd–3rd warmest **with no El Niño present** — the
2023–24 records rode a strong El Niño, this one didn't. A record set on a
cyclical boost is a warm year. A record set without one is a moved baseline. The
model assumes the opposite.

Nine claims are now marked as strained by observed data, including two dead
ends worth naming: `CropSpec.zone_min`/`zone_max` are populated for all 17 crops
and **read by nothing** — the database asserts a compatibility check that doesn't
happen — and `SCENARIOS` holds five fixed point estimates with no probability
weighting and no compound events.

### What this deliberately does *not* do

**No constant was changed.** A global indicator doesn't license a specific local
number: knowing growing seasons are lengthening doesn't tell you what Zone 4 corn
yields next year. The strain is recorded, the unknowns are named, the numbers
stay put until something local is measured. Changing them now would produce a
model that is *differently wrong and newly confident* — worse than one that's
honestly stale.

### Most of it doesn't reach this model, and that's stated

Roughly two thirds of the recorded indicators — sea level, Arctic and Antarctic
ice, ocean heat, glacier mass balance, atmospheric CO₂ — are filed with **no
pathway** into any calculation here and listed under their own heading. They're
real; they're not evidence about a town at 1,180 feet in southern Minnesota.
Carrying an alarming number that changes no output is exactly the decorative-
statistic habit the ledger exists to prevent.

Provenance gets verified before entry. These figures arrived cited to a report
"published August 2025 covering the 2025 calendar year" — impossible on its face,
since a report can't cover a year that hasn't ended. Corrected to the 36th
edition, BAMS 107(8), August 2026. The correction is an observation on the
record, not a silent edit.

```bash
python climate.py          # the observed record, and the stationarity check
```

## What This Model Doesn't Know

Most of the numbers in this simulator are estimates. Pretending otherwise would
make it worse than useless in the conditions it's built for, so the estimates
are written down as claims instead — `claims.py` names each one, records what
happened when it was tested, and keeps the versions that turned out wrong.

Right now **67% of the model's active claims have never been checked against
evidence**, and there are 80 open unknowns on the list. That number is meant to
be uncomfortable. It's also the honest one.

### The loop

```
hypothesize  →  run  →  falsified  →  edit claim  →  unknowns  →  rerun
```

Two worked examples are in [`legacy/`](legacy/).

The days-to-crisis formula divided a day count by 365, adding years to days, and
reported that a town holding three years of food would reach crisis in 6.3 days.
Its own adjacent output — 328.8% annual surplus — is what exposed it.

The overall score was an unweighted mean of six domains, which reported Fairmont
as FUNCTIONAL while its energy domain sat at 50. That looked cosmetic until the
leverage analysis ranked a $200 skills inventory **176× above** the one small
lever that actually moved the binding domain. A score that inverts the advice is
worse than a score that is merely imprecise. The state is now held down to the
weakest domain.

Each record keeps the falsified version, its output, the reasoning, the fix, and
what is *still* unknown about the successor.

### Precedence still carries

A falsified claim isn't deleted and its id is never reused. The wrong version
stays with the evidence that killed it and a pointer to what replaced it, so
the next person to look at a number can see whether it's already been tried and
rejected — and why. `lineage()` walks any claim back through every revision.

```bash
python claims.py           # full ledger, a worked lineage, and the unknowns list
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
