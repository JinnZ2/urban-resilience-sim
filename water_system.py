"""
water_system.py — Water Infrastructure Resilience
Urban Resilience Simulator
License: CC0

Models municipal water system resilience,
backup capacity, and transition to local sources.
"""

from dataclasses import dataclass
from enum import Enum


class WaterSystemState(Enum):
    NORMAL = "NORMAL"
    CONSERVATION = "CONSERVATION"
    BOIL_ORDER = "BOIL_ORDER"
    RATIONED = "RATIONED"
    FAILED = "FAILED"


@dataclass
class WaterInfrastructure:
    """Community water system profile."""
    community_name: str
    population: int

    # Municipal system
    municipal_source: str = "groundwater"  # "groundwater" | "surface" | "both"
    treatment_plant: bool = True
    treatment_backup_power: bool = False
    distribution_miles: float = 0.0
    storage_gallons: float = 0.0

    # Backup sources
    private_wells: int = 0
    springs_known: int = 0
    surface_sources: int = 0  # streams, lakes, ponds
    rainwater_systems: int = 0

    # Contamination risks
    agricultural_runoff_risk: bool = True
    industrial_contamination: bool = False
    aging_infrastructure_pct: float = 50.0  # % of pipes/system past design life

    # Emergency capacity
    water_trucks_available: int = 0
    purification_knowledge: bool = False  # community knows how to purify
    bulk_storage_gallons: float = 0.0


# ── Water math ────────────────────────────────────────────────

GALLONS_PER_PERSON_DAY = 80          # US average domestic use
GALLONS_SURVIVAL_MINIMUM = 2         # absolute survival drinking
GALLONS_FUNCTIONAL_MINIMUM = 10      # drinking + cooking + sanitation


def water_resilience_score(infra: WaterInfrastructure) -> dict:
    """Score water system resilience."""
    daily_need = infra.population * GALLONS_PER_PERSON_DAY
    survival_need = infra.population * GALLONS_SURVIVAL_MINIMUM
    functional_need = infra.population * GALLONS_FUNCTIONAL_MINIMUM

    # Storage duration
    storage_days_normal = infra.storage_gallons / daily_need if daily_need > 0 else 0
    storage_days_rationed = infra.storage_gallons / functional_need if functional_need > 0 else 0

    # Source redundancy (0-100)
    source_score = 0
    if infra.treatment_plant: source_score += 30
    if infra.treatment_backup_power: source_score += 20
    source_score += min(20, infra.private_wells * 2)
    source_score += min(10, infra.springs_known * 5)
    source_score += min(10, infra.surface_sources * 3)
    source_score += min(10, infra.rainwater_systems * 2)

    # Risk factors
    risk_deduction = 0
    if infra.agricultural_runoff_risk: risk_deduction += 15
    if infra.industrial_contamination: risk_deduction += 20
    if infra.aging_infrastructure_pct > 50: risk_deduction += 10
    if infra.aging_infrastructure_pct > 75: risk_deduction += 10

    resilience = max(0, min(100, source_score - risk_deduction))

    # State classification
    if resilience >= 70 and storage_days_normal >= 3:
        state = WaterSystemState.NORMAL
    elif resilience >= 50:
        state = WaterSystemState.CONSERVATION
    elif resilience >= 30:
        state = WaterSystemState.BOIL_ORDER
    elif resilience >= 15:
        state = WaterSystemState.RATIONED
    else:
        state = WaterSystemState.FAILED

    return {
        "daily_need_gallons": round(daily_need),
        "survival_need_gallons": round(survival_need),
        "functional_need_gallons": round(functional_need),
        "storage_days_normal": round(storage_days_normal, 1),
        "storage_days_rationed": round(storage_days_rationed, 1),
        "source_score": source_score,
        "risk_deduction": risk_deduction,
        "resilience_score": resilience,
        "state": state,
    }


def grid_down_water_plan(infra: WaterInfrastructure) -> list[dict]:
    """What happens to water when power goes out."""
    steps = []
    has_backup = infra.treatment_backup_power

    if not has_backup:
        steps.append({
            "hour": 0,
            "event": "GRID DOWN — water treatment stops",
            "action": "Issue boil-water advisory immediately",
            "note": "Pressure will drop as tower/tank drains",
        })
        if infra.storage_gallons > 0:
            hours = (infra.storage_gallons / (infra.population * GALLONS_FUNCTIONAL_MINIMUM / 24))
            steps.append({
                "hour": round(hours),
                "event": f"Water storage exhausted ({infra.storage_gallons:,.0f} gal)",
                "action": "Switch to emergency sources — wells, surface water with purification",
                "note": f"At functional minimum ({GALLONS_FUNCTIONAL_MINIMUM} gal/person/day)",
            })
    else:
        steps.append({
            "hour": 0,
            "event": "GRID DOWN — backup power activated for water treatment",
            "action": "Implement conservation measures to extend fuel",
            "note": "Treatment continues but fuel-limited",
        })

    # Emergency purification
    if infra.private_wells > 0:
        steps.append({
            "hour": 1,
            "event": f"{infra.private_wells} private wells available (manual pump possible)",
            "action": "Inventory wells that can operate without power",
            "note": "Hand pumps critical — add to community preparedness",
        })

    if infra.surface_sources > 0:
        steps.append({
            "hour": 2,
            "event": f"{infra.surface_sources} surface water sources available",
            "action": "Establish purification stations — boil, filter, or solar treatment",
            "note": "Test for agricultural contamination before use",
        })

    steps.append({
        "hour": 24,
        "event": "Day 1 checkpoint",
        "action": "Assess: is power returning? If not, activate full emergency water protocol",
        "note": "Prioritize water for medical, elderly, children",
    })

    return steps


def water_report(infra: WaterInfrastructure) -> str:
    """Full water infrastructure resilience report."""
    score = water_resilience_score(infra)
    grid_plan = grid_down_water_plan(infra)

    lines = [
        f"{'=' * 60}",
        f"WATER INFRASTRUCTURE REPORT: {infra.community_name}",
        f"{'=' * 60}",
        f"Population:     {infra.population:,}",
        f"Source:         {infra.municipal_source}",
        f"State:          {score['state'].value}",
        f"Resilience:     {score['resilience_score']}/100",
        f"",
        f"── DEMAND ──",
        f"  Normal daily:      {score['daily_need_gallons']:,} gal",
        f"  Functional min:    {score['functional_need_gallons']:,} gal",
        f"  Survival min:      {score['survival_need_gallons']:,} gal",
        f"",
        f"── STORAGE ──",
        f"  Total:             {infra.storage_gallons:,.0f} gal",
        f"  Duration (normal): {score['storage_days_normal']:.1f} days",
        f"  Duration (rationed): {score['storage_days_rationed']:.1f} days",
        f"",
        f"── SOURCES ──",
        f"  Municipal:         {'Yes' if infra.treatment_plant else 'No'}",
        f"  Backup power:      {'Yes' if infra.treatment_backup_power else 'NO'}",
        f"  Private wells:     {infra.private_wells}",
        f"  Springs:           {infra.springs_known}",
        f"  Surface water:     {infra.surface_sources}",
        f"  Rainwater:         {infra.rainwater_systems}",
        f"",
        f"── GRID-DOWN SCENARIO ──",
    ]

    for step in grid_plan:
        lines.append(f"  Hour {step['hour']:3d}: {step['event']}")
        lines.append(f"           → {step['action']}")

    lines.append(f"{'=' * 60}")
    return "\n".join(lines)


if __name__ == "__main__":
    fairmont_water = WaterInfrastructure(
        community_name="Fairmont, MN",
        population=10_000,
        municipal_source="groundwater",
        treatment_plant=True,
        treatment_backup_power=True,
        distribution_miles=50,
        storage_gallons=500_000,
        private_wells=20,
        springs_known=0,
        surface_sources=3,  # chain of lakes
        rainwater_systems=2,
        agricultural_runoff_risk=True,
        aging_infrastructure_pct=60,
    )
    print(water_report(fairmont_water))
