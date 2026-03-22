#!/usr/bin/env python3
"""
simulator.py — Interactive Urban Resilience Simulator
Urban Resilience Simulator
License: CC0

Zero dependencies. Models community resilience under stress.
Usage: python simulator.py
"""

import sys
from community import (
    CommunityProfile, community_report,
    local_production_capacity, score_infrastructure,
)
from supply_chain import (
    SCENARIOS, SupplyDisruption, DisruptionType,
    simulate_disruption, disruption_report,
)
from food_system import (
    GrowingSeason, crisis_planting_plan, food_system_report,
    sq_ft_to_feed, CROP_DB,
)
from energy_model import EnergyProfile, energy_report, energy_independence_score
from water_system import WaterInfrastructure, water_report, water_resilience_score
from network import (
    CorridorNetwork, CommunityNode, Connection,
    ConnectionType, TradeGood, network_report,
)


# ── Terminal helpers ──────────────────────────────────────────

def clear():
    print("\033[2J\033[H", end="")


def banner(text, char="=", width=60):
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def prompt(text, default=None):
    if default is not None:
        text = f"{text} [{default}]"
    val = input(f"  {text}: ").strip()
    if not val and default is not None:
        return str(default)
    return val


def prompt_float(text, default=0.0):
    val = prompt(text, default)
    try:
        return float(val)
    except ValueError:
        return default


def prompt_int(text, default=0):
    val = prompt(text, default)
    try:
        return int(val)
    except ValueError:
        return default


def prompt_bool(text, default=False):
    default_str = "Y/n" if default else "y/N"
    val = prompt(f"{text} ({default_str})", None)
    if not val:
        return default
    return val.lower().startswith("y")


def prompt_choice(text, options, default=0):
    print(f"\n  {text}")
    for i, opt in enumerate(options):
        marker = " >> " if i == default else "    "
        print(f"{marker}{i + 1}. {opt}")
    val = prompt("Choice", default + 1)
    try:
        idx = int(val) - 1
        if 0 <= idx < len(options):
            return idx
    except ValueError:
        pass
    return default


def pause():
    input("\n  Press Enter to continue...")


def print_bar(label, value, max_val, width=30):
    filled = int((value / max_val) * width) if max_val > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    print(f"  {label:20s} [{bar}] {value:.0f}/{max_val:.0f}")


# ── Quick community builder ──────────────────────────────────

def build_community() -> CommunityProfile:
    """Interactive community profile builder."""
    banner("BUILD YOUR COMMUNITY PROFILE")

    name = prompt("Community name", "My Town")
    pop = prompt_int("Population", 5000)
    county = prompt("County", "Martin")

    banner("FOOD SYSTEM", char="-")
    grocery = prompt_int("Grocery stores", 1)
    food_days = prompt_float("Days of food on grocery shelves", 3.0)
    gardens = prompt_float("Community garden acres", 0.0)
    farms = prompt_int("Active local farms (growing food, not just commodity)", 0)
    elevator = prompt_bool("Grain elevator present?")

    banner("WATER", char="-")
    municipal = prompt_bool("Municipal water system?", True)
    wells = prompt_int("Private wells in area", 0)
    surface = prompt_int("Surface water sources (lakes, streams)", 0)
    backup_water = prompt_bool("Water plant has backup power?")

    banner("ENERGY", char="-")
    solar = prompt_int("Solar installations (residential/commercial)", 0)
    generators = prompt_int("Backup generators (community-wide)", 0)
    fuel_days = prompt_float("Fuel reserve (days)", 3.0)

    banner("MEDICAL", char="-")
    hospital = prompt_bool("Hospital present?")
    clinic = prompt_bool("Clinic present?", True)
    pharmacy = prompt_int("Pharmacies", 1)

    banner("SOCIAL", char="-")
    skill_holders = prompt_int("Identified skill holders (food, water, mechanical)", 0)
    mutual_aid = prompt_int("Mutual aid / neighborhood networks", 0)
    ham = prompt_int("HAM radio operators", 0)

    return CommunityProfile(
        name=name, population=pop, county=county,
        grocery_stores=grocery, days_food_supply_retail=food_days,
        community_gardens_acres=gardens, active_farms_local=farms,
        grain_elevator_present=elevator,
        municipal_water=municipal, wells_private=wells,
        surface_water_sources=surface,
        water_treatment_functional=municipal,
        backup_power_water_plant=backup_water,
        solar_installations=solar,
        backup_generators=generators, fuel_reserve_days=fuel_days,
        hospital_present=hospital, clinic_present=clinic,
        pharmacy_count=pharmacy, ems_available=hospital or clinic,
        skill_holders_identified=skill_holders,
        mutual_aid_networks=mutual_aid,
        ham_radio_operators=ham,
    )


# ── Scenario runner ───────────────────────────────────────────

def run_supply_chain_scenario(profile: CommunityProfile):
    """Run a supply chain disruption scenario."""
    banner("SUPPLY CHAIN DISRUPTION SCENARIOS")

    options = [s.name for s in SCENARIOS] + ["Back"]
    choice = prompt_choice("Select scenario:", options)

    if choice >= len(SCENARIOS):
        return

    scenario = SCENARIOS[choice]
    print(f"\n  Running: {scenario.name}")
    print(f"  {scenario.description}\n")
    print(disruption_report(profile, scenario))
    pause()


# ── Food system planner ──────────────────────────────────────

def run_food_planner(profile: CommunityProfile):
    """Interactive food system planning."""
    banner("FOOD SYSTEM PLANNER")

    acres = prompt_float("Available growing land (acres)", profile.community_gardens_acres or 1.0)
    season_idx = prompt_choice("Current growing season:",
                               ["Dormant (Nov-Mar)", "Early (Apr-May)", "Peak (Jun-Aug)", "Late (Sep-Oct)"])
    season = [GrowingSeason.DORMANT, GrowingSeason.EARLY, GrowingSeason.PEAK, GrowingSeason.LATE][season_idx]

    print(food_system_report(acres, profile.population, season))

    # Show what full self-sufficiency looks like
    full_acres = sq_ft_to_feed(profile.population) / 43560
    print(f"\n  To feed {profile.population:,} people entirely from local land:")
    print(f"    Need: {full_acres:,.0f} acres (intensive production)")
    print(f"    That's {full_acres / 640:.1f} square miles")

    pause()


# ── Energy planner ────────────────────────────────────────────

def run_energy_planner(profile: CommunityProfile):
    """Interactive energy assessment."""
    banner("ENERGY INDEPENDENCE ASSESSMENT")

    energy = EnergyProfile(
        community_name=profile.name,
        population=profile.population,
        solar_mw=profile.solar_installations * 0.005,
        generator_mw=profile.backup_generators * 0.05,
        fuel_gallons=profile.fuel_reserve_days * 50 * profile.backup_generators,
    )
    print(energy_report(energy))
    pause()


# ── Water planner ─────────────────────────────────────────────

def run_water_planner(profile: CommunityProfile):
    """Interactive water assessment."""
    banner("WATER INFRASTRUCTURE ASSESSMENT")

    water = WaterInfrastructure(
        community_name=profile.name,
        population=profile.population,
        treatment_plant=profile.municipal_water,
        treatment_backup_power=profile.backup_power_water_plant,
        private_wells=profile.wells_private,
        surface_sources=profile.surface_water_sources,
        storage_gallons=profile.population * 50,  # estimate
    )
    print(water_report(water))
    pause()


# ── Demo mode ─────────────────────────────────────────────────

def run_demo():
    """Demo with Fairmont data."""
    banner("DEMO: Fairmont, MN — Population 10,000")
    print("  Using estimated data for a typical southern MN community.\n")

    profile = CommunityProfile(
        name="Fairmont, MN", population=10_000, county="Martin",
        grocery_stores=3, days_food_supply_retail=3.0,
        farmers_market=True, community_gardens_acres=0.5,
        active_farms_local=50, grain_elevator_present=True,
        food_bank_present=True,
        municipal_water=True, wells_private=20,
        surface_water_sources=3,
        water_treatment_functional=True,
        backup_power_water_plant=True,
        days_water_reserve=2.0,
        hospital_present=True, clinic_present=True,
        pharmacy_count=3, ems_available=True,
        cell_towers=3, internet_providers=2,
        ham_radio_operators=2, community_alert_system=True,
        highway_access=True, rail_access=True,
        fuel_stations=5, fuel_reserve_days=5.0,
        solar_installations=5, backup_generators=10,
        skill_holders_identified=2, mutual_aid_networks=1,
        faith_communities=8, civic_organizations=5,
    )

    print(community_report(profile))
    pause()

    # Run worst-case scenario
    print(disruption_report(profile, SCENARIOS[1]))
    pause()

    return profile


# ── Main menu ─────────────────────────────────────────────────

def main():
    clear()
    banner("URBAN RESILIENCE SIMULATOR", char="#")
    print("  How long can your community sustain itself?")
    print("  Model infrastructure stress, food production,")
    print("  energy independence, and inter-community networks.")
    print("")
    print("  Zero dependencies. Fully offline.")
    print("  License: CC0 — no rights reserved\n")

    profile = None

    while True:
        options = [
            "New Community Profile — build your town's profile",
            "Demo Mode — Fairmont, MN scenario",
            "Community Report" + (f" — {profile.name}" if profile else " (build profile first)"),
            "Supply Chain Stress Test" + (" — run scenarios" if profile else " (build profile first)"),
            "Food System Planner" + (" — crisis planting" if profile else " (build profile first)"),
            "Energy Assessment" + (" — independence score" if profile else " (build profile first)"),
            "Water Assessment" + (" — grid-down plan" if profile else " (build profile first)"),
            "Crop Database — browse all crops",
            "Quit",
        ]

        choice = prompt_choice("What would you like to do?", options)

        if choice == 0:
            profile = build_community()
            print(community_report(profile))
            pause()

        elif choice == 1:
            profile = run_demo()

        elif choice == 2:
            if profile:
                print(community_report(profile))
                pause()
            else:
                print("\n  Build a profile first (option 1 or 2).")
                pause()

        elif choice == 3:
            if profile:
                run_supply_chain_scenario(profile)
            else:
                print("\n  Build a profile first.")
                pause()

        elif choice == 4:
            if profile:
                run_food_planner(profile)
            else:
                print("\n  Build a profile first.")
                pause()

        elif choice == 5:
            if profile:
                run_energy_planner(profile)
            else:
                print("\n  Build a profile first.")
                pause()

        elif choice == 6:
            if profile:
                run_water_planner(profile)
            else:
                print("\n  Build a profile first.")
                pause()

        elif choice == 7:
            show_crop_database()
            pause()

        elif choice == 8:
            banner("Stay resilient.", char="#")
            break


def show_crop_database():
    """Browse the crop database."""
    banner("CROP DATABASE (Zone 4 Optimized)")

    options = ["All crops", "Fast cycle (crisis planting)", "Calorie crops",
               "Storage crops (winter survival)", "Protein sources"]
    choice = prompt_choice("Filter:", options)

    from food_system import CropType
    filters = {
        0: None,
        1: CropType.FAST_CYCLE,
        2: CropType.CALORIE_CROP,
        3: CropType.STORAGE_CROP,
        4: CropType.PROTEIN,
    }
    crop_filter = filters[choice]

    crops = CROP_DB if crop_filter is None else [c for c in CROP_DB if c.crop_type == crop_filter]

    for c in crops:
        print(f"\n  {c.name} ({c.crop_type.value})")
        print(f"    Days to harvest: {c.days_to_harvest}")
        print(f"    Cal/sq ft:       {c.calories_per_sq_ft}")
        print(f"    Stores:          {c.stores_months} months")
        print(f"    Water:           {c.water_needs}")
        print(f"    Seed saving:     {'Yes' if c.seed_saving else 'No'}")
        if c.notes:
            print(f"    Note: {c.notes}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n")
        banner("Session ended. Stay resilient.", char="#")
        sys.exit(0)
