"""
transition.py — Leverage Analysis & Transition Pathways
Urban Resilience Simulator
License: CC0

Two questions this module answers:

  1. Which small modifications buy the most resilience per dollar?
     Every lever is applied to a real copy of the profile and re-scored
     through community.score_infrastructure(), so the ranking is computed,
     not asserted. If the scoring weights are wrong the ranking is wrong
     with them — see claim TRANS-03.

  2. What actually has to happen for a community to get there?
     A model can say "add 1 MW of local generation". It cannot add it.
     Somebody has to pass something, fund something, and own something.
     INSTRUMENT_DB holds the governance and financial instruments a small
     municipality actually has, with the procedural steps each one takes,
     how long it runs, what kills it, and how hard it is to undo.

The second question is the one that usually decides the outcome. A town
does not fail to build resilience because it picked the wrong technology;
it fails because nobody could find a legal vehicle to pay for it.
"""

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, List, Optional, Tuple

from community import (CommunityProfile, InfraState, score_infrastructure,
                       local_production_capacity)


# ── Vocabulary ────────────────────────────────────────────────

class LeverScale(Enum):
    SMALL = "SMALL"     # under ~$5k, or volunteer effort only
    MEDIUM = "MEDIUM"   # ~$5k-100k — a budget line or a grant
    LARGE = "LARGE"     # over ~$100k — debt, a co-op, or a capital plan


class Actor(Enum):
    HOUSEHOLD = "households"
    CIVIC_GROUP = "civic group / volunteers"
    CITY_COUNCIL = "city council"
    COUNTY_BOARD = "county board"
    UTILITY = "utility or utility commission"
    SCHOOL_DISTRICT = "school district"
    COOPERATIVE = "cooperative members"
    STATE_FEDERAL = "state or federal agency"


class Instrument(Enum):
    """The legal or financial vehicle that moves old design to new."""
    VOLUNTEER_ORGANIZING = "volunteer organizing"
    RESOLUTION = "council resolution"
    ORDINANCE = "ordinance"
    ZONING_AMENDMENT = "zoning amendment"
    COMP_PLAN_AMENDMENT = "comprehensive plan amendment"
    MUTUAL_AID_COMPACT = "mutual aid compact"
    JOINT_POWERS = "joint powers agreement"
    NONPROFIT_FORMATION = "nonprofit formation"
    COOP_FORMATION = "cooperative formation"
    BUDGET_LINE = "annual budget line"
    CAPITAL_PLAN = "capital improvement plan"
    GRANT = "grant award"
    REVOLVING_LOAN_FUND = "revolving loan fund"
    SPECIAL_ASSESSMENT = "special assessment"
    FRANCHISE_FEE = "utility franchise fee"
    RATE_RIDER = "utility rate rider"
    REVENUE_BOND = "revenue bond"
    GO_BOND = "general obligation bond"
    TIF_DISTRICT = "tax increment financing district"
    PRIVATE_INVESTMENT = "private investment"


class Reversibility(Enum):
    HIGH = "HIGH"       # undo at the next meeting
    MEDIUM = "MEDIUM"   # a budget cycle or two to unwind
    LOW = "LOW"         # multi-decade commitment; forecloses other options


# ── Governance & financial instruments ────────────────────────

@dataclass
class InstrumentSpec:
    """What it actually takes to use one instrument."""
    instrument: Instrument
    who_acts: Actor
    steps: List[str]
    typical_months: int
    reversibility: Reversibility
    money_source: str
    fails_when: str
    notes: str = ""


# [TRANS-05] Procedural steps and durations are generic US small-municipality
# practice, MN-flavoured. Every one of them varies by charter and state code.
INSTRUMENT_DB = {

    Instrument.VOLUNTEER_ORGANIZING: InstrumentSpec(
        instrument=Instrument.VOLUNTEER_ORGANIZING,
        who_acts=Actor.CIVIC_GROUP,
        steps=[
            "Find two or three people who will actually show up repeatedly",
            "Pick a standing meeting time and hold it even when attendance is bad",
            "Produce one visible artifact (a map, a list, a working radio net)",
            "Only then ask the council for recognition or a small appropriation",
        ],
        typical_months=3,
        reversibility=Reversibility.HIGH,
        money_source="Donated time; incidental costs from passing the hat",
        fails_when="It is organised around a meeting instead of around a task, "
                   "or it depends on one person who then moves away.",
        notes="No permission required. This is the only instrument that needs "
              "nothing from anyone, which is why it is where transitions start.",
    ),

    Instrument.RESOLUTION: InstrumentSpec(
        instrument=Instrument.RESOLUTION,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Council member or staff places it on the agenda",
            "Single reading and vote at a regular meeting",
            "Effective immediately on adoption",
        ],
        typical_months=1,
        reversibility=Reversibility.HIGH,
        money_source="None — a statement of intent, not an appropriation",
        fails_when="Treated as the accomplishment rather than the authorisation. "
                   "A resolution with no follow-on instrument changes nothing.",
        notes="Cheap and fast. Useful to establish standing and to make a "
              "committee official enough to receive grants.",
    ),

    Instrument.ORDINANCE: InstrumentSpec(
        instrument=Instrument.ORDINANCE,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Draft language with the city attorney",
            "First reading at council",
            "Publish notice per charter requirements",
            "Second reading, public comment, and vote",
            "Effective on publication or a stated date",
        ],
        typical_months=3,
        reversibility=Reversibility.HIGH,
        money_source="None — regulatory, removes a prohibition or sets a rule",
        fails_when="No council sponsor, or six loud people at the public hearing "
                   "and nobody speaking for it.",
        notes="Permission-granting ordinances (gardens, poultry, greywater, "
              "rainwater catchment) cost the city nothing and unlock household "
              "action at zero public expense. The highest-leverage instrument "
              "on this list per dollar spent, because the dollar is zero.",
    ),

    Instrument.ZONING_AMENDMENT: InstrumentSpec(
        instrument=Instrument.ZONING_AMENDMENT,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Application to the planning commission",
            "Mailed notice to nearby property owners",
            "Planning commission hearing and recommendation",
            "Council hearing and vote (supermajority in some charters)",
        ],
        typical_months=5,
        reversibility=Reversibility.MEDIUM,
        money_source="None; applicant may owe filing fees",
        fails_when="It conflicts with the comprehensive plan — then the plan "
                   "has to be amended first, adding six months or more.",
        notes="Check the comprehensive plan before starting. This is the most "
              "common place a resilience project silently loses a year.",
    ),

    Instrument.COMP_PLAN_AMENDMENT: InstrumentSpec(
        instrument=Instrument.COMP_PLAN_AMENDMENT,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Planning commission work sessions",
            "Public engagement process",
            "Draft amendment and review period",
            "Council adoption; regional review where required",
        ],
        typical_months=10,
        reversibility=Reversibility.MEDIUM,
        money_source="Staff time; often a consultant contract",
        fails_when="Scheduled as a one-off instead of folded into the regular "
                   "plan update, which is far cheaper.",
        notes="Slow, but it is the document every later zoning fight is decided "
              "against. Getting resilience language in during a scheduled "
              "update costs almost nothing extra.",
    ),

    Instrument.MUTUAL_AID_COMPACT: InstrumentSpec(
        instrument=Instrument.MUTUAL_AID_COMPACT,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Identify neighbouring jurisdictions with complementary capacity",
            "Attorneys draft reciprocal terms (equipment, personnel, liability)",
            "Each council adopts by resolution",
            "Joint exercise to find out whether it actually works",
        ],
        typical_months=6,
        reversibility=Reversibility.HIGH,
        money_source="None — trades capacity rather than buying it",
        fails_when="Signed and filed without a joint exercise. An untested "
                   "compact is a document, not a capability.",
        notes="Buys access to equipment the town could never justify owning. "
              "Pairs directly with the corridor model in network.py.",
    ),

    Instrument.JOINT_POWERS: InstrumentSpec(
        instrument=Instrument.JOINT_POWERS,
        who_acts=Actor.COUNTY_BOARD,
        steps=[
            "Agree on the shared function and cost-share formula",
            "Draft the joint powers agreement",
            "Each participating body adopts it",
            "Stand up the joint board and its budget",
        ],
        typical_months=9,
        reversibility=Reversibility.MEDIUM,
        money_source="Pooled contributions from member jurisdictions",
        fails_when="The cost-share formula is not tied to benefit received, so "
                   "the largest member concludes it is subsidising everyone.",
        notes="How small towns afford things at county scale — shared water "
              "operators, joint equipment, regional emergency management.",
    ),

    Instrument.NONPROFIT_FORMATION: InstrumentSpec(
        instrument=Instrument.NONPROFIT_FORMATION,
        who_acts=Actor.CIVIC_GROUP,
        steps=[
            "Incorporate with the Secretary of State",
            "Adopt bylaws and seat an initial board",
            "File for federal tax exemption (or use a fiscal sponsor to skip this)",
            "Open books and adopt a conflict-of-interest policy",
        ],
        typical_months=7,
        reversibility=Reversibility.MEDIUM,
        money_source="Donations, grants, fee-for-service",
        fails_when="Formed before there is any activity to house. An entity "
                   "with no program is an annual filing obligation.",
        notes="Fiscal sponsorship by an existing nonprofit gets grant "
              "eligibility in weeks instead of months. Use it first; "
              "incorporate later if the work outlives the sponsor.",
    ),

    Instrument.COOP_FORMATION: InstrumentSpec(
        instrument=Instrument.COOP_FORMATION,
        who_acts=Actor.COOPERATIVE,
        steps=[
            "Feasibility study and member survey",
            "Incorporate under the state cooperative statute",
            "Member equity drive to raise the capital base",
            "Seat a board; hire or contract an operator",
        ],
        typical_months=15,
        reversibility=Reversibility.MEDIUM,
        money_source="Member equity, patronage capital, co-op lenders",
        fails_when="The equity drive stalls halfway and the project carries "
                   "organising costs with no asset to show for them.",
        notes="Slower than a private developer and keeps ownership — and the "
              "earnings — inside the community. That ownership is itself a "
              "resilience asset the infrastructure score does not measure.",
    ),

    Instrument.BUDGET_LINE: InstrumentSpec(
        instrument=Instrument.BUDGET_LINE,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Department request during budget preparation",
            "Council work sessions and preliminary levy certification",
            "Truth-in-taxation hearing",
            "Final budget adoption",
        ],
        typical_months=8,
        reversibility=Reversibility.MEDIUM,
        money_source="Property tax levy, local government aid, fees",
        fails_when="Missing the preliminary levy certification deadline. The "
                   "preliminary levy can be lowered later but never raised, "
                   "so a request that misses it waits a full year.",
        notes="Timing dominates. Ask in the month the department requests are "
              "assembled, not the month the budget is adopted.",
    ),

    Instrument.CAPITAL_PLAN: InstrumentSpec(
        instrument=Instrument.CAPITAL_PLAN,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Get the project into the five-year capital improvement plan",
            "Annual re-prioritisation as projects move up the queue",
            "Funding instrument selected in the year of execution",
        ],
        typical_months=14,
        reversibility=Reversibility.MEDIUM,
        money_source="Whatever instrument is chosen in the execution year",
        fails_when="Listed in year five forever, re-listed each cycle without "
                   "ever entering year one.",
        notes="Being in the CIP is what makes a project fundable later. Cheap "
              "to do early and it costs nothing to be in the out-years.",
    ),

    Instrument.GRANT: InstrumentSpec(
        instrument=Instrument.GRANT,
        who_acts=Actor.STATE_FEDERAL,
        steps=[
            "Identify the program and confirm eligibility",
            "Secure the local match — this is the real constraint",
            "Council resolution authorising the application",
            "Apply; award; then execute under the reporting rules",
        ],
        typical_months=12,
        reversibility=Reversibility.MEDIUM,
        money_source="External, usually with a 10-50% local match required",
        fails_when="No match identified, or the administrative burden exceeds "
                   "what the staff can carry for the life of the award.",
        notes="Attractive because the money is external, expensive because the "
              "match and the reporting are not. A small grant can cost more in "
              "staff time than it delivers.",
    ),

    Instrument.REVOLVING_LOAN_FUND: InstrumentSpec(
        instrument=Instrument.REVOLVING_LOAN_FUND,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Seed the fund once (grant, one-time levy, or reserves)",
            "Adopt lending criteria and a loan committee",
            "Lend for qualifying improvements; repayments replenish the fund",
        ],
        typical_months=10,
        reversibility=Reversibility.MEDIUM,
        money_source="One-time seed, then self-sustaining from repayments",
        fails_when="Criteria so tight nothing qualifies, or so loose the first "
                   "defaults decapitalise the fund.",
        notes="The highest-leverage financial instrument here: one "
              "appropriation funds work repeatedly. Especially strong for "
              "household-scale measures the city cannot fund directly.",
    ),

    Instrument.SPECIAL_ASSESSMENT: InstrumentSpec(
        instrument=Instrument.SPECIAL_ASSESSMENT,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Feasibility report and preliminary assessment roll",
            "Improvement hearing with mailed notice to affected owners",
            "Order the improvement; award construction",
            "Assessment hearing; owners retain appeal rights",
        ],
        typical_months=11,
        reversibility=Reversibility.LOW,
        money_source="Levied against benefited properties over 10-20 years",
        fails_when="The benefit test fails — assessments must not exceed the "
                   "increase in property value, and appeals turn on exactly that.",
        notes="Works where benefit is geographically specific. Falls apart for "
              "community-wide benefits like emergency communications.",
    ),

    Instrument.FRANCHISE_FEE: InstrumentSpec(
        instrument=Instrument.FRANCHISE_FEE,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Negotiate or renew the franchise with the utility",
            "Adopt a fee ordinance, flat or percentage",
            "Dedicate proceeds by policy to the intended purpose",
        ],
        typical_months=6,
        reversibility=Reversibility.MEDIUM,
        money_source="A fee on utility bills, collected by the utility",
        fails_when="Proceeds land in the general fund and quietly become "
                   "ordinary operating revenue.",
        notes="Produces steady, predictable money without a levy increase. "
              "Regressive as a flat fee — a per-account charge hits a small "
              "household as hard as a large one.",
    ),

    Instrument.RATE_RIDER: InstrumentSpec(
        instrument=Instrument.RATE_RIDER,
        who_acts=Actor.UTILITY,
        steps=[
            "Utility commission proposes a dedicated rider",
            "Cost-of-service justification",
            "Public hearing and adoption",
        ],
        typical_months=7,
        reversibility=Reversibility.MEDIUM,
        money_source="Dedicated surcharge on utility rates",
        fails_when="There is no municipal utility — an investor-owned utility "
                   "answers to the state commission, not the council.",
        notes="Only available to towns that own their utility. Where it exists "
              "it is the cleanest way to fund generation and storage.",
    ),

    Instrument.REVENUE_BOND: InstrumentSpec(
        instrument=Instrument.REVENUE_BOND,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Engineering report and revenue sufficiency analysis",
            "Bond counsel opinion; rating if the issue is large enough",
            "Council authorises issuance",
            "Sale, closing, and construction draw-down",
        ],
        typical_months=13,
        reversibility=Reversibility.LOW,
        money_source="Repaid from the revenues of the financed system",
        fails_when="Projected revenues do not cover debt service with coverage "
                   "to spare, which forces a rate increase to close the gap.",
        notes="Usually avoids a referendum because it is not backed by the "
              "levy. Commits the utility's revenue for 20-30 years.",
    ),

    Instrument.GO_BOND: InstrumentSpec(
        instrument=Instrument.GO_BOND,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Capital plan and cost estimates",
            "Determine whether a referendum is required",
            "Referendum campaign if so",
            "Bond counsel, authorisation, sale, levy certification",
        ],
        typical_months=20,
        reversibility=Reversibility.LOW,
        money_source="Repaid from the property tax levy",
        fails_when="The referendum fails, which typically freezes the project "
                   "for several years regardless of merit.",
        notes="The largest lever available and the least reversible. Debt "
              "service is a fixed claim on future levies — it narrows what a "
              "future council can respond to. Weigh that against the asset.",
    ),

    Instrument.TIF_DISTRICT: InstrumentSpec(
        instrument=Instrument.TIF_DISTRICT,
        who_acts=Actor.CITY_COUNCIL,
        steps=[
            "Establish the district and adopt a TIF plan",
            "Notice to county and school district",
            "Council public hearing and approval",
            "Increment captured as new value comes on line",
        ],
        typical_months=13,
        reversibility=Reversibility.LOW,
        money_source="Property tax increment above the frozen base value",
        fails_when="The increment never materialises, leaving the district "
                   "carrying costs against a base that did not grow.",
        notes="Diverts revenue the county and school district would otherwise "
              "receive. Politically expensive with those partners, and they "
              "are the same partners needed for joint powers work later.",
    ),

    Instrument.PRIVATE_INVESTMENT: InstrumentSpec(
        instrument=Instrument.PRIVATE_INVESTMENT,
        who_acts=Actor.HOUSEHOLD,
        steps=[
            "Remove the regulatory barrier (usually an ordinance)",
            "Reduce the information cost — permitting guide, vetted installers",
            "Reduce the capital cost — revolving loan, bulk purchase, on-bill",
        ],
        typical_months=4,
        reversibility=Reversibility.HIGH,
        money_source="Household and business capital",
        fails_when="The barrier removed was not the binding one. Ordinance "
                   "relief does nothing if the real obstacle was financing.",
        notes="The largest pool of capital in most towns and the one a council "
              "most often forgets it can mobilise. Costs the city near zero: "
              "permission plus information plus a credit backstop.",
    ),
}


# ── Levers ────────────────────────────────────────────────────

@dataclass
class Lever:
    """A modification to a community, and what it takes to make it."""
    id: str
    name: str
    domain: str
    scale: LeverScale
    changes: Dict[str, Tuple[str, float]]   # field -> ("add"|"set", value)
    cost_low: int
    cost_high: int
    lead_months: int
    instruments: List[Instrument]
    prerequisites: List[str] = field(default_factory=list)
    notes: str = ""


# [TRANS-01] Cost ranges are order-of-magnitude estimates for a town of a few
# thousand people. [TRANS-02] Lead times are from decision to operation.
LEVER_DB = [

    # ── No capital required ──
    Lever("SKILLS-MAP", "Inventory who can actually do things", "social_cohesion",
          LeverScale.SMALL, {"skill_holders_identified": ("add", 10)},
          0, 400, 3, [Instrument.VOLUNTEER_ORGANIZING],
          notes="Welders, well drillers, hams, nurses, mechanics, people who "
                "keep bees. Costs a spreadsheet and a church basement."),

    Lever("GARDEN-ORD", "Right-to-garden ordinance + one municipal lot", "social_cohesion",
          LeverScale.SMALL, {"community_gardens_acres": ("add", 2.0)},
          200, 4_000, 5, [Instrument.ORDINANCE, Instrument.ZONING_AMENDMENT],
          notes="Removes the prohibition, then demonstrates on city-owned land. "
                "Scores in social cohesion and food capacity at once."),

    Lever("MUTUAL-AID", "Formalise a mutual aid network", "social_cohesion",
          LeverScale.SMALL, {"mutual_aid_networks": ("add", 1)},
          0, 1_200, 6, [Instrument.VOLUNTEER_ORGANIZING, Instrument.MUTUAL_AID_COMPACT],
          prerequisites=["SKILLS-MAP"],
          notes="The skills inventory is what makes this more than a mailing list."),

    Lever("CIVIC-CMTE", "Stand up a standing resilience committee", "social_cohesion",
          LeverScale.SMALL, {"civic_organizations": ("add", 1)},
          0, 600, 4, [Instrument.RESOLUTION, Instrument.VOLUNTEER_ORGANIZING],
          notes="Recognition by resolution is what lets it hold a grant later."),

    Lever("HAM-NET", "Recruit and license amateur radio operators", "communication",
          LeverScale.SMALL, {"ham_radio_operators": ("add", 3)},
          400, 2_500, 6, [Instrument.VOLUNTEER_ORGANIZING],
          notes="Licence study, exam fees, and a few HF rigs. The only "
                "communication capacity in this model that survives losing "
                "both the towers and the ISPs."),

    Lever("WELL-INV", "Inventory private wells; add hand pumps", "water",
          LeverScale.SMALL, {"wells_private": ("add", 5)},
          800, 6_000, 7, [Instrument.VOLUNTEER_ORGANIZING, Instrument.BUDGET_LINE],
          notes="Most of these wells already exist and are simply not known "
                "about. The spend is testing and hand-pump retrofits."),

    Lever("HOME-SOLAR", "Unlock household solar: permit guide + loan fund", "energy",
          LeverScale.SMALL, {"solar_installations": ("add", 12)},
          2_000, 25_000, 9,
          [Instrument.ORDINANCE, Instrument.PRIVATE_INVESTMENT,
           Instrument.REVOLVING_LOAN_FUND],
          notes="City spends on permission, information and a credit backstop; "
                "households supply the capital. Cheapest route to distributed "
                "generation on this list."),

    # ── Budget-scale ──
    Lever("ALERT-SYS", "Community alert system", "communication",
          LeverScale.MEDIUM, {"community_alert_system": ("set", True)},
          4_000, 30_000, 10, [Instrument.BUDGET_LINE, Instrument.GRANT]),

    Lever("FUEL-RES", "Extend municipal fuel reserve to 14 days", "transportation",
          LeverScale.MEDIUM, {"fuel_reserve_days": ("set", 14.0)},
          15_000, 70_000, 12, [Instrument.BUDGET_LINE, Instrument.CAPITAL_PLAN],
          notes="Tankage plus fuel. Scores in transportation and energy both."),

    Lever("GEN-CRIT", "Backup generation at critical facilities", "energy",
          LeverScale.MEDIUM, {"backup_generators": ("add", 5)},
          30_000, 120_000, 14, [Instrument.CAPITAL_PLAN, Instrument.GRANT]),

    Lever("WATER-BKP", "Backup power for the water plant", "water",
          LeverScale.MEDIUM, {"backup_power_water_plant": ("set", True)},
          40_000, 180_000, 15,
          [Instrument.REVENUE_BOND, Instrument.GRANT, Instrument.RATE_RIDER],
          notes="Without it, losing the grid takes the water system with it "
                "inside a day — see water_system.py."),

    Lever("WATER-RES", "Raise treated water reserve to 7 days", "water",
          LeverScale.MEDIUM, {"days_water_reserve": ("set", 7.0)},
          60_000, 400_000, 18,
          [Instrument.REVENUE_BOND, Instrument.SPECIAL_ASSESSMENT]),

    Lever("SURFACE-W", "Develop a surface water intake and treatment", "water",
          LeverScale.MEDIUM, {"surface_water_sources": ("add", 2)},
          80_000, 500_000, 20, [Instrument.REVENUE_BOND, Instrument.GRANT]),

    Lever("PHARM", "Recruit an additional pharmacy", "medical",
          LeverScale.MEDIUM, {"pharmacy_count": ("add", 1)},
          10_000, 90_000, 16,
          [Instrument.TIF_DISTRICT, Instrument.REVOLVING_LOAN_FUND,
           Instrument.PRIVATE_INVESTMENT]),

    # ── Capital-scale ──
    Lever("SOLAR-MUNI", "Municipal solar array, 1 MW", "energy",
          LeverScale.LARGE, {"local_generation_mw": ("add", 1.0)},
          900_000, 1_700_000, 26,
          [Instrument.GO_BOND, Instrument.REVENUE_BOND, Instrument.GRANT],
          prerequisites=["CIVIC-CMTE"]),

    Lever("WIND-COOP", "Community wind, 2 MW, member-owned", "energy",
          LeverScale.LARGE, {"wind_capacity_mw": ("add", 2.0)},
          3_000_000, 5_500_000, 34,
          [Instrument.COOP_FORMATION, Instrument.PRIVATE_INVESTMENT],
          prerequisites=["CIVIC-CMTE"],
          notes="Slower than a developer-owned array and the earnings stay in "
                "the county. Ownership structure is the point."),

    Lever("RAIL", "Restore rail spur service", "transportation",
          LeverScale.LARGE, {"rail_access": ("set", True)},
          1_500_000, 8_000_000, 40,
          [Instrument.JOINT_POWERS, Instrument.GRANT, Instrument.GO_BOND]),

    Lever("CLINIC", "Establish a hospital or expand to full service", "medical",
          LeverScale.LARGE, {"hospital_present": ("set", True)},
          4_000_000, 20_000_000, 48,
          [Instrument.GO_BOND, Instrument.JOINT_POWERS, Instrument.GRANT]),
]


# ── Applying levers ───────────────────────────────────────────

def apply_lever(profile: CommunityProfile, lever: Lever) -> CommunityProfile:
    """Return a copy of the profile with the lever's changes applied."""
    updates = {}
    for fieldname, (mode, value) in lever.changes.items():
        current = getattr(profile, fieldname)
        if mode == "add":
            updates[fieldname] = current + value
        elif mode == "set":
            updates[fieldname] = value
        else:
            raise ValueError(f"{lever.id}: unknown change mode {mode!r}")
    return replace(profile, **updates)


def apply_levers(profile: CommunityProfile, levers: List[Lever]) -> CommunityProfile:
    """Apply several levers in sequence."""
    for lever in levers:
        profile = apply_lever(profile, lever)
    return profile


def lever_by_id(lever_id: str, levers: Optional[List[Lever]] = None) -> Optional[Lever]:
    levers = LEVER_DB if levers is None else levers
    for lever in levers:
        if lever.id == lever_id:
            return lever
    return None


# ── Leverage analysis ─────────────────────────────────────────

# [TRANS-04] Leverage is score points per $10k, using a floor cost so that
# no-capital levers do not divide by zero. Volunteer effort is not free; the
# floor is a stand-in for organising cost that nobody has measured.
COST_FLOOR_USD = 250


def evaluate_lever(profile: CommunityProfile, lever: Lever) -> dict:
    """Score one lever by actually applying it and re-running the model."""
    base_infra = score_infrastructure(profile)
    base_food = local_production_capacity(profile)

    after = apply_lever(profile, lever)
    new_infra = score_infrastructure(after)
    new_food = local_production_capacity(after)

    cost_mid = (lever.cost_low + lever.cost_high) / 2
    d_overall = new_infra["overall"] - base_infra["overall"]
    d_floor = new_infra["floor"] - base_infra["floor"]
    d_autonomy = new_infra["autonomy_overall"] - base_infra["autonomy_overall"]
    d_food_days = (new_food["days_until_crisis_no_resupply"]
                   - base_food["days_until_crisis_no_resupply"])

    # Does it relieve the constraint that actually binds?
    relieves_binding = (lever.domain == base_infra["binding_constraint"]
                        and d_floor > 0)

    worst_reversibility = Reversibility.HIGH
    for instrument in lever.instruments:
        spec = INSTRUMENT_DB.get(instrument)
        if spec is None:
            continue
        order = [Reversibility.HIGH, Reversibility.MEDIUM, Reversibility.LOW]
        if order.index(spec.reversibility) > order.index(worst_reversibility):
            worst_reversibility = spec.reversibility

    # [SCORE-02] Domain terms are capped. Once a community is past a cap,
    # further investment in that measure scores nothing — the lever still
    # changes the profile, the score just stops being able to see it.
    saturated = (d_overall == 0 and d_food_days == 0
                 and apply_lever(profile, lever) != profile)

    return {
        "lever": lever,
        "cost_mid": cost_mid,
        "saturated": saturated,
        "d_overall": round(d_overall, 2),
        "d_floor": round(d_floor, 2),
        "d_autonomy": round(d_autonomy, 2),
        "d_food_days": round(d_food_days, 1),
        "relieves_binding": relieves_binding,
        "state_before": base_infra["state"],
        "state_after": new_infra["state"],
        "changes_state": base_infra["state"] is not new_infra["state"],
        "points_per_10k": round(
            d_overall / max(cost_mid, COST_FLOOR_USD) * 10_000, 2),
        "autonomy_per_10k": round(
            d_autonomy / max(cost_mid, COST_FLOOR_USD) * 10_000, 2),
        "reversibility": worst_reversibility,
        "lead_months": lever.lead_months,
    }


def leverage_analysis(profile: CommunityProfile,
                      levers: Optional[List[Lever]] = None,
                      scale: Optional[LeverScale] = None) -> List[dict]:
    """Rank every lever by resilience gained per dollar.

    Ranking puts levers that relieve the binding constraint first — a point
    added to the weakest domain is worth more than a point added to the
    strongest, and the mean score alone will not show that.
    """
    levers = LEVER_DB if levers is None else levers
    if scale is not None:
        levers = [l for l in levers if l.scale is scale]

    results = [evaluate_lever(profile, lever) for lever in levers]
    results.sort(key=lambda r: (not r["relieves_binding"], -r["points_per_10k"]))
    return results


def most_leveraged(profile: CommunityProfile, top: int = 5,
                   scale: Optional[LeverScale] = LeverScale.SMALL) -> List[dict]:
    """The smallest modifications with the largest effect. Defaults to SMALL."""
    return leverage_analysis(profile, scale=scale)[:top]


# ── Transition sequencing ─────────────────────────────────────

# [TRANS-06] Phase assignment is by the least demanding instrument a lever can
# use — an optimistic reading. A lever that could be done by ordinance but is
# in practice pursued by bond lands in phase 0 here and in year two in reality.
_PHASE_BY_INSTRUMENT = {
    Instrument.VOLUNTEER_ORGANIZING: 0,
    Instrument.RESOLUTION: 0,
    Instrument.ORDINANCE: 0,
    Instrument.MUTUAL_AID_COMPACT: 0,
    Instrument.PRIVATE_INVESTMENT: 0,
    Instrument.ZONING_AMENDMENT: 1,
    Instrument.NONPROFIT_FORMATION: 1,
    Instrument.BUDGET_LINE: 1,
    Instrument.CAPITAL_PLAN: 1,
    Instrument.GRANT: 1,
    Instrument.REVOLVING_LOAN_FUND: 1,
    Instrument.FRANCHISE_FEE: 1,
    Instrument.COMP_PLAN_AMENDMENT: 2,
    Instrument.JOINT_POWERS: 2,
    Instrument.COOP_FORMATION: 2,
    Instrument.RATE_RIDER: 2,
    Instrument.SPECIAL_ASSESSMENT: 2,
    Instrument.REVENUE_BOND: 2,
    Instrument.GO_BOND: 2,
    Instrument.TIF_DISTRICT: 2,
}

PHASE_NAMES = {
    0: "Phase 0 — no appropriation required",
    1: "Phase 1 — current budget cycle",
    2: "Phase 2 — financed / multi-year",
}


def lever_phase(lever: Lever) -> int:
    """Earliest phase the lever could move in, by its cheapest instrument."""
    return min((_PHASE_BY_INSTRUMENT.get(i, 2) for i in lever.instruments),
               default=2)


def transition_plan(profile: CommunityProfile,
                    levers: Optional[List[Lever]] = None,
                    budget: Optional[float] = None) -> dict:
    """Sequence levers into phases, respecting prerequisites and budget.

    Walks the community from its current profile to a modified one, tracking
    cumulative cost and score as it goes, so each step can be checked against
    what it actually bought.
    """
    levers = LEVER_DB if levers is None else levers
    ranked = leverage_analysis(profile, levers)

    selected, spent, chosen_ids = [], 0.0, set()
    # Cheapest-instrument phase first, then leverage rank within a phase.
    for result in sorted(ranked, key=lambda r: (lever_phase(r["lever"]),
                                                not r["relieves_binding"],
                                                -r["points_per_10k"])):
        lever = result["lever"]
        if budget is not None and spent + result["cost_mid"] > budget:
            continue
        if any(p not in chosen_ids for p in lever.prerequisites):
            continue
        selected.append(result)
        chosen_ids.add(lever.id)
        spent += result["cost_mid"]

    # Re-score cumulatively along the chosen sequence.
    running, steps = profile, []
    base = score_infrastructure(profile)
    for result in selected:
        running = apply_lever(running, result["lever"])
        infra = score_infrastructure(running)
        steps.append({
            "lever": result["lever"],
            "phase": lever_phase(result["lever"]),
            "cost_mid": result["cost_mid"],
            "cumulative_overall": infra["overall"],
            "cumulative_floor": infra["floor"],
            "cumulative_autonomy": infra["autonomy_overall"],
            "binding_now": infra["binding_constraint"],
            "state": infra["state"],
        })

    final = score_infrastructure(running)
    return {
        "steps": steps,
        "total_cost_mid": spent,
        "months_longest_path": max((s["lever"].lead_months for s in steps),
                                   default=0),
        "before": base,
        "after": final,
        "profile_after": running,
        "low_reversibility": [s["lever"] for s in steps
                              if any(INSTRUMENT_DB[i].reversibility
                                     is Reversibility.LOW
                                     for i in s["lever"].instruments
                                     if i in INSTRUMENT_DB)],
    }


# ── Reports ───────────────────────────────────────────────────

def _money(amount: float) -> str:
    if amount == 0:
        return "$0"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount / 1_000:.0f}k"
    return f"${amount:.0f}"


def leverage_report(profile: CommunityProfile,
                    scale: Optional[LeverScale] = None,
                    top: Optional[int] = None) -> str:
    """Levers ranked by resilience bought per dollar."""
    base = score_infrastructure(profile)
    results = leverage_analysis(profile, scale=scale)
    if top:
        results = results[:top]

    label = f" ({scale.value} only)" if scale else ""
    lines = [
        "=" * 72,
        f"LEVERAGE ANALYSIS: {profile.name}{label}",
        "=" * 72,
        f"Now: {base['state'].value} — overall {base['overall']}, "
        f"autonomy {base['autonomy_overall']}",
        f"Binding constraint: {base['binding_constraint'].replace('_', ' ')} "
        f"at {base['floor']}/100",
        "",
        "Ranked by score points per $10k. Levers that relieve the binding",
        "constraint sort first — a point added to the weakest domain is worth",
        "more than a point added to the strongest.",
        "",
        f"  {'lever':<12} {'cost':>8} {'pts/$10k':>9} {'floor':>6} "
        f"{'auton':>6} {'mo':>3}  notes",
        f"  {'-' * 12} {'-' * 8} {'-' * 9} {'-' * 6} {'-' * 6} {'-' * 3}  {'-' * 20}",
    ]

    for result in results:
        lever = result["lever"]
        flags = []
        if result["relieves_binding"]:
            flags.append("RELIEVES BINDING")
        if result["changes_state"]:
            flags.append(f"-> {result['state_after'].value}")
        if result["d_food_days"] > 0:
            flags.append(f"+{result['d_food_days']:.1f}d food")
        if result["reversibility"] is Reversibility.LOW:
            flags.append("LOW REVERSIBILITY")
        if result["saturated"]:
            flags.append("SCORE SATURATED — see note")
        lines.append(
            f"  {lever.id:<12} {_money(result['cost_mid']):>8} "
            f"{result['points_per_10k']:>9.2f} "
            f"{result['d_floor']:>+6.1f} {result['d_autonomy']:>+6.1f} "
            f"{lever.lead_months:>3}  {', '.join(flags)}")
        lines.append(f"               {lever.name}")

    if any(r["saturated"] for r in results):
        lines += [
            "",
            "── SCORE SATURATED " + "─" * 28,
            "  These levers change the community but score zero: the relevant",
            "  domain term is already at its cap, so the model cannot see further",
            "  investment. That is a limit of the scoring, not a finding about the",
            "  measure — a sixth civic organisation and a twenty-fifth private well",
            "  are worth something the model has stopped counting. See SCORE-02.",
        ]

    lines += ["", "=" * 72]
    return "\n".join(lines)


def instrument_report(instrument: Instrument) -> str:
    """The active steps for one governance or financial instrument."""
    spec = INSTRUMENT_DB.get(instrument)
    if spec is None:
        return f"No instrument on record: {instrument}"

    lines = [
        "=" * 72,
        f"INSTRUMENT: {instrument.value.upper()}",
        "=" * 72,
        f"Who acts:      {spec.who_acts.value}",
        f"Typical time:  {spec.typical_months} months",
        f"Money source:  {spec.money_source}",
        f"Reversibility: {spec.reversibility.value}",
        "",
        "Steps:",
    ]
    for number, step in enumerate(spec.steps, 1):
        lines.append(f"  {number}. {step}")
    lines += [
        "",
        f"Fails when:    {spec.fails_when}",
    ]
    if spec.notes:
        lines += ["", f"Note: {spec.notes}"]
    lines.append("=" * 72)
    return "\n".join(lines)


def transition_report(profile: CommunityProfile,
                      budget: Optional[float] = None) -> str:
    """The full old-design to new-design pathway, phased."""
    plan = transition_plan(profile, budget=budget)
    before, after = plan["before"], plan["after"]

    lines = [
        "=" * 72,
        f"TRANSITION PATHWAY: {profile.name}",
        "=" * 72,
        f"From: {before['state'].value:<12} overall {before['overall']:>5}  "
        f"autonomy {before['autonomy_overall']:>5}  "
        f"binding: {before['binding_constraint']}",
        f"To:   {after['state'].value:<12} overall {after['overall']:>5}  "
        f"autonomy {after['autonomy_overall']:>5}  "
        f"binding: {after['binding_constraint']}",
        f"Cost: {_money(plan['total_cost_mid'])}"
        + (f" (budget {_money(budget)})" if budget else ""),
        "",
    ]

    for phase in (0, 1, 2):
        steps = [s for s in plan["steps"] if s["phase"] == phase]
        if not steps:
            continue
        lines.append(f"── {PHASE_NAMES[phase]} " + "─" * max(0, 40 - len(PHASE_NAMES[phase])))
        for step in steps:
            lever = step["lever"]
            instruments = ", ".join(i.value for i in lever.instruments)
            lines.append(f"  {lever.id:<12} {lever.name}")
            lines.append(f"               via {instruments}")
            lines.append(f"               {_money(step['cost_mid'])}, "
                         f"{lever.lead_months} months  ->  overall "
                         f"{step['cumulative_overall']}, floor "
                         f"{step['cumulative_floor']}, "
                         f"autonomy {step['cumulative_autonomy']} "
                         f"({step['state'].value})")
            if lever.prerequisites:
                lines.append(f"               after: {', '.join(lever.prerequisites)}")
        lines.append("")

    if plan["low_reversibility"]:
        lines += [
            "── LOCK-IN WARNING " + "─" * 28,
            "  These commit the community for a generation. Debt service and",
            "  assessments are fixed claims on future budgets — they narrow what",
            "  a future council can respond to, which is itself a resilience cost",
            "  the infrastructure score does not measure.",
            "",
        ]
        for lever in plan["low_reversibility"]:
            lines.append(f"    {lever.id:<12} {lever.name}")
        lines.append("")

    lines += [
        "── SEQUENCING NOTE " + "─" * 28,
        "  Phase 0 needs no appropriation and can begin at the next meeting.",
        "  It is also what makes phases 1 and 2 fundable: a standing committee",
        "  can hold a grant, and a skills inventory is what turns a mutual aid",
        "  agreement into a capability. Doing phase 0 late is the most common",
        "  way a transition stalls.",
        "=" * 72,
    ]
    return "\n".join(lines)


# ── Demo ──────────────────────────────────────────────────────

if __name__ == "__main__":
    fairmont = CommunityProfile(
        name="Fairmont, MN", population=10_000, county="Martin",
        grocery_stores=3, days_food_supply_retail=3.0, farmers_market=True,
        community_gardens_acres=0.5, active_farms_local=50,
        grain_elevator_present=True, food_bank_present=True,
        municipal_water=True, wells_private=20, surface_water_sources=3,
        water_treatment_functional=True, backup_power_water_plant=True,
        days_water_reserve=2.0,
        grid_connected=True, local_generation_mw=0.0, solar_installations=5,
        wind_capacity_mw=0.0, backup_generators=10, fuel_reserve_days=5.0,
        hospital_present=True, clinic_present=True, pharmacy_count=3,
        ems_available=True,
        cell_towers=3, internet_providers=2, ham_radio_operators=2,
        community_alert_system=True,
        highway_access=True, rail_access=True, fuel_stations=5,
        skill_holders_identified=2, mutual_aid_networks=1,
        faith_communities=8, civic_organizations=5,
    )

    print(leverage_report(fairmont, scale=LeverScale.SMALL))
    print("")
    print(transition_report(fairmont, budget=250_000))
    print("")
    print(instrument_report(Instrument.REVOLVING_LOAN_FUND))
