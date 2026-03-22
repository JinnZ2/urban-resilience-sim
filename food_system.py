"""
food_system.py — Local Food Production Capacity Model
Urban Resilience Simulator
License: CC0

Models the transition from commodity agriculture to
local food production under stress conditions.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Optional


class GrowingSeason(Enum):
    DORMANT = "DORMANT"         # Nov-Mar in zone 4
    EARLY = "EARLY"             # Apr-May
    PEAK = "PEAK"               # Jun-Aug
    LATE = "LATE"               # Sep-Oct


class CropType(Enum):
    FAST_CYCLE = "fast_cycle"       # 25-60 days
    CALORIE_CROP = "calorie_crop"   # 60-120 days
    STORAGE_CROP = "storage_crop"   # harvest once, stores months
    PERENNIAL = "perennial"         # multi-year establishment
    PROTEIN = "protein"             # beans, livestock


@dataclass
class CropSpec:
    name: str
    crop_type: CropType
    days_to_harvest: int
    calories_per_sq_ft: float   # annual yield
    stores_months: float        # how long it keeps
    zone_min: int
    zone_max: int
    water_needs: str            # "low" | "moderate" | "high"
    soil_tolerance: str
    seed_saving: bool           # can save seed for next year
    notes: str = ""


# ── Crop database (Zone 4 optimized) ─────────────────────────

CROP_DB = [
    # Fast cycle — first food in crisis
    CropSpec("Radish", CropType.FAST_CYCLE, 25, 2.5, 0.5,
             3, 10, "moderate", "Wide tolerance",
             True, "First harvest possible. Marks rows for slower crops"),
    CropSpec("Lettuce", CropType.FAST_CYCLE, 30, 1.5, 0.1,
             3, 10, "moderate", "Prefers loose soil",
             True, "Cut-and-come-again for continuous harvest"),
    CropSpec("Spinach", CropType.FAST_CYCLE, 40, 2.0, 0.1,
             3, 10, "moderate", "Tolerates poor soil",
             True, "Cold tolerant — extend season with row cover"),
    CropSpec("Green beans (bush)", CropType.FAST_CYCLE, 50, 4.0, 0.2,
             3, 10, "moderate", "Fixes nitrogen",
             True, "Nitrogen fixer — improves soil for next crop"),
    CropSpec("Turnip", CropType.FAST_CYCLE, 45, 5.0, 3.0,
             3, 9, "low", "Wide tolerance",
             True, "Root + greens both edible. Stores well"),

    # Calorie crops — sustenance
    CropSpec("Potato", CropType.CALORIE_CROP, 90, 20.0, 6.0,
             3, 10, "moderate", "Loose, well-drained",
             True, "Highest calorie density per square foot. Save seed potatoes"),
    CropSpec("Sweet corn (open-pollinated)", CropType.CALORIE_CROP, 80, 8.0, 0.2,
             4, 9, "moderate", "Rich soil preferred",
             True, "MUST be open-pollinated for seed saving. Dry for cornmeal"),
    CropSpec("Dry beans", CropType.CALORIE_CROP, 90, 6.0, 12.0,
             3, 10, "moderate", "Fixes nitrogen",
             True, "Complete protein with corn. Stores dry for years"),

    # Storage crops — winter survival
    CropSpec("Winter squash", CropType.STORAGE_CROP, 100, 12.0, 6.0,
             3, 10, "moderate", "Rich soil, full sun",
             True, "Butternut stores 6+ months unrefrigerated"),
    CropSpec("Onion", CropType.STORAGE_CROP, 100, 4.0, 8.0,
             3, 10, "moderate", "Well-drained",
             True, "Stores through winter in cool/dry"),
    CropSpec("Carrot", CropType.STORAGE_CROP, 70, 5.0, 5.0,
             3, 10, "moderate", "Loose, deep soil",
             True, "Leave in ground under mulch for winter harvest"),
    CropSpec("Cabbage", CropType.STORAGE_CROP, 80, 3.0, 4.0,
             3, 10, "moderate", "Rich soil",
             True, "Ferment to sauerkraut for 12+ month storage"),
    CropSpec("Garlic", CropType.STORAGE_CROP, 240, 6.0, 10.0,
             3, 8, "low", "Well-drained",
             True, "Plant fall, harvest summer. Stores 10+ months"),

    # Perennials — long-term investment
    CropSpec("Asparagus", CropType.PERENNIAL, 730, 3.0, 0.1,
             3, 8, "low", "Well-drained, established beds",
             False, "2 year establishment, then 20+ years of harvest"),
    CropSpec("Rhubarb", CropType.PERENNIAL, 365, 2.0, 0.1,
             3, 8, "low", "Tolerates poor soil",
             False, "Established plants produce for decades"),
    CropSpec("Jerusalem artichoke", CropType.PERENNIAL, 120, 15.0, 3.0,
             3, 9, "low", "Grows anywhere — invasive",
             True, "Calorie-dense tuber. Spreads aggressively. Hard to kill."),

    # Protein
    CropSpec("Dried peas", CropType.PROTEIN, 70, 5.0, 12.0,
             3, 10, "moderate", "Fixes nitrogen",
             True, "Cool season crop. Complete protein with grain"),
    CropSpec("Sunflower (oil/seed)", CropType.PROTEIN, 80, 4.0, 6.0,
             3, 9, "low", "Wide tolerance",
             True, "Seed, oil, bird feed. Deep taproot breaks soil"),
]


# ── Food system modeling ──────────────────────────────────────

def crisis_planting_plan(
    available_sq_ft: float,
    days_until_need: int,
    growing_season: GrowingSeason,
    people_to_feed: int,
) -> dict:
    """
    Generate immediate planting plan for crisis conditions.
    Prioritizes fastest calories.
    """
    daily_cal_need = people_to_feed * 2000
    plan = []

    # Filter by what can produce in time
    viable = [c for c in CROP_DB if c.days_to_harvest <= days_until_need]
    if growing_season == GrowingSeason.DORMANT:
        viable = []  # can't plant in winter in zone 4

    # Allocation strategy: 60% calorie crops, 25% fast cycle, 15% storage
    calorie_crops = [c for c in viable if c.crop_type == CropType.CALORIE_CROP]
    fast_crops = [c for c in viable if c.crop_type == CropType.FAST_CYCLE]
    storage_crops = [c for c in viable if c.crop_type == CropType.STORAGE_CROP]

    allocations = []

    # If we can grow calorie crops, prioritize them
    if calorie_crops:
        best_calorie = max(calorie_crops, key=lambda c: c.calories_per_sq_ft)
        alloc = available_sq_ft * 0.60
        allocations.append((best_calorie, alloc))

    # Fast crops for immediate food
    if fast_crops:
        best_fast = max(fast_crops, key=lambda c: c.calories_per_sq_ft)
        alloc = available_sq_ft * 0.25
        allocations.append((best_fast, alloc))

    # Storage for winter
    if storage_crops:
        best_storage = max(storage_crops, key=lambda c: c.stores_months)
        alloc = available_sq_ft * 0.15
        allocations.append((best_storage, alloc))

    # If nothing viable, suggest what to prepare for
    if not allocations:
        return {
            "status": "CANNOT_PLANT",
            "reason": f"No crops viable in {growing_season.value} or within {days_until_need} days",
            "prepare_for": "Prepare soil now. First plantable crops in spring.",
            "fastest_option": "Sprouting seeds indoors (any season, 3-7 days to food)",
        }

    total_calories = 0
    plan_details = []
    for crop, sq_ft in allocations:
        annual_cal = crop.calories_per_sq_ft * sq_ft
        seasonal_cal = annual_cal * (crop.days_to_harvest / 365)
        total_calories += annual_cal
        plan_details.append({
            "crop": crop.name,
            "sq_ft": round(sq_ft),
            "days_to_first_harvest": crop.days_to_harvest,
            "annual_calories": round(annual_cal),
            "stores_months": crop.stores_months,
            "save_seed": crop.seed_saving,
        })

    days_fed = total_calories / daily_cal_need if daily_cal_need > 0 else 0

    return {
        "status": "PLAN_READY",
        "total_sq_ft": round(available_sq_ft),
        "crops": plan_details,
        "total_annual_calories": round(total_calories),
        "days_fed_per_year": round(days_fed, 1),
        "pct_of_need": round((days_fed / 365) * 100, 1),
        "gap_calories": max(0, round(daily_cal_need * 365 - total_calories)),
    }


def sq_ft_to_feed(people: int, target_pct: float = 100) -> float:
    """How many square feet needed to feed N people at target %."""
    # Using potato as benchmark (highest cal/sqft)
    best = max(CROP_DB, key=lambda c: c.calories_per_sq_ft)
    cal_needed = people * 2000 * 365 * (target_pct / 100)
    return cal_needed / best.calories_per_sq_ft


def food_system_report(
    available_acres: float,
    people: int,
    season: GrowingSeason,
) -> str:
    """Full food system capacity report."""
    sq_ft = available_acres * 43560
    plan = crisis_planting_plan(sq_ft, 120, season, people)

    lines = [
        f"{'=' * 60}",
        f"FOOD SYSTEM CAPACITY REPORT",
        f"{'=' * 60}",
        f"People to feed:   {people:,}",
        f"Available land:   {available_acres:.1f} acres ({sq_ft:,.0f} sq ft)",
        f"Growing season:   {season.value}",
        f"",
    ]

    if plan["status"] == "CANNOT_PLANT":
        lines += [
            f"  ⚠ {plan['reason']}",
            f"  Prepare: {plan['prepare_for']}",
            f"  Immediate: {plan['fastest_option']}",
        ]
    else:
        lines += [
            f"── CRISIS PLANTING PLAN ──",
            f"  Status: {plan['status']}",
            f"",
        ]
        for crop in plan["crops"]:
            lines += [
                f"  {crop['crop']:25s} {crop['sq_ft']:>8,} sq ft",
                f"    First harvest: {crop['days_to_first_harvest']} days",
                f"    Annual calories: {crop['annual_calories']:,}",
                f"    Storage: {crop['stores_months']} months | Seed saving: {'Yes' if crop['save_seed'] else 'No'}",
            ]
        lines += [
            f"",
            f"  Total annual calories: {plan['total_annual_calories']:,}",
            f"  Days fed per year:     {plan['days_fed_per_year']}",
            f"  % of need met:         {plan['pct_of_need']}%",
        ]
        if plan["gap_calories"] > 0:
            gap_acres = plan["gap_calories"] / (20 * 43560)  # potato benchmark
            lines.append(f"  Calorie gap:           {plan['gap_calories']:,} cal/year")
            lines.append(f"  Additional land needed: ~{gap_acres:.1f} acres (potato equivalent)")

    # How much land to be self-sufficient
    full_acres = sq_ft_to_feed(people) / 43560
    lines += [
        f"",
        f"── SELF-SUFFICIENCY BENCHMARK ──",
        f"  Land to feed {people:,} people (100%): {full_acres:,.1f} acres",
        f"  Land to feed {people:,} people (50%):  {full_acres / 2:,.1f} acres",
        f"  Current land: {available_acres:.1f} acres = {(available_acres / full_acres * 100):.1f}% of full need",
        f"{'=' * 60}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # Fairmont scenario: how much food can we grow?
    print(food_system_report(
        available_acres=10.0,  # community gardens + converted lots
        people=10_000,
        season=GrowingSeason.EARLY,
    ))
