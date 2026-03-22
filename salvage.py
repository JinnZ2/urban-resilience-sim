"""
salvage.py — Urban Salvage & Material Recovery Model
Urban Resilience Simulator
License: CC0

Models the recovery of usable resources from urban waste streams,
abandoned structures, and scrap materials. Turns a community's
junk into survival infrastructure.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MaterialClass(Enum):
    METAL = "metal"                 # scrap steel, copper, aluminum
    LUMBER = "lumber"               # dimensional lumber, plywood, pallets
    MASONRY = "masonry"             # brick, concrete block, stone
    GLASS = "glass"                 # windows, bottles, jars
    PLASTIC = "plastic"             # containers, pipe, sheeting
    TEXTILE = "textile"             # clothing, fabric, tarps
    ORGANIC = "organic"             # food waste, yard waste, paper/cardboard
    MECHANICAL = "mechanical"       # engines, motors, pumps, bearings
    ELECTRICAL = "electrical"       # wire, panels, batteries, inverters
    CHEMICAL = "chemical"           # fertilizer, fuel, solvents, paint


class ReuseCategory(Enum):
    SHELTER = "shelter"             # building repair, insulation, roofing
    GROWING = "growing"             # raised beds, compost, greenhouse material
    ENERGY = "energy"               # fuel, biogas feedstock, battery banks
    WATER = "water"                 # rain catchment, filtration, pipe repair
    TOOLS = "tools"                 # fabricated or repaired hand/power tools
    MEDICAL = "medical"             # sanitization, bandaging, splinting
    TRADE_GOODS = "trade_goods"     # items with barter value in corridor network


class SalvageEffort(Enum):
    MINIMAL = "minimal"             # picking through accessible piles
    MODERATE = "moderate"           # organized sorting, basic disassembly
    INTENSIVE = "intensive"         # demolition, smelting, full processing


# ── Salvage source database ──────────────────────────────────

@dataclass
class SalvageSource:
    """A type of urban salvage source."""
    name: str
    materials: list[MaterialClass]
    reuse_targets: list[ReuseCategory]
    effort: SalvageEffort
    yield_per_unit: float           # lbs of usable material per unit
    units_description: str          # what "per unit" means
    safety_notes: str = ""
    skill_required: str = "none"    # "none" | "basic" | "trades" | "specialist"


SALVAGE_DB = [
    # ── Structures ──
    SalvageSource(
        "Abandoned house (frame)",
        [MaterialClass.LUMBER, MaterialClass.METAL, MaterialClass.GLASS,
         MaterialClass.ELECTRICAL],
        [ReuseCategory.SHELTER, ReuseCategory.ENERGY, ReuseCategory.GROWING],
        SalvageEffort.INTENSIVE, 8000, "per house",
        safety_notes="Check for asbestos, lead paint. Shore before entry.",
        skill_required="trades",
    ),
    SalvageSource(
        "Commercial building (demo)",
        [MaterialClass.METAL, MaterialClass.MASONRY, MaterialClass.ELECTRICAL,
         MaterialClass.MECHANICAL],
        [ReuseCategory.SHELTER, ReuseCategory.TOOLS, ReuseCategory.ENERGY],
        SalvageEffort.INTENSIVE, 25000, "per building",
        safety_notes="Structural assessment required. Heavy equipment preferred.",
        skill_required="specialist",
    ),
    SalvageSource(
        "Pallet stockpile",
        [MaterialClass.LUMBER],
        [ReuseCategory.GROWING, ReuseCategory.SHELTER, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MINIMAL, 40, "per pallet",
        safety_notes="Avoid chemically treated pallets (marked MB is OK, avoid CT).",
        skill_required="none",
    ),

    # ── Vehicles ──
    SalvageSource(
        "Junk vehicle",
        [MaterialClass.METAL, MaterialClass.MECHANICAL, MaterialClass.ELECTRICAL,
         MaterialClass.GLASS, MaterialClass.TEXTILE],
        [ReuseCategory.TOOLS, ReuseCategory.ENERGY, ReuseCategory.SHELTER,
         ReuseCategory.TRADE_GOODS],
        SalvageEffort.MODERATE, 2500, "per vehicle",
        safety_notes="Drain fluids first. Battery acid hazard.",
        skill_required="basic",
    ),
    SalvageSource(
        "Farm equipment (non-functional)",
        [MaterialClass.METAL, MaterialClass.MECHANICAL],
        [ReuseCategory.TOOLS, ReuseCategory.GROWING, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MODERATE, 5000, "per implement",
        safety_notes="Heavy — requires lifting equipment or multiple people.",
        skill_required="trades",
    ),

    # ── Waste streams ──
    SalvageSource(
        "Municipal yard waste",
        [MaterialClass.ORGANIC],
        [ReuseCategory.GROWING],
        SalvageEffort.MINIMAL, 500, "per truck load",
        safety_notes="Avoid herbicide-treated grass clippings.",
        skill_required="none",
    ),
    SalvageSource(
        "Food waste (restaurants/groceries)",
        [MaterialClass.ORGANIC],
        [ReuseCategory.GROWING, ReuseCategory.ENERGY],
        SalvageEffort.MODERATE, 200, "per pickup load",
        safety_notes="Compost or biogas only — do not consume spoiled food.",
        skill_required="basic",
    ),
    SalvageSource(
        "Cardboard/paper stockpile",
        [MaterialClass.ORGANIC],
        [ReuseCategory.GROWING, ReuseCategory.SHELTER],
        SalvageEffort.MINIMAL, 100, "per bale",
        safety_notes="Sheet mulch or insulation. Keep dry for insulation use.",
        skill_required="none",
    ),

    # ── Scrap & junk ──
    SalvageSource(
        "Scrap metal pile",
        [MaterialClass.METAL],
        [ReuseCategory.TOOLS, ReuseCategory.SHELTER, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MODERATE, 1000, "per ton",
        safety_notes="Wear gloves. Tetanus risk. Sort ferrous/non-ferrous.",
        skill_required="basic",
    ),
    SalvageSource(
        "Tire stockpile",
        [MaterialClass.PLASTIC],
        [ReuseCategory.GROWING, ReuseCategory.SHELTER, ReuseCategory.WATER],
        SalvageEffort.MINIMAL, 20, "per tire",
        safety_notes="Earthship walls, raised beds, rain catchment. Mosquito breeding risk if water collects.",
        skill_required="none",
    ),
    SalvageSource(
        "Appliance dump",
        [MaterialClass.METAL, MaterialClass.MECHANICAL, MaterialClass.ELECTRICAL],
        [ReuseCategory.TOOLS, ReuseCategory.ENERGY, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MODERATE, 150, "per appliance",
        safety_notes="Refrigerant must be handled carefully. Copper in motors/compressors.",
        skill_required="basic",
    ),

    # ── Specialty ──
    SalvageSource(
        "Glass bottles/jars",
        [MaterialClass.GLASS],
        [ReuseCategory.GROWING, ReuseCategory.MEDICAL, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MINIMAL, 1, "per jar/bottle",
        safety_notes="Canning jars are high-value. Sort by size.",
        skill_required="none",
    ),
    SalvageSource(
        "Copper wire (buildings/equipment)",
        [MaterialClass.METAL, MaterialClass.ELECTRICAL],
        [ReuseCategory.ENERGY, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MODERATE, 5, "per 100 ft",
        safety_notes="De-energize before stripping. High trade value.",
        skill_required="trades",
    ),
    SalvageSource(
        "Plastic sheeting/tarps",
        [MaterialClass.PLASTIC],
        [ReuseCategory.SHELTER, ReuseCategory.GROWING, ReuseCategory.WATER],
        SalvageEffort.MINIMAL, 10, "per sheet",
        safety_notes="Greenhouse covers, rain catchment, temporary roofing.",
        skill_required="none",
    ),
    SalvageSource(
        "Battery bank (vehicle/UPS/solar)",
        [MaterialClass.ELECTRICAL, MaterialClass.CHEMICAL],
        [ReuseCategory.ENERGY, ReuseCategory.TRADE_GOODS],
        SalvageEffort.MODERATE, 40, "per battery",
        safety_notes="Acid hazard. Test before reuse — many still hold charge.",
        skill_required="trades",
    ),
]


# ── Community salvage profile ────────────────────────────────

@dataclass
class SalvageProfile:
    """A community's salvage resource inventory."""
    community_name: str
    population: int

    # Source counts
    abandoned_houses: int = 0
    commercial_buildings_empty: int = 0
    junk_vehicles: int = 0
    farm_equipment_idle: int = 0
    pallet_sources: int = 0         # businesses with pallet waste
    scrap_metal_tons: float = 0.0
    tire_stockpile: int = 0
    appliance_dumps: int = 0        # count of dump sites / collection points

    # Waste streams (weekly volume)
    yard_waste_loads_weekly: float = 0.0
    food_waste_loads_weekly: float = 0.0
    cardboard_bales_weekly: float = 0.0
    glass_jars_available: int = 0

    # Specialty
    battery_sources: int = 0        # dead batteries recoverable
    copper_wire_sites: int = 0      # buildings/equipment with recoverable wire
    plastic_sheeting_sources: int = 0

    # Community capacity
    skilled_trades_people: int = 0  # electricians, mechanics, welders, carpenters
    hand_tools_available: bool = False
    power_tools_available: bool = False
    vehicle_for_hauling: bool = False
    storage_space_sq_ft: float = 0.0


# ── Material recovery estimation ─────────────────────────────

REUSE_CONVERSIONS = {
    # material class → reuse category → conversion description and multiplier
    (MaterialClass.ORGANIC, ReuseCategory.GROWING): {
        "process": "Compost (90-day cycle)",
        "output": "Finished compost",
        "yield_pct": 40,  # 40% of input weight becomes compost
    },
    (MaterialClass.ORGANIC, ReuseCategory.ENERGY): {
        "process": "Biogas digester",
        "output": "Methane for cooking/heating",
        "yield_pct": 15,  # energy recovery percentage
    },
    (MaterialClass.LUMBER, ReuseCategory.SHELTER): {
        "process": "Denail, sort, stack",
        "output": "Dimensional lumber for repair",
        "yield_pct": 60,
    },
    (MaterialClass.LUMBER, ReuseCategory.GROWING): {
        "process": "Build raised beds",
        "output": "4x8 raised beds",
        "yield_pct": 80,
    },
    (MaterialClass.METAL, ReuseCategory.TOOLS): {
        "process": "Forge/weld/fabricate",
        "output": "Repaired or new hand tools",
        "yield_pct": 50,
    },
    (MaterialClass.METAL, ReuseCategory.SHELTER): {
        "process": "Roofing, framing, fasteners",
        "output": "Building materials",
        "yield_pct": 70,
    },
    (MaterialClass.ELECTRICAL, ReuseCategory.ENERGY): {
        "process": "Test, recondition, rewire",
        "output": "Functional electrical components",
        "yield_pct": 30,
    },
    (MaterialClass.GLASS, ReuseCategory.GROWING): {
        "process": "Cold frame / greenhouse glazing",
        "output": "Season-extending structures",
        "yield_pct": 70,
    },
    (MaterialClass.GLASS, ReuseCategory.MEDICAL): {
        "process": "Sterilize jars for storage",
        "output": "Medical supply containers",
        "yield_pct": 90,
    },
    (MaterialClass.PLASTIC, ReuseCategory.WATER): {
        "process": "Rain catchment / cistern lining",
        "output": "Water collection capacity",
        "yield_pct": 80,
    },
    (MaterialClass.PLASTIC, ReuseCategory.GROWING): {
        "process": "Greenhouse sheeting, row cover",
        "output": "Protected growing space",
        "yield_pct": 70,
    },
    (MaterialClass.MECHANICAL, ReuseCategory.TOOLS): {
        "process": "Repair, repurpose motors/pumps",
        "output": "Functional mechanical equipment",
        "yield_pct": 40,
    },
}


def estimate_material_recovery(profile: SalvageProfile) -> dict:
    """Estimate total recoverable materials by class."""
    totals = {mc: 0.0 for mc in MaterialClass}

    source_map = {
        "Abandoned house (frame)": profile.abandoned_houses,
        "Commercial building (demo)": profile.commercial_buildings_empty,
        "Junk vehicle": profile.junk_vehicles,
        "Farm equipment (non-functional)": profile.farm_equipment_idle,
        "Pallet stockpile": profile.pallet_sources * 20,  # ~20 pallets per source
        "Scrap metal pile": profile.scrap_metal_tons,
        "Tire stockpile": profile.tire_stockpile,
        "Appliance dump": profile.appliance_dumps * 30,  # ~30 appliances per site
        "Municipal yard waste": profile.yard_waste_loads_weekly * 52,
        "Food waste (restaurants/groceries)": profile.food_waste_loads_weekly * 52,
        "Cardboard/paper stockpile": profile.cardboard_bales_weekly * 52,
        "Glass bottles/jars": profile.glass_jars_available,
        "Battery bank (vehicle/UPS/solar)": profile.battery_sources,
        "Copper wire (buildings/equipment)": profile.copper_wire_sites * 500,  # ~500 ft per site
        "Plastic sheeting/tarps": profile.plastic_sheeting_sources,
    }

    source_details = []
    for source in SALVAGE_DB:
        count = source_map.get(source.name, 0)
        if count <= 0:
            continue
        lbs = count * source.yield_per_unit
        for mc in source.materials:
            share = lbs / len(source.materials)
            totals[mc] += share
        source_details.append({
            "source": source.name,
            "count": count,
            "total_lbs": round(lbs),
            "materials": [mc.value for mc in source.materials],
            "effort": source.effort.value,
            "skill": source.skill_required,
        })

    return {
        "material_totals_lbs": {mc.value: round(v) for mc, v in totals.items() if v > 0},
        "total_recoverable_lbs": round(sum(totals.values())),
        "source_breakdown": source_details,
    }


# ── Reuse planning ───────────────────────────────────────────

def salvage_reuse_plan(profile: SalvageProfile) -> list[dict]:
    """Generate prioritized reuse plan from available salvage."""
    recovery = estimate_material_recovery(profile)
    plan = []

    # Priority order: growing (food first), water, shelter, energy, tools, medical, trade
    priority_order = [
        ReuseCategory.GROWING,
        ReuseCategory.WATER,
        ReuseCategory.SHELTER,
        ReuseCategory.ENERGY,
        ReuseCategory.TOOLS,
        ReuseCategory.MEDICAL,
        ReuseCategory.TRADE_GOODS,
    ]

    for priority, category in enumerate(priority_order, 1):
        actions = []
        for (mc, rc), conversion in REUSE_CONVERSIONS.items():
            if rc != category:
                continue
            available_lbs = 0
            for mc_key, lbs in recovery["material_totals_lbs"].items():
                if mc_key == mc.value:
                    available_lbs = lbs
            if available_lbs <= 0:
                continue
            output_lbs = available_lbs * conversion["yield_pct"] / 100
            actions.append({
                "input_material": mc.value,
                "input_lbs": available_lbs,
                "process": conversion["process"],
                "output": conversion["output"],
                "output_lbs": round(output_lbs),
                "yield_pct": conversion["yield_pct"],
            })

        if actions:
            plan.append({
                "priority": priority,
                "category": category.value,
                "actions": actions,
            })

    return plan


# ── Scoring ──────────────────────────────────────────────────

def salvage_resilience_score(profile: SalvageProfile) -> dict:
    """Score a community's salvage recovery potential."""
    recovery = estimate_material_recovery(profile)
    total_lbs = recovery["total_recoverable_lbs"]
    lbs_per_capita = total_lbs / profile.population if profile.population > 0 else 0

    # Material diversity (0-30)
    material_types = len(recovery["material_totals_lbs"])
    diversity_score = min(30, material_types * 3)

    # Volume score (0-30) — based on lbs per capita
    if lbs_per_capita >= 500:
        volume_score = 30
    elif lbs_per_capita >= 200:
        volume_score = 25
    elif lbs_per_capita >= 100:
        volume_score = 20
    elif lbs_per_capita >= 50:
        volume_score = 15
    elif lbs_per_capita >= 10:
        volume_score = 10
    else:
        volume_score = min(10, int(lbs_per_capita))

    # Capacity score (0-40) — can the community actually process it?
    capacity = 0
    capacity += min(15, profile.skilled_trades_people * 3)
    capacity += 8 if profile.hand_tools_available else 0
    capacity += 7 if profile.power_tools_available else 0
    capacity += 5 if profile.vehicle_for_hauling else 0
    capacity += min(5, profile.storage_space_sq_ft / 200)

    total_score = min(100, diversity_score + volume_score + capacity)

    if total_score >= 70:
        grade = "STRONG"
    elif total_score >= 50:
        grade = "MODERATE"
    elif total_score >= 30:
        grade = "LIMITED"
    else:
        grade = "MINIMAL"

    return {
        "total_recoverable_lbs": total_lbs,
        "lbs_per_capita": round(lbs_per_capita, 1),
        "diversity_score": diversity_score,
        "volume_score": volume_score,
        "capacity_score": min(40, capacity),
        "total_score": round(total_score, 1),
        "grade": grade,
        "material_summary": recovery["material_totals_lbs"],
    }


# ── Report ───────────────────────────────────────────────────

def salvage_report(profile: SalvageProfile) -> str:
    """Full salvage and material recovery report."""
    score = salvage_resilience_score(profile)
    recovery = estimate_material_recovery(profile)
    plan = salvage_reuse_plan(profile)

    lines = [
        f"{'=' * 60}",
        f"SALVAGE & MATERIAL RECOVERY REPORT: {profile.community_name}",
        f"{'=' * 60}",
        f"Population:     {profile.population:,}",
        f"Grade:          {score['grade']} (score {score['total_score']}/100)",
        f"Total material: {score['total_recoverable_lbs']:,} lbs"
        f" ({score['lbs_per_capita']:.0f} lbs/person)",
        f"",
        f"  Diversity:  {score['diversity_score']}/30"
        f"  Volume: {score['volume_score']}/30"
        f"  Capacity: {score['capacity_score']}/40",
        f"",
        f"── RECOVERABLE MATERIALS ──",
    ]

    for material, lbs in sorted(score["material_summary"].items(),
                                 key=lambda x: x[1], reverse=True):
        bar_len = min(30, int(lbs / max(1, score["total_recoverable_lbs"]) * 30))
        bar = "█" * bar_len + "░" * (30 - bar_len)
        lines.append(f"  {material:15s} [{bar}] {lbs:>10,} lbs")

    # Source breakdown
    lines += [f"", f"── SALVAGE SOURCES ──"]
    for source in recovery["source_breakdown"]:
        lines.append(f"  {source['source']}")
        lines.append(f"    Count: {source['count']}  |  Yield: {source['total_lbs']:,} lbs"
                     f"  |  Effort: {source['effort']}  |  Skill: {source['skill']}")

    # Reuse plan
    lines += [f"", f"── REUSE PLAN (by priority) ──"]
    for step in plan:
        lines.append(f"\n  [{step['priority']}] {step['category'].upper()}")
        for action in step["actions"]:
            lines.append(f"    {action['input_material']} → {action['process']}")
            lines.append(f"      Input: {action['input_lbs']:,} lbs → Output: {action['output_lbs']:,} lbs"
                         f" ({action['yield_pct']}% recovery)")
            lines.append(f"      Result: {action['output']}")

    # Safety reminders
    lines += [
        f"",
        f"── SAFETY REMINDERS ──",
        f"  - Asbestos/lead testing before demolition (pre-1980 structures)",
        f"  - Drain fluids before vehicle disassembly",
        f"  - Battery acid handled with gloves and eye protection",
        f"  - Tetanus risk with scrap metal — ensure vaccination",
        f"  - Never burn treated lumber, tires, or plastics",
        f"{'=' * 60}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # Fairmont, MN — typical small town salvage inventory
    fairmont_salvage = SalvageProfile(
        community_name="Fairmont, MN",
        population=10_000,
        abandoned_houses=15,
        commercial_buildings_empty=3,
        junk_vehicles=40,
        farm_equipment_idle=10,
        pallet_sources=5,
        scrap_metal_tons=20,
        tire_stockpile=200,
        appliance_dumps=2,
        yard_waste_loads_weekly=10,
        food_waste_loads_weekly=5,
        cardboard_bales_weekly=8,
        glass_jars_available=500,
        battery_sources=30,
        copper_wire_sites=5,
        plastic_sheeting_sources=20,
        skilled_trades_people=8,
        hand_tools_available=True,
        power_tools_available=True,
        vehicle_for_hauling=True,
        storage_space_sq_ft=2000,
    )
    print(salvage_report(fairmont_salvage))
