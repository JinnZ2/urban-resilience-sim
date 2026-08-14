"""
claims.py — Assumption Ledger & Falsification Record
Urban Resilience Simulator
License: CC0

Every number in this simulator is a claim about the world. Most of them
have never been checked. This module makes those claims explicit, records
what happened when they were tested, and keeps the falsified versions
readable instead of deleting them.

The loop:

    hypothesize  →  a claim enters the ledger as UNTESTED
    run          →  an Observation is recorded against it
    falsified    →  the claim is marked FALSIFIED, never edited in place
    edit claim   →  a NEW claim is written with revision_of pointing back
    unknowns     →  what would have to be known to test it is written down
    rerun        →  the successor is observed in turn

PRECEDENCE RULE
    A falsified claim is not deleted and its id is never reused. The
    superseded version keeps its record because knowing what was tried
    and why it failed is worth as much as the current answer. lineage()
    walks any claim back to its origin so the whole chain stays visible.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ── Status vocabulary ─────────────────────────────────────────

class ClaimStatus(Enum):
    UNTESTED = "UNTESTED"       # asserted, never checked against evidence
    SUPPORTED = "SUPPORTED"     # checked, survived the check
    STRAINED = "STRAINED"       # partially contradicted, not yet revised
    FALSIFIED = "FALSIFIED"     # contradicted; must not be relied on
    SUPERSEDED = "SUPERSEDED"   # replaced by a successor claim
    RETIRED = "RETIRED"         # no longer load-bearing anywhere in the code


class Verdict(Enum):
    CONFIRMS = "CONFIRMS"
    CONTRADICTS = "CONTRADICTS"
    INCONCLUSIVE = "INCONCLUSIVE"


# ── Data model ────────────────────────────────────────────────

@dataclass
class Claim:
    """A falsifiable assertion the model depends on."""
    id: str                                 # stable, never reused
    statement: str                          # what is being asserted
    module: str                             # where it is load-bearing
    symbol: str = ""                        # constant or function it lives in
    status: ClaimStatus = ClaimStatus.UNTESTED
    basis: str = ""                         # where the number came from
    falsifier: str = ""                     # what observation would kill it
    unknowns: List[str] = field(default_factory=list)
    revision_of: str = ""                   # claim id this one replaces
    superseded_by: str = ""                 # claim id that replaced this one
    notes: str = ""


@dataclass
class Observation:
    """A recorded run bearing on a claim."""
    claim_id: str
    date: str                               # ISO date, supplied by the recorder
    source: str                             # how it was observed
    finding: str
    verdict: Verdict = Verdict.INCONCLUSIVE


# ── The ledger ────────────────────────────────────────────────
#
# Seeded from the assumptions already embedded in the modules. Most are
# UNTESTED — that is the honest state, not a gap to be papered over.

CLAIM_LEDGER = [

    # ── Food ──
    Claim(
        id="FOOD-01",
        statement="A person requires 2,000 kcal/day to remain functional.",
        module="community.py",
        symbol="CALORIES_PER_PERSON_DAY",
        status=ClaimStatus.UNTESTED,
        basis="Standard adult reference intake used on nutrition labels.",
        falsifier="A community-specific intake survey showing mean need "
                  "outside roughly 1,800-2,400 kcal/day.",
        unknowns=[
            "Age and body-mass distribution of the actual population.",
            "Winter heating load in Zone 4 — cold raises maintenance intake.",
            "Activity level under crisis: manual labor replaces sedentary work.",
        ],
        notes="Under-counts if the population is doing physical recovery work "
              "outdoors in winter, which is the exact scenario modelled.",
    ),
    Claim(
        id="FOOD-02",
        statement="Mixed subsistence growing yields 3,000,000 kcal/acre/year.",
        module="community.py",
        symbol="CALORIES_PER_ACRE_MIXED",
        status=ClaimStatus.UNTESTED,
        basis="Order-of-magnitude figure; original source not recorded.",
        falsifier="Measured harvest from a known plot area over one season.",
        unknowns=[
            "Soil quality — this is a Layer 0 input from the Fairmont framework.",
            "Whether the figure assumes irrigation and amendment inputs.",
            "First-year yields on broken ground are typically far lower.",
        ],
    ),
    Claim(
        id="FOOD-03",
        statement="Grain (corn/wheat equivalent) yields 6,000,000 kcal/acre/year.",
        module="community.py",
        symbol="CALORIES_PER_ACRE_GRAIN",
        status=ClaimStatus.UNTESTED,
        basis="Commodity corn yields at conventional input levels.",
        falsifier="A season of yields without synthetic fertiliser or fuel, "
                  "which is the condition the simulator is modelling.",
        unknowns=[
            "Yield decay without synthetic nitrogen — plausibly 40-60% in year one.",
            "Fuel availability for planting and harvest equipment.",
            "Drying and storage energy for wet-harvest corn.",
        ],
        notes="This is the single largest term in the Fairmont demo. If it is "
              "wrong, the headline food-security number is wrong.",
    ),
    Claim(
        id="FOOD-04",
        statement="Intensive vegetable gardening yields 4,000,000 kcal/acre/year.",
        module="community.py",
        symbol="CALORIES_PER_ACRE_GARDEN",
        status=ClaimStatus.RETIRED,
        basis="Order-of-magnitude figure; original source not recorded.",
        falsifier="n/a — the constant is not referenced by any code path.",
        unknowns=[],
        notes="Defined but never used: local_production_capacity() scores "
              "community garden acreage with CALORIES_PER_ACRE_MIXED instead. "
              "Retained as a documented dead constant rather than silently "
              "deleted — see legacy/README.md. Either gardens should use it, "
              "or it should go; that decision needs a real yield observation.",
    ),
    Claim(
        id="FOOD-05",
        statement="The average local farm counted in a profile is 80 acres.",
        module="community.py",
        symbol="local_production_capacity()",
        status=ClaimStatus.UNTESTED,
        basis="Inline estimate, no source recorded.",
        falsifier="County agricultural census average farm size.",
        unknowns=[
            "Actual mean farm size in the modelled county.",
            "Whether 'active_farms_local' counts operations or parcels — "
            "an operation may run many non-contiguous parcels.",
        ],
    ),
    Claim(
        id="FOOD-06",
        statement="Days to crisis without resupply = retail buffer days + "
                  "(annual local calories / daily need / 365).",
        module="community.py",
        symbol="local_production_capacity()['days_until_crisis_no_resupply']",
        status=ClaimStatus.FALSIFIED,
        basis="Original formulation, committed 3730556.",
        falsifier="Dimensional analysis of the second term.",
        unknowns=[],
        superseded_by="FOOD-07",
        notes="Dimensionally incoherent: (annual kcal / daily kcal) is already "
              "a count of DAYS. Dividing by 365 converts it to years, which is "
              "then added to a figure in days. See legacy/ for the full record.",
    ),
    Claim(
        id="FOOD-07",
        statement="Days to crisis without resupply = retail buffer days + "
                  "(annual local calories / daily need).",
        module="community.py",
        symbol="local_production_capacity()['days_until_crisis_no_resupply']",
        status=ClaimStatus.SUPPORTED,
        basis="Revision of FOOD-06 after dimensional falsification.",
        falsifier="An actual community running its stores down to zero — or a "
                  "showing that stored annual output is not in fact drawable "
                  "at a constant daily rate.",
        unknowns=[
            "Harvest timing: annual production is not available on day one. A "
            "failure in March has a very different curve than one in October.",
            "Storage losses — spoilage, rodents, freezing — over a year.",
            "Whether the harvest can be processed and stored at all without "
            "grid power (drying, canning, refrigeration).",
        ],
        revision_of="FOOD-06",
        notes="Dimensionally sound, but only an upper bound. The harvest-timing "
              "unknown is the obvious next thing to model.",
    ),
    Claim(
        id="FOOD-08",
        statement="Local commodity farm acreage counts toward the community's "
                  "edible caloric supply.",
        module="community.py",
        symbol="local_production_capacity()",
        status=ClaimStatus.STRAINED,
        basis="Implicit in summing farm acreage into total_local_annual.",
        falsifier="Tracing where a county's actual corn and soy tonnage goes.",
        unknowns=[
            "Share of local acreage in field corn and soy versus food-grade crops.",
            "Whether ethanol and feed-grade output can be diverted to human food, "
            "and what processing that needs.",
            "Local processing capacity — standing corn is not flour.",
        ],
        notes="The Fairmont demo profile itself carries the comment 'mostly "
              "commodity' on active_farms_local, then counts that acreage as "
              "directly edible. Strained by the repo's own annotation.",
    ),
    Claim(
        id="FOOD-09",
        statement="Food security classes are set at 120 / 80 / 40 / 10 percent "
                  "of local caloric need.",
        module="community.py",
        symbol="local_production_capacity()",
        status=ClaimStatus.UNTESTED,
        basis="Chosen thresholds, no source recorded.",
        falsifier="Outcome data from communities at known production ratios.",
        unknowns=[
            "Whether the classes track anything observable, or are labels only.",
        ],
    ),

    # ── Water ──
    Claim(
        id="WATER-01",
        statement="Normal domestic use is 80 gallons/person/day.",
        module="water_system.py",
        symbol="GALLONS_PER_PERSON_DAY",
        status=ClaimStatus.UNTESTED,
        basis="Cited inline as the US average domestic figure.",
        falsifier="Municipal pumping records divided by served population.",
        unknowns=["Whether the local system's real per-capita draw matches."],
    ),
    Claim(
        id="WATER-02",
        statement="Survival drinking minimum is 2 gallons/person/day.",
        module="water_system.py",
        symbol="GALLONS_SURVIVAL_MINIMUM",
        status=ClaimStatus.UNTESTED,
        basis="Common emergency-planning figure.",
        falsifier="Physiological requirement under the actual work and "
                  "temperature conditions modelled.",
        unknowns=["Summer labour raises this substantially."],
    ),
    Claim(
        id="WATER-03",
        statement="Functional minimum including cooking and sanitation is "
                  "10 gallons/person/day.",
        module="water_system.py",
        symbol="GALLONS_FUNCTIONAL_MINIMUM",
        status=ClaimStatus.UNTESTED,
        basis="Common emergency-planning figure.",
        falsifier="Observed consumption in a community actually running at "
                  "reduced supply.",
        unknowns=["Sanitation need scales with disease pressure, not headcount."],
    ),

    # ── Energy ──
    Claim(
        id="ENERGY-01",
        statement="Residential demand is 1.0 kW per person.",
        module="energy_model.py",
        symbol="estimate_demand()",
        status=ClaimStatus.STRAINED,
        basis="Implementation uses population * 0.001 MW.",
        falsifier="Utility load data for the modelled community.",
        unknowns=[
            "Which figure is intended — the code and its own comment disagree.",
            "Small-town load is stated to be lower than the US average, but no "
            "reduction factor is actually applied.",
        ],
        notes="The comment directly above the line states the US average as "
              "~1.2 kW/person; the code implements 1.0 kW/person. One of the "
              "two is wrong and the record does not say which.",
    ),
    Claim(
        id="ENERGY-02",
        statement="Commercial demand is 30% of residential demand.",
        module="energy_model.py",
        symbol="estimate_demand()",
        status=ClaimStatus.UNTESTED,
        basis="Inline ratio, no source recorded.",
        falsifier="Utility rate-class breakdown for the community.",
        unknowns=[
            "A town with a single large industrial load breaks this ratio badly.",
        ],
    ),
    Claim(
        id="ENERGY-03",
        statement="Peak demand is 1.5x base demand.",
        module="energy_model.py",
        symbol="estimate_demand()",
        status=ClaimStatus.UNTESTED,
        basis="Inline ratio, no source recorded.",
        falsifier="Hourly load curve for the community.",
        unknowns=["Winter evening peaks in Zone 4 may exceed this."],
    ),

    # ── Salvage ──
    Claim(
        id="SALVAGE-01",
        statement="A salvage source's recoverable mass divides equally among "
                  "the material classes it contains.",
        module="salvage.py",
        symbol="estimate_material_recovery()",
        status=ClaimStatus.UNTESTED,
        basis="Simplifying assumption: lbs / len(source.materials).",
        falsifier="Weighing the actual output of one stripped source.",
        unknowns=[
            "A junk vehicle is overwhelmingly steel, not equal parts steel, "
            "glass, plastic and mechanical.",
            "Per-source material fractions are not recorded anywhere.",
        ],
        notes="Known to be crude. Flagged rather than fixed because the fix "
              "needs real mass fractions per source type.",
    ),
    Claim(
        id="SALVAGE-02",
        statement="Bulk source multipliers: 20 pallets per pallet source, "
                  "30 appliances per dump site, 500 ft copper wire per site.",
        module="salvage.py",
        symbol="estimate_material_recovery()",
        status=ClaimStatus.UNTESTED,
        basis="Inline estimates, no source recorded.",
        falsifier="Counting one real site of each type.",
        unknowns=["Site-to-site variance is likely larger than the estimate."],
    ),

    # ── Network ──
    Claim(
        id="NET-01",
        statement="Haversine distance on a spherical earth is accurate enough "
                  "for inter-community corridor planning.",
        module="network.py",
        symbol="haversine_distance()",
        status=ClaimStatus.SUPPORTED,
        basis="Spherical approximation of an oblate spheroid.",
        falsifier="A planning decision changed by sub-1% distance error.",
        unknowns=[
            "Road distance, not great-circle distance, is what a truck drives. "
            "The ratio is typically 1.2-1.4x and is not modelled.",
        ],
        notes="Sound for its stated purpose. The unmodelled road-versus-air "
              "factor matters more than the earth's shape.",
    ),

    # ── Scoring ──
    Claim(
        id="SCORE-01",
        statement="Overall infrastructure resilience is the unweighted mean of "
                  "six domain scores.",
        module="community.py",
        symbol="score_infrastructure()",
        status=ClaimStatus.UNTESTED,
        basis="Implementation: sum(scores.values()) / len(scores).",
        falsifier="A community failing from one collapsed domain while its "
                  "mean score stayed comfortable.",
        unknowns=[
            "Equal weighting asserts that communication resilience matters "
            "exactly as much as water. No evidence supports that.",
            "Averaging hides single-domain collapse — the Fairmont demo scores "
            "FUNCTIONAL at 79.7 while energy sits at 50.",
        ],
        notes="A minimum-domain or weighted score would likely behave better. "
              "Left as-is pending a reason to prefer specific weights.",
    ),
    Claim(
        id="SCORE-02",
        statement="Additive point systems capped at 100 produce meaningful "
                  "cross-domain comparability.",
        module="community.py",
        symbol="score_infrastructure()",
        status=ClaimStatus.UNTESTED,
        basis="Design convention across all scoring functions.",
        falsifier="Two communities with equal scores and clearly unequal "
                  "real-world outcomes.",
        unknowns=[
            "Capping compresses the top: a town far past a threshold scores "
            "the same as one barely over it.",
        ],
    ),
    Claim(
        id="SCORE-03",
        statement="Infrastructure states divide at scores of 70 / 50 / 30.",
        module="community.py",
        symbol="score_infrastructure()",
        status=ClaimStatus.UNTESTED,
        basis="Chosen thresholds, no source recorded.",
        falsifier="Outcome data from communities at known scores.",
        unknowns=["Whether the labels track anything observable."],
    ),
    Claim(
        id="SIM-01",
        statement="Municipal water storage is 50 gallons per resident.",
        module="simulator.py",
        symbol="run_demo()",
        status=ClaimStatus.UNTESTED,
        basis="Inline estimate marked '# estimate'.",
        falsifier="Tower and reservoir capacity from the utility.",
        unknowns=[
            "Real storage is sized to fire-flow and peak-hour rules, which "
            "do not scale linearly with population.",
        ],
    ),
]


# ── Observations ──────────────────────────────────────────────
#
# Each entry is a run that bore on a claim. Add, never edit.

OBSERVATIONS = [
    Observation(
        claim_id="FOOD-06",
        date="2026-08-14",
        source="Dimensional analysis + `python community.py` demo output",
        finding="The Fairmont demo reports local production at 328.8% of annual "
                "need — a full-year surplus — while simultaneously reporting "
                "'Days to crisis (no resupply): 6.3'. Both cannot hold. "
                "Tracing the term: 24,001,500,000 annual kcal / 20,000,000 "
                "kcal-per-day = 1,200.08 days of local supply; the extra /365 "
                "converts that to 3.29 YEARS, which is then added to 3 days of "
                "retail buffer as though it were days, giving 6.3. Correct "
                "value: 1,203.1.",
        verdict=Verdict.CONTRADICTS,
    ),
    Observation(
        claim_id="FOOD-07",
        date="2026-08-14",
        source="Recomputation of the Fairmont demo after revision",
        finding="Days to crisis now reports 1,203.1, consistent with a stated "
                "328.8% annual surplus. Dimensionally coherent. Still an upper "
                "bound: it assumes the whole annual harvest is in hand and "
                "drawable at a flat daily rate from day one.",
        verdict=Verdict.CONFIRMS,
    ),
    Observation(
        claim_id="FOOD-04",
        date="2026-08-14",
        source="Reference search across the module set",
        finding="CALORIES_PER_ACRE_GARDEN is defined at community.py:98 and "
                "referenced nowhere. Community garden acreage is scored with "
                "CALORIES_PER_ACRE_MIXED at community.py:110.",
        verdict=Verdict.CONTRADICTS,
    ),
    Observation(
        claim_id="FOOD-08",
        date="2026-08-14",
        source="Code inspection of the demo profile",
        finding="The Fairmont profile sets active_farms_local=50 with the "
                "inline comment 'surrounding farms — mostly commodity', and "
                "that acreage is then counted as edible calories at "
                "CALORIES_PER_ACRE_GRAIN. The repo contradicts itself in the "
                "space of two lines.",
        verdict=Verdict.CONTRADICTS,
    ),
    Observation(
        claim_id="ENERGY-01",
        date="2026-08-14",
        source="Code inspection",
        finding="energy_model.py states 'US avg: ~1.2 kW per person' in a "
                "comment, then implements population * 0.001 MW = 1.0 kW per "
                "person on the line below. A further comment says small-town "
                "load should be lower still, but no reduction is applied.",
        verdict=Verdict.CONTRADICTS,
    ),
    Observation(
        claim_id="SCORE-01",
        date="2026-08-14",
        source="`python community.py` demo output",
        finding="Fairmont scores FUNCTIONAL overall at 79.7/100 while its "
                "energy domain sits at 50.0 — the weakest domain is invisible "
                "in the headline. Averaging is masking the binding constraint.",
        verdict=Verdict.INCONCLUSIVE,
    ),
    Observation(
        claim_id="NET-01",
        date="2026-08-14",
        source="Error-bound reasoning",
        finding="Spherical-earth error is under ~0.5% at corridor ranges of "
                "10-200 km, far below the road-versus-great-circle factor of "
                "1.2-1.4x that is not modelled at all. Adequate for its stated "
                "purpose under 'practical over precise'.",
        verdict=Verdict.CONFIRMS,
    ),
]


# ── Queries ───────────────────────────────────────────────────

def claim_by_id(claim_id: str, ledger: Optional[List[Claim]] = None) -> Optional[Claim]:
    """Look up a single claim. Returns None if the id is unknown."""
    ledger = CLAIM_LEDGER if ledger is None else ledger
    for claim in ledger:
        if claim.id == claim_id:
            return claim
    return None


def lineage(claim_id: str, ledger: Optional[List[Claim]] = None) -> List[Claim]:
    """Walk a claim back through every version it replaced.

    Returns oldest-first, so the list reads as the history of the idea.
    This is the precedence rule in code: a superseded claim stays
    reachable from its successor forever.
    """
    ledger = CLAIM_LEDGER if ledger is None else ledger
    chain = []
    seen = set()
    current = claim_by_id(claim_id, ledger)
    while current is not None and current.id not in seen:
        seen.add(current.id)
        chain.append(current)
        current = claim_by_id(current.revision_of, ledger) if current.revision_of else None
    chain.reverse()
    return chain


def observations_for(claim_id: str,
                     observations: Optional[List[Observation]] = None) -> List[Observation]:
    """Every recorded run bearing on one claim."""
    observations = OBSERVATIONS if observations is None else observations
    return [o for o in observations if o.claim_id == claim_id]


def open_unknowns(ledger: Optional[List[Claim]] = None) -> List[dict]:
    """The 'search for unknowns' step, collected across the ledger.

    Retired and superseded claims are skipped — their unknowns belong to
    whatever replaced them.
    """
    ledger = CLAIM_LEDGER if ledger is None else ledger
    live = (ClaimStatus.UNTESTED, ClaimStatus.SUPPORTED,
            ClaimStatus.STRAINED, ClaimStatus.FALSIFIED)
    out = []
    for claim in ledger:
        if claim.status not in live or not claim.unknowns:
            continue
        out.append({
            "claim_id": claim.id,
            "module": claim.module,
            "status": claim.status,
            "statement": claim.statement,
            "unknowns": list(claim.unknowns),
        })
    return out


def ledger_summary(ledger: Optional[List[Claim]] = None,
                   observations: Optional[List[Observation]] = None) -> dict:
    """Counts by status, plus how much of the model rests on unchecked numbers."""
    ledger = CLAIM_LEDGER if ledger is None else ledger
    observations = OBSERVATIONS if observations is None else observations

    counts = {status: 0 for status in ClaimStatus}
    for claim in ledger:
        counts[claim.status] += 1

    active = [c for c in ledger
              if c.status not in (ClaimStatus.SUPERSEDED, ClaimStatus.RETIRED)]
    untested = [c for c in active if c.status == ClaimStatus.UNTESTED]
    unknown_count = sum(len(u["unknowns"]) for u in open_unknowns(ledger))

    return {
        "total_claims": len(ledger),
        "active_claims": len(active),
        "counts": counts,
        "untested_pct": round(100 * len(untested) / len(active), 1) if active else 0.0,
        "observations": len(observations),
        "open_unknowns": unknown_count,
    }


def audit_ledger(ledger: Optional[List[Claim]] = None,
                 observations: Optional[List[Observation]] = None) -> List[str]:
    """Integrity check on the record itself.

    Catches the ways a ledger rots: dangling links, one-way supersession,
    duplicate ids, and claims whose declared status disagrees with the
    observations filed against them.
    """
    ledger = CLAIM_LEDGER if ledger is None else ledger
    observations = OBSERVATIONS if observations is None else observations
    problems = []

    ids = [c.id for c in ledger]
    for claim_id in sorted(set(i for i in ids if ids.count(i) > 1)):
        problems.append(f"{claim_id}: duplicate claim id — ids must never be reused")

    for claim in ledger:
        for link, label in ((claim.revision_of, "revision_of"),
                            (claim.superseded_by, "superseded_by")):
            if link and claim_by_id(link, ledger) is None:
                problems.append(f"{claim.id}: {label} points at unknown claim {link!r}")

        if claim.superseded_by:
            successor = claim_by_id(claim.superseded_by, ledger)
            if successor is not None and successor.revision_of != claim.id:
                problems.append(
                    f"{claim.id}: superseded_by {successor.id}, but {successor.id} "
                    f"does not point back — supersession must be two-way")

        if claim.status == ClaimStatus.SUPERSEDED and not claim.superseded_by:
            problems.append(f"{claim.id}: marked SUPERSEDED with no successor recorded")

        if claim.status in (ClaimStatus.UNTESTED, ClaimStatus.SUPPORTED):
            contradicted = [o for o in observations_for(claim.id, observations)
                            if o.verdict is Verdict.CONTRADICTS]
            if contradicted:
                problems.append(
                    f"{claim.id}: status {claim.status.value} but "
                    f"{len(contradicted)} contradicting observation(s) on file")

        if claim.status == ClaimStatus.UNTESTED:
            conclusive = [o for o in observations_for(claim.id, observations)
                          if o.verdict is not Verdict.INCONCLUSIVE]
            if conclusive:
                problems.append(
                    f"{claim.id}: marked UNTESTED but has conclusive observations on file")

    for obs in observations:
        if claim_by_id(obs.claim_id, ledger) is None:
            problems.append(f"observation references unknown claim {obs.claim_id!r}")

    return problems


# ── Reports ───────────────────────────────────────────────────

def ledger_report(ledger: Optional[List[Claim]] = None,
                  observations: Optional[List[Observation]] = None) -> str:
    """Full assumption ledger, grouped by status."""
    ledger = CLAIM_LEDGER if ledger is None else ledger
    observations = OBSERVATIONS if observations is None else observations
    summary = ledger_summary(ledger, observations)

    lines = [
        "=" * 60,
        "ASSUMPTION LEDGER",
        "=" * 60,
        f"Claims on record:   {summary['total_claims']} "
        f"({summary['active_claims']} active)",
        f"Observations filed: {summary['observations']}",
        f"Open unknowns:      {summary['open_unknowns']}",
        f"Active claims never checked against evidence: {summary['untested_pct']}%",
        "",
    ]

    order = [ClaimStatus.FALSIFIED, ClaimStatus.STRAINED, ClaimStatus.UNTESTED,
             ClaimStatus.SUPPORTED, ClaimStatus.SUPERSEDED, ClaimStatus.RETIRED]

    for status in order:
        group = [c for c in ledger if c.status == status]
        if not group:
            continue
        lines.append(f"── {status.value} ({len(group)}) " + "─" * max(0, 34 - len(status.value)))
        for claim in group:
            lines.append(f"  [{claim.id}] {claim.statement}")
            lines.append(f"      {claim.module} :: {claim.symbol or '—'}")
            if claim.revision_of:
                lines.append(f"      revises:      {claim.revision_of}")
            if claim.superseded_by:
                lines.append(f"      superseded by: {claim.superseded_by}")
            for obs in observations_for(claim.id, observations):
                lines.append(f"      {obs.verdict.value} ({obs.date}): {obs.finding}")
            if claim.unknowns:
                lines.append(f"      unknowns: {len(claim.unknowns)}")
        lines.append("")

    problems = audit_ledger(ledger, observations)
    lines.append("── LEDGER INTEGRITY " + "─" * 26)
    if problems:
        for problem in problems:
            lines.append(f"  ! {problem}")
    else:
        lines.append("  No structural problems found.")
    lines.append("=" * 60)
    return "\n".join(lines)


def lineage_report(claim_id: str,
                   ledger: Optional[List[Claim]] = None,
                   observations: Optional[List[Observation]] = None) -> str:
    """The history of one idea, oldest version first.

    This is what 'precedence still carries' looks like at the terminal:
    the falsified version is still here, still readable, still explaining
    why the current version says what it says.
    """
    ledger = CLAIM_LEDGER if ledger is None else ledger
    observations = OBSERVATIONS if observations is None else observations

    chain = lineage(claim_id, ledger)
    if not chain:
        return f"No claim on record with id {claim_id!r}."

    lines = [
        "=" * 60,
        f"CLAIM LINEAGE: {claim_id}",
        "=" * 60,
    ]
    for depth, claim in enumerate(chain):
        marker = "origin" if depth == 0 else f"revision {depth}"
        lines.append(f"── {marker}: [{claim.id}] {claim.status.value} " +
                     "─" * max(0, 20 - len(claim.status.value)))
        lines.append(f"  {claim.statement}")
        lines.append(f"  in:    {claim.module} :: {claim.symbol or '—'}")
        if claim.basis:
            lines.append(f"  basis: {claim.basis}")
        if claim.falsifier:
            lines.append(f"  falsified by: {claim.falsifier}")
        for obs in observations_for(claim.id, observations):
            lines.append(f"  {obs.verdict.value} ({obs.date}) via {obs.source}:")
            lines.append(f"    {obs.finding}")
        if claim.unknowns:
            lines.append("  still unknown:")
            for unknown in claim.unknowns:
                lines.append(f"    - {unknown}")
        if claim.notes:
            lines.append(f"  note:  {claim.notes}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def unknowns_report(ledger: Optional[List[Claim]] = None) -> str:
    """What would have to be found out — the search list for the next run."""
    ledger = CLAIM_LEDGER if ledger is None else ledger
    items = open_unknowns(ledger)

    lines = [
        "=" * 60,
        "OPEN UNKNOWNS",
        "=" * 60,
        "What the model would need to know to test what it already asserts.",
        "",
    ]
    priority = {ClaimStatus.FALSIFIED: 0, ClaimStatus.STRAINED: 1,
                ClaimStatus.UNTESTED: 2, ClaimStatus.SUPPORTED: 3}
    for item in sorted(items, key=lambda i: (priority.get(i["status"], 9), i["claim_id"])):
        lines.append(f"[{item['claim_id']}] {item['status'].value} — {item['module']}")
        lines.append(f"  {item['statement']}")
        for unknown in item["unknowns"]:
            lines.append(f"    ? {unknown}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


# ── Demo ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print(ledger_report())
    print("")
    print(lineage_report("FOOD-07"))
    print("")
    print(unknowns_report())
