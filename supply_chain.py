"""
supply_chain.py — Supply Chain Stress Model
Urban Resilience Simulator
License: CC0

Models supply chain disruption scenarios and cascading effects
on community resilience over time.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from community import CommunityProfile, local_production_capacity, score_infrastructure


class DisruptionType(Enum):
    GRADUAL_DECLINE = "gradual_decline"    # Slow erosion over months
    SUDDEN_STOP = "sudden_stop"            # Trucks stop overnight
    INTERMITTENT = "intermittent"          # On-again off-again
    SELECTIVE = "selective"                # Some goods, not others
    REGIONAL = "regional"                  # Whole region affected


@dataclass
class SupplyDisruption:
    """A supply chain disruption scenario."""
    name: str
    disruption_type: DisruptionType
    severity_pct: float          # 0-100, how much supply is cut
    duration_days: int
    affects_fuel: bool = True
    affects_food: bool = True
    affects_medicine: bool = True
    affects_parts: bool = True   # repair parts, hardware
    description: str = ""


@dataclass
class TimeStep:
    """Community state at a point in time during disruption."""
    day: int
    food_remaining_days: float
    fuel_remaining_days: float
    water_functional: bool
    medical_functional: bool
    population_fed_pct: float
    local_production_active: bool
    community_response: str
    critical_events: list[str] = field(default_factory=list)


# ── Preset scenarios ──────────────────────────────────────────

SCENARIOS = [
    SupplyDisruption(
        "Trucking disruption — fuel shortage",
        DisruptionType.GRADUAL_DECLINE, 60, 30,
        affects_fuel=True, affects_food=True,
        affects_medicine=True, affects_parts=True,
        description="Diesel shortage reduces truck deliveries 60% over 30 days",
    ),
    SupplyDisruption(
        "Regional supply chain collapse",
        DisruptionType.SUDDEN_STOP, 95, 90,
        affects_fuel=True, affects_food=True,
        affects_medicine=True, affects_parts=True,
        description="Major disruption cuts regional supply lines. 90-day duration.",
    ),
    SupplyDisruption(
        "Winter storm — 2 week isolation",
        DisruptionType.SUDDEN_STOP, 100, 14,
        affects_fuel=False, affects_food=True,
        affects_medicine=True, affects_parts=True,
        description="Ice storm isolates community for 2 weeks. Local fuel available.",
    ),
    SupplyDisruption(
        "Agricultural subsidy collapse",
        DisruptionType.GRADUAL_DECLINE, 40, 365,
        affects_fuel=False, affects_food=True,
        affects_medicine=False, affects_parts=False,
        description="Commodity agriculture becomes unviable. Slow food system transition needed.",
    ),
    SupplyDisruption(
        "Grid failure — extended outage",
        DisruptionType.SUDDEN_STOP, 80, 21,
        affects_fuel=True, affects_food=True,
        affects_medicine=True, affects_parts=False,
        description="Regional grid down 3 weeks. Cascading effects on water, food storage.",
    ),
]


# ── Simulation engine ─────────────────────────────────────────

def simulate_disruption(
    profile: CommunityProfile,
    disruption: SupplyDisruption,
    step_days: int = 7,
) -> list[TimeStep]:
    """
    Simulate a disruption scenario over time.
    Returns timeline of community state at each step.
    """
    food_info = local_production_capacity(profile)
    infra = score_infrastructure(profile)

    # Starting state
    food_buffer = profile.days_food_supply_retail
    fuel_buffer = profile.fuel_reserve_days
    water_ok = profile.water_treatment_functional
    medical_ok = profile.hospital_present or profile.clinic_present
    local_production = profile.community_gardens_acres > 0 or profile.active_farms_local > 0

    steps = []
    severity = disruption.severity_pct / 100

    for day in range(0, disruption.duration_days + 1, step_days):
        events = []

        # Consumption vs resupply
        resupply_fraction = 1.0 - severity
        if disruption.disruption_type == DisruptionType.GRADUAL_DECLINE:
            # Severity increases over time
            progress = day / disruption.duration_days if disruption.duration_days > 0 else 1
            resupply_fraction = 1.0 - (severity * progress)

        # Food dynamics
        if disruption.affects_food:
            consumed = step_days
            resupplied = step_days * resupply_fraction
            food_buffer = max(0, food_buffer - consumed + resupplied)
        if food_buffer <= 0:
            events.append("FOOD SUPPLY EXHAUSTED")

        # Fuel dynamics
        if disruption.affects_fuel:
            fuel_consumed = step_days * 0.5  # slower burn
            fuel_resupplied = step_days * 0.5 * resupply_fraction
            fuel_buffer = max(0, fuel_buffer - fuel_consumed + fuel_resupplied)
        if fuel_buffer <= 0 and disruption.affects_fuel:
            events.append("FUEL EXHAUSTED")
            if not profile.backup_power_water_plant:
                water_ok = False
                events.append("WATER TREATMENT OFFLINE (no backup power)")

        # Medical
        if disruption.affects_medicine and day > 14:
            if fuel_buffer <= 0:
                medical_ok = False
                events.append("MEDICAL SERVICES DEGRADED")

        # Community response thresholds
        if day == 0:
            response = "Normal operations"
        elif food_buffer > 5:
            response = "Rationing voluntary"
        elif food_buffer > 2:
            response = "Rationing mandatory"
            events.append("Mandatory rationing in effect")
        elif food_buffer > 0:
            response = "Emergency distribution"
            events.append("Emergency food distribution activated")
        else:
            if local_production:
                response = "Local production mode — community survival"
                events.append("Switched to local food production")
            else:
                response = "CRISIS — no food pipeline, no local production"
                events.append("CRITICAL: No food source available")

        # Fed percentage
        local_daily_cal = 0
        if local_production:
            local_daily_cal = food_info["local_production_pct"]
        fed_pct = min(100, (food_buffer / max(1, step_days)) * 100 * (1 if food_buffer > 0 else 0) + local_daily_cal)

        steps.append(TimeStep(
            day=day,
            food_remaining_days=round(food_buffer, 1),
            fuel_remaining_days=round(fuel_buffer, 1),
            water_functional=water_ok,
            medical_functional=medical_ok,
            population_fed_pct=round(min(100, fed_pct), 1),
            local_production_active=local_production and food_buffer <= 3,
            community_response=response,
            critical_events=events,
        ))

    return steps


# ── Report ────────────────────────────────────────────────────

def disruption_report(
    profile: CommunityProfile,
    disruption: SupplyDisruption,
) -> str:
    """Full disruption simulation report."""
    steps = simulate_disruption(profile, disruption)

    lines = [
        f"{'=' * 60}",
        f"SUPPLY CHAIN DISRUPTION SIMULATION",
        f"{'=' * 60}",
        f"Community:    {profile.name} (pop. {profile.population:,})",
        f"Scenario:     {disruption.name}",
        f"Severity:     {disruption.severity_pct}% supply reduction",
        f"Duration:     {disruption.duration_days} days",
        f"Description:  {disruption.description}",
        f"",
        f"Affects: {'food' if disruption.affects_food else ''}"
        f" {'fuel' if disruption.affects_fuel else ''}"
        f" {'medicine' if disruption.affects_medicine else ''}"
        f" {'parts' if disruption.affects_parts else ''}",
        f"",
        f"── TIMELINE ──",
    ]

    for step in steps:
        lines.append(f"\n  Day {step.day:3d}")
        food_bar_len = int(step.food_remaining_days / 0.5)
        food_bar = "█" * min(30, food_bar_len) + "░" * max(0, 30 - food_bar_len)
        lines.append(f"    Food:   [{food_bar}] {step.food_remaining_days:.1f} days")

        fuel_bar_len = int(step.fuel_remaining_days / 0.3)
        fuel_bar = "█" * min(30, fuel_bar_len) + "░" * max(0, 30 - fuel_bar_len)
        lines.append(f"    Fuel:   [{fuel_bar}] {step.fuel_remaining_days:.1f} days")

        lines.append(f"    Water:  {'✓ OK' if step.water_functional else '✗ OFFLINE'}")
        lines.append(f"    Medical:{'✓ OK' if step.medical_functional else '✗ DEGRADED'}")
        lines.append(f"    Fed:    {step.population_fed_pct:.0f}%")
        lines.append(f"    Status: {step.community_response}")

        for event in step.critical_events:
            lines.append(f"    >> {event}")

    # Summary
    crisis_day = None
    for step in steps:
        if step.food_remaining_days <= 0 and not step.local_production_active:
            crisis_day = step.day
            break

    lines += [
        f"",
        f"── SUMMARY ──",
    ]
    if crisis_day is not None:
        lines.append(f"  !! FOOD CRISIS REACHED: Day {crisis_day}")
        lines.append(f"  !! Without local production, community cannot sustain itself")
    else:
        lines.append(f"  Community survives scenario duration")

    final = steps[-1]
    lines += [
        f"  Final food buffer:   {final.food_remaining_days:.1f} days",
        f"  Final fuel buffer:   {final.fuel_remaining_days:.1f} days",
        f"  Water at end:        {'functional' if final.water_functional else 'OFFLINE'}",
        f"  Local production:    {'active' if final.local_production_active else 'not needed / not available'}",
        f"{'=' * 60}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    from community import CommunityProfile

    fairmont = CommunityProfile(
        name="Fairmont, MN", population=10_000, county="Martin",
        grocery_stores=3, days_food_supply_retail=3.0,
        farmers_market=True, community_gardens_acres=0.5,
        active_farms_local=50, grain_elevator_present=True,
        municipal_water=True, wells_private=20,
        water_treatment_functional=True,
        backup_power_water_plant=True,
        days_water_reserve=2.0,
        hospital_present=True, clinic_present=True,
        fuel_reserve_days=5.0,
        backup_generators=10,
    )

    # Run most severe scenario
    print(disruption_report(fairmont, SCENARIOS[1]))
