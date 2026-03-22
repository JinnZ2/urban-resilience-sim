"""
energy_model.py — Energy Independence Model
Urban Resilience Simulator
License: CC0

Models community energy needs, local generation capacity,
and transition pathways when grid becomes unreliable.
"""

from dataclasses import dataclass
from enum import Enum


class GridState(Enum):
    STABLE = "STABLE"
    BROWNOUTS = "BROWNOUTS"
    ROLLING_BLACKOUTS = "ROLLING_BLACKOUTS"
    GRID_DOWN = "GRID_DOWN"
    ISLANDED = "ISLANDED"  # running on local generation


@dataclass
class EnergyProfile:
    """Community energy snapshot."""
    community_name: str
    population: int

    # Current demand (MW)
    peak_demand_mw: float = 0.0
    base_demand_mw: float = 0.0

    # Generation
    grid_import_mw: float = 0.0
    solar_mw: float = 0.0
    wind_mw: float = 0.0
    biomass_mw: float = 0.0
    hydro_mw: float = 0.0
    generator_mw: float = 0.0

    # Storage
    battery_mwh: float = 0.0
    fuel_gallons: float = 0.0

    # Critical loads (MW) — must keep running
    water_treatment_mw: float = 0.05
    hospital_mw: float = 0.2
    communication_mw: float = 0.01
    food_storage_mw: float = 0.1  # refrigeration


def estimate_demand(population: int) -> dict:
    """Estimate community power demand from population."""
    # US avg: ~1.2 kW per person (residential)
    # Small town: lower due to less commercial/industrial
    residential_mw = population * 0.001  # 1 kW per person
    commercial_mw = residential_mw * 0.3
    critical_mw = 0.05 + 0.01 + 0.1  # water + comms + food storage
    if population > 5000:
        critical_mw += 0.2  # hospital

    return {
        "residential_mw": round(residential_mw, 2),
        "commercial_mw": round(commercial_mw, 2),
        "critical_mw": round(critical_mw, 2),
        "total_base_mw": round(residential_mw + commercial_mw, 2),
        "total_peak_mw": round((residential_mw + commercial_mw) * 1.5, 2),
    }


def energy_independence_score(profile: EnergyProfile) -> dict:
    """Score how energy-independent a community is."""
    local_gen = profile.solar_mw + profile.wind_mw + profile.biomass_mw + profile.hydro_mw
    total_gen = local_gen + profile.generator_mw
    critical_load = (profile.water_treatment_mw + profile.hospital_mw +
                     profile.communication_mw + profile.food_storage_mw)

    demand = profile.base_demand_mw if profile.base_demand_mw > 0 else estimate_demand(profile.population)["total_base_mw"]

    # Can we cover critical loads?
    critical_covered = total_gen >= critical_load
    # Can we cover base demand?
    base_covered = total_gen >= demand

    # Generator runtime
    gen_hours = 0
    if profile.generator_mw > 0 and profile.fuel_gallons > 0:
        # ~15 gal/hr per MW for diesel
        gal_per_hour = profile.generator_mw * 15
        gen_hours = profile.fuel_gallons / gal_per_hour if gal_per_hour > 0 else 0

    # Battery hours at critical load
    battery_hours = profile.battery_mwh / critical_load if critical_load > 0 else 0

    independence_pct = (local_gen / demand * 100) if demand > 0 else 0

    if independence_pct >= 100:
        state = GridState.ISLANDED
    elif independence_pct >= 50:
        state = GridState.BROWNOUTS
    elif independence_pct >= 20:
        state = GridState.ROLLING_BLACKOUTS
    else:
        state = GridState.GRID_DOWN

    return {
        "local_generation_mw": round(local_gen, 3),
        "total_generation_mw": round(total_gen, 3),
        "base_demand_mw": round(demand, 2),
        "critical_load_mw": round(critical_load, 3),
        "independence_pct": round(independence_pct, 1),
        "critical_loads_covered": critical_covered,
        "base_loads_covered": base_covered,
        "generator_hours": round(gen_hours, 1),
        "battery_hours_critical": round(battery_hours, 1),
        "grid_down_state": state,
    }


def energy_transition_plan(profile: EnergyProfile) -> list[dict]:
    """Generate prioritized energy transition steps."""
    score = energy_independence_score(profile)
    steps = []

    critical_load = score["critical_load_mw"]

    # Priority 1: Cover critical loads
    if not score["critical_loads_covered"]:
        deficit = critical_load - score["total_generation_mw"]
        solar_panels = int(deficit / 0.005) + 1  # ~5kW panels
        steps.append({
            "priority": 1,
            "action": f"Install {solar_panels} x 5kW solar systems for critical loads",
            "impact": f"Covers {critical_load:.3f} MW critical demand",
            "timeline": "Month 1-3",
            "cost_note": "Focus on water treatment + communication first",
        })

    # Priority 2: Battery storage for overnight
    if score["battery_hours_critical"] < 12:
        needed_mwh = critical_load * 12 - profile.battery_mwh
        steps.append({
            "priority": 2,
            "action": f"Add {needed_mwh:.1f} MWh battery storage",
            "impact": "12 hours overnight coverage for critical systems",
            "timeline": "Month 1-6",
            "cost_note": "Used EV batteries as alternative source",
        })

    # Priority 3: Community solar
    if score["independence_pct"] < 50:
        needed_mw = score["base_demand_mw"] * 0.5 - profile.solar_mw
        acres_needed = needed_mw / 0.2  # ~5 acres per MW
        steps.append({
            "priority": 3,
            "action": f"Community solar farm: {needed_mw:.1f} MW ({acres_needed:.0f} acres)",
            "impact": "50% energy independence",
            "timeline": "Year 1-2",
            "cost_note": "Can co-locate with grazing or pollinator habitat",
        })

    # Priority 4: Biomass/biogas
    if profile.biomass_mw == 0:
        steps.append({
            "priority": 4,
            "action": "Establish biomass/biogas generation from agricultural waste",
            "impact": "Baseload power that runs 24/7 (unlike solar/wind)",
            "timeline": "Year 1-3",
            "cost_note": "Manure digesters serve dual purpose with ecological recovery",
        })

    # Priority 5: Wind
    if profile.wind_mw == 0:
        steps.append({
            "priority": 5,
            "action": "Community wind turbine (1-2 MW)",
            "impact": "Complements solar (generates at night/winter)",
            "timeline": "Year 2-5",
            "cost_note": "Southern MN is excellent wind resource",
        })

    return steps


def energy_report(profile: EnergyProfile) -> str:
    """Full energy assessment report."""
    score = energy_independence_score(profile)
    plan = energy_transition_plan(profile)

    lines = [
        f"{'=' * 60}",
        f"ENERGY INDEPENDENCE REPORT: {profile.community_name}",
        f"{'=' * 60}",
        f"Population:        {profile.population:,}",
        f"Base demand:       {score['base_demand_mw']:.2f} MW",
        f"Critical load:     {score['critical_load_mw']:.3f} MW",
        f"",
        f"── GENERATION ──",
        f"  Solar:           {profile.solar_mw:.3f} MW",
        f"  Wind:            {profile.wind_mw:.3f} MW",
        f"  Biomass:         {profile.biomass_mw:.3f} MW",
        f"  Hydro:           {profile.hydro_mw:.3f} MW",
        f"  Generator:       {profile.generator_mw:.3f} MW ({score['generator_hours']:.0f} hrs fuel)",
        f"  TOTAL LOCAL:     {score['local_generation_mw']:.3f} MW",
        f"",
        f"  Independence:    {score['independence_pct']:.1f}%",
        f"  Critical covered: {'YES' if score['critical_loads_covered'] else 'NO'}",
        f"  Grid-down state: {score['grid_down_state'].value}",
        f"  Battery backup:  {score['battery_hours_critical']:.1f} hrs (critical loads)",
        f"",
    ]

    if plan:
        lines.append(f"── TRANSITION PLAN ──")
        for step in plan:
            lines += [
                f"  [{step['priority']}] {step['action']}",
                f"      Impact:   {step['impact']}",
                f"      Timeline: {step['timeline']}",
            ]

    lines.append(f"{'=' * 60}")
    return "\n".join(lines)


if __name__ == "__main__":
    fairmont = EnergyProfile(
        community_name="Fairmont, MN",
        population=10_000,
        solar_mw=0.025,       # 5 residential installations
        wind_mw=0.0,
        biomass_mw=0.0,
        generator_mw=0.5,     # backup generators combined
        fuel_gallons=2000,
        battery_mwh=0.05,
    )
    print(energy_report(fairmont))
