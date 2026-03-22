"""
community.py — Community Resilience Model
Urban Resilience Simulator
License: CC0

Models a community's resources, population, infrastructure,
and capacity for self-sufficiency under stress.
"""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Optional


class InfraState(Enum):
    FUNCTIONAL = "FUNCTIONAL"
    STRESSED = "STRESSED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class FoodSecurity(Enum):
    SURPLUS = "SURPLUS"           # >120% of caloric need met locally
    ADEQUATE = "ADEQUATE"         # 80-120%
    STRESSED = "STRESSED"         # 40-80%
    CRITICAL = "CRITICAL"         # 10-40%
    CATASTROPHIC = "CATASTROPHIC" # <10%


class WaterSecurity(Enum):
    INDEPENDENT = "INDEPENDENT"   # Local sources sufficient
    ADEQUATE = "ADEQUATE"         # Municipal + backup
    DEPENDENT = "DEPENDENT"       # Municipal only
    RATIONED = "RATIONED"         # Insufficient supply
    CRISIS = "CRISIS"             # No reliable supply


@dataclass
class CommunityProfile:
    """Snapshot of a community's resilience capacity."""
    name: str
    population: int
    county: str
    state: str = "MN"

    # Food system
    grocery_stores: int = 1
    days_food_supply_retail: float = 3.0  # typical grocery turnover
    farmers_market: bool = False
    community_gardens_acres: float = 0.0
    active_farms_local: int = 0
    grain_elevator_present: bool = False
    food_bank_present: bool = False

    # Water
    municipal_water: bool = True
    wells_private: int = 0
    surface_water_sources: int = 0
    water_treatment_functional: bool = True
    backup_power_water_plant: bool = False
    days_water_reserve: float = 1.0

    # Energy
    grid_connected: bool = True
    local_generation_mw: float = 0.0
    solar_installations: int = 0
    wind_capacity_mw: float = 0.0
    backup_generators: int = 0
    fuel_reserve_days: float = 3.0

    # Medical
    hospital_present: bool = False
    clinic_present: bool = True
    pharmacy_count: int = 1
    ems_available: bool = True

    # Communication
    cell_towers: int = 1
    internet_providers: int = 1
    ham_radio_operators: int = 0
    community_alert_system: bool = False

    # Transportation
    highway_access: bool = True
    rail_access: bool = False
    fuel_stations: int = 1

    # Social
    skill_holders_identified: int = 0
    mutual_aid_networks: int = 0
    faith_communities: int = 0
    civic_organizations: int = 0


# ── Caloric math ──────────────────────────────────────────────

CALORIES_PER_PERSON_DAY = 2000
CALORIES_PER_ACRE_GARDEN = 4_000_000   # intensive vegetable garden, annual
CALORIES_PER_ACRE_GRAIN = 6_000_000    # corn/wheat equivalent
CALORIES_PER_ACRE_MIXED = 3_000_000    # mixed subsistence

def daily_caloric_need(population: int) -> float:
    return population * CALORIES_PER_PERSON_DAY

def local_production_capacity(profile: CommunityProfile) -> dict:
    """Estimate local food production vs need."""
    daily_need = daily_caloric_need(profile.population)
    annual_need = daily_need * 365

    garden_calories = profile.community_gardens_acres * CALORIES_PER_ACRE_MIXED
    farm_calories = profile.active_farms_local * 80 * CALORIES_PER_ACRE_GRAIN  # est 80 acres avg

    retail_calories = profile.days_food_supply_retail * daily_need

    total_local_annual = garden_calories + farm_calories
    local_pct = (total_local_annual / annual_need * 100) if annual_need > 0 else 0

    if local_pct >= 120:
        security = FoodSecurity.SURPLUS
    elif local_pct >= 80:
        security = FoodSecurity.ADEQUATE
    elif local_pct >= 40:
        security = FoodSecurity.STRESSED
    elif local_pct >= 10:
        security = FoodSecurity.CRITICAL
    else:
        security = FoodSecurity.CATASTROPHIC

    return {
        "daily_need_calories": daily_need,
        "annual_need_calories": annual_need,
        "garden_annual_calories": garden_calories,
        "farm_annual_calories": farm_calories,
        "retail_buffer_calories": retail_calories,
        "retail_buffer_days": profile.days_food_supply_retail,
        "local_production_pct": round(local_pct, 1),
        "food_security": security,
        "days_until_crisis_no_resupply": round(
            profile.days_food_supply_retail + (total_local_annual / daily_need / 365)
            if daily_need > 0 else 0, 1
        ),
    }


# ── Infrastructure scoring ───────────────────────────────────

def score_infrastructure(profile: CommunityProfile) -> dict:
    """Score infrastructure resilience across domains."""
    scores = {}

    # Water (0-100)
    water = 30 if profile.municipal_water else 0
    water += 20 if profile.water_treatment_functional else 0
    water += 15 if profile.backup_power_water_plant else 0
    water += min(15, profile.wells_private * 3)
    water += min(10, profile.surface_water_sources * 5)
    water += min(10, profile.days_water_reserve * 2)
    scores["water"] = min(100, water)

    if scores["water"] >= 70:
        water_state = WaterSecurity.INDEPENDENT
    elif scores["water"] >= 50:
        water_state = WaterSecurity.ADEQUATE
    elif scores["water"] >= 30:
        water_state = WaterSecurity.DEPENDENT
    else:
        water_state = WaterSecurity.RATIONED

    # Energy (0-100)
    energy = 20 if profile.grid_connected else 0
    energy += min(30, profile.local_generation_mw * 10)
    energy += min(15, profile.solar_installations * 2)
    energy += min(15, profile.wind_capacity_mw * 5)
    energy += min(10, profile.backup_generators * 2)
    energy += min(10, profile.fuel_reserve_days * 2)
    scores["energy"] = min(100, energy)

    # Medical (0-100)
    medical = 30 if profile.hospital_present else 0
    medical += 20 if profile.clinic_present else 0
    medical += min(20, profile.pharmacy_count * 10)
    medical += 15 if profile.ems_available else 0
    scores["medical"] = min(100, medical)

    # Communication (0-100)
    comm = min(20, profile.cell_towers * 10)
    comm += min(20, profile.internet_providers * 10)
    comm += min(30, profile.ham_radio_operators * 10)
    comm += 20 if profile.community_alert_system else 0
    scores["communication"] = min(100, comm)

    # Social cohesion (0-100)
    social = min(20, profile.skill_holders_identified * 2)
    social += min(25, profile.mutual_aid_networks * 10)
    social += min(20, profile.faith_communities * 5)
    social += min(20, profile.civic_organizations * 5)
    social += 15 if profile.community_gardens_acres > 0 else 0
    scores["social_cohesion"] = min(100, social)

    # Transportation (0-100)
    transport = 30 if profile.highway_access else 0
    transport += 20 if profile.rail_access else 0
    transport += min(30, profile.fuel_stations * 10)
    transport += min(20, profile.fuel_reserve_days * 4)
    scores["transportation"] = min(100, transport)

    overall = sum(scores.values()) / len(scores)
    if overall >= 70:
        state = InfraState.FUNCTIONAL
    elif overall >= 50:
        state = InfraState.STRESSED
    elif overall >= 30:
        state = InfraState.DEGRADED
    else:
        state = InfraState.FAILED

    return {
        "scores": scores,
        "overall": round(overall, 1),
        "state": state,
        "water_security": water_state,
    }


# ── Report ────────────────────────────────────────────────────

def community_report(profile: CommunityProfile) -> str:
    """Full community resilience assessment."""
    food = local_production_capacity(profile)
    infra = score_infrastructure(profile)

    lines = [
        f"{'=' * 60}",
        f"COMMUNITY RESILIENCE REPORT: {profile.name}",
        f"{'=' * 60}",
        f"Population:  {profile.population:,}",
        f"Location:    {profile.county} County, {profile.state}",
        f"",
        f"── FOOD SECURITY: {food['food_security'].value} ──",
        f"  Daily caloric need:      {food['daily_need_calories']:,.0f} cal",
        f"  Local production:        {food['local_production_pct']}% of need",
        f"  Retail buffer:           {food['retail_buffer_days']:.0f} days",
        f"  Days to crisis (no resupply): {food['days_until_crisis_no_resupply']}",
        f"",
        f"── INFRASTRUCTURE: {infra['state'].value} (score {infra['overall']}/100) ──",
    ]

    for domain, score in infra["scores"].items():
        bar_len = int(score / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"  {domain.replace('_', ' ').title():20s} [{bar}] {score}/100")

    lines += [
        f"",
        f"  Water security: {infra['water_security'].value}",
        f"{'=' * 60}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # Example: Fairmont, MN — typical southern MN town
    fairmont = CommunityProfile(
        name="Fairmont, MN",
        population=10_000,
        county="Martin",
        grocery_stores=3,
        days_food_supply_retail=3.0,
        farmers_market=True,
        community_gardens_acres=0.5,
        active_farms_local=50,  # surrounding farms — mostly commodity
        grain_elevator_present=True,
        food_bank_present=True,
        municipal_water=True,
        wells_private=20,
        surface_water_sources=3,  # lakes
        water_treatment_functional=True,
        backup_power_water_plant=True,
        days_water_reserve=2.0,
        grid_connected=True,
        local_generation_mw=0.0,
        solar_installations=5,
        wind_capacity_mw=0.0,
        backup_generators=10,
        fuel_reserve_days=5.0,
        hospital_present=True,
        clinic_present=True,
        pharmacy_count=3,
        ems_available=True,
        cell_towers=3,
        internet_providers=2,
        ham_radio_operators=2,
        community_alert_system=True,
        highway_access=True,
        rail_access=True,
        fuel_stations=5,
        skill_holders_identified=2,
        mutual_aid_networks=1,
        faith_communities=8,
        civic_organizations=5,
    )
    print(community_report(fairmont))
