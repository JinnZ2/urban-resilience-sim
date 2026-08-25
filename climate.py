"""
climate.py — External Forcing Baseline & Stationarity Check
Urban Resilience Simulator
License: CC0

Every number in this repo is calibrated against a historical baseline.
Zone 4 crop viability, "typical" winter storm duration, grain yields per
acre, days of water reserve — each of them encodes an assumption that
the past is a usable guide to the next few decades.

This module records the observed climate indicators that bear on that
assumption, and names which model claims each one strains. It does not
model climate. It exists so that a stale baseline is visible in the code
rather than implied by it.

THE HONEST PART
    Most indicators in the source report have no pathway into this model
    at all. Global mean sea level does not reach a town at 1,180 feet in
    southern Minnesota; Antarctic sea ice extent does not enter any
    calculation here. Those are recorded with an empty `pathway` and
    listed separately by unmodelled_indicators(). Carrying an alarming
    number that changes no output is the decorative-statistic habit the
    assumption ledger exists to prevent.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ── Source ────────────────────────────────────────────────────

SOURCE = (
    "State of the Climate in 2025, 36th annual edition. Bulletin of the "
    "American Meteorological Society vol. 107 no. 8 (August 2026), "
    "American Meteorological Society. 625 scientists, 60 countries. "
    "Covers calendar year 2025."
)

# [CLIMATE-05] Provenance was corrected before entry: the figures arrived
# attributed to a report "published August 2025 covering the 2025 calendar
# year", which cannot be — a report cannot cover a year that has not ended.
# Verified against the AMS publication record: 36th edition, published
# August 2026, covering 2025. The values themselves were not altered.
SOURCE_YEAR = 2025
PUBLISHED = "2026-08"


# ── Indicators ────────────────────────────────────────────────

@dataclass
class Indicator:
    """One observed climate indicator and how (or whether) it reaches this model."""
    id: str
    name: str
    value: str
    year: int
    comparison: str
    record: bool
    bears_on: List[str] = field(default_factory=list)   # claim ids in claims.py
    pathway: str = ""                                   # empty = no route into this model
    note: str = ""


INDICATORS = [

    # ── Reaches the model ──
    Indicator(
        id="CLIM-TEMP",
        name="Global mean surface temperature",
        value="2nd or 3rd warmest year on record",
        year=2025,
        comparison="Records begin mid-1800s. The last 11 years (2015-2025) "
                   "are the 11 warmest.",
        record=False,
        bears_on=["FOOD-01", "FOOD-03", "WATER-02", "CLIMATE-01"],
        pathway="Growing-season length, heat stress on crops and on people "
                "doing physical recovery work, and winter heating load all "
                "sit downstream of this. The model treats every one of them "
                "as a fixed historical figure.",
        note="Set without El Nino support — near-neutral to La Nina-like "
             "conditions prevailed. Previous record years were partly "
             "El Nino-driven, so this is the more informative datapoint: "
             "the baseline itself moved, rather than a warm year riding a "
             "cyclical boost.",
    ),
    Indicator(
        id="CLIM-ZONE",
        name="Sustained warming of the continental interior",
        value="Europe warmest on record; Russia, China, South Korea, "
              "Argentina each 2nd-warmest",
        year=2025,
        comparison="Multi-decade trend, not a single-year excursion.",
        record=False,
        bears_on=["FOOD-10", "CLIMATE-02"],
        pathway="USDA hardiness zones are defined on the mean annual extreme "
                "minimum temperature, and they have been shifting northward. "
                "CROP_DB is titled 'Zone 4 optimized' and carries zone_min / "
                "zone_max on every entry.",
        note="This is the indicator with the most direct route into the "
             "repo, and the route is currently broken — see FOOD-10.",
    ),
    Indicator(
        id="CLIM-CYCLONE",
        name="Tropical cyclone count and intensity",
        value="97 named storms; 5 reached Category 5",
        year=2025,
        comparison="1991-2020 average is 87 named storms. Three of the "
                   "Category 5s were North Atlantic — tied 2nd most for "
                   "that basin.",
        record=False,
        bears_on=["CLIMATE-03"],
        pathway="Indirect only. Southern Minnesota does not receive tropical "
                "cyclones. The route into this model is through national "
                "supply chains and insurance markets — real, but long, and "
                "not quantified anywhere in supply_chain.py.",
        note="Hurricane Melissa: 190 mph, 892 hPa, Category 5 landfall in "
             "Jamaica, 95 fatalities, >$12.2B damage. Cyclone Zelia flooded "
             "Marble Bar, Western Australia nearly 2 m above prior records. "
             "Cited as evidence that event severity distributions are "
             "moving, not as a hazard to Fairmont.",
    ),
    Indicator(
        id="CLIM-PRECIP",
        name="Hydrological volatility",
        value="87% of the ocean surface saw at least one marine heatwave; "
              "Arctic tundra greenness 3rd highest on record",
        year=2025,
        comparison="Tundra greening attributed to warming plus increased "
                   "precipitation.",
        record=False,
        bears_on=["WATER-01", "WATER-03", "CLIMATE-01"],
        pathway="A warmer atmosphere holds more water and delivers it less "
                "evenly. surface_water_sources is scored in community.py as "
                "a static count with no reliability term, and days_water_"
                "reserve is sized against historical demand.",
        note="The model counts a lake as a lake. It has no representation "
             "of a lake that is lower than it used to be in August.",
    ),

    # ── No pathway into this model ──
    Indicator(
        id="CLIM-CO2",
        name="Atmospheric carbon dioxide",
        value="425.6 ppm",
        year=2025,
        comparison="53% above the pre-industrial ~278 ppm. Record high.",
        record=True,
        note="Fossil fuel CO2 emissions also hit a record 10.3 petagrams of "
             "carbon per year, more than 3x the 1960s rate.",
    ),
    Indicator(
        id="CLIM-CH4",
        name="Atmospheric methane",
        value="1,935.7 ppb",
        year=2025,
        comparison="166% above pre-industrial. Record high.",
        record=True,
    ),
    Indicator(
        id="CLIM-N2O",
        name="Atmospheric nitrous oxide",
        value="338.9 ppb",
        year=2025,
        comparison="26% above pre-industrial. Record high.",
        record=True,
    ),
    Indicator(
        id="CLIM-OHC",
        name="Ocean heat content, surface to 2,000 m",
        value="Record high",
        year=2025,
        comparison="Oceans have absorbed ~90% of excess trapped heat over "
                   "the past half century.",
        record=True,
    ),
    Indicator(
        id="CLIM-SLR",
        name="Global mean sea level",
        value="111.2 mm above the 1993 baseline",
        year=2025,
        comparison="Record high for the 14th consecutive year. Thermal "
                   "expansion ~1.6 mm/yr, ice melt ~2.0 mm/yr.",
        record=True,
        note="No pathway to an inland community at roughly 1,180 ft "
             "elevation. Recorded for completeness, not for scoring.",
    ),
    Indicator(
        id="CLIM-SST",
        name="Sea surface temperature",
        value="3rd highest in the 172-year record",
        year=2025,
        comparison="Reached despite cool ENSO conditions.",
        record=False,
    ),
    Indicator(
        id="CLIM-ARCTIC",
        name="Arctic sea ice and warming",
        value="Lowest maximum extent in the 47-year satellite record",
        year=2025,
        comparison="2nd-warmest year in the 126-year Arctic record. Surface "
                   "air temperatures rising ~3x the global rate. Minimum "
                   "extent 11th lowest.",
        record=True,
        note="Multi-year ice collapse: ice older than 4 years fell to "
             "95,000 km2 in September 2025, from ~1.5 million km2 in the "
             "1980s. More than half the winter pack is now under one year "
             "old. No pathway into this model, which has no cryosphere and "
             "no polar-amplification term — but it is the clearest single "
             "measure in the report that a baseline has moved rather than "
             "wobbled.",
    ),
    Indicator(
        id="CLIM-ANTARCTIC",
        name="Antarctic warmth and sea ice",
        value="Warmest year since records began in 1979",
        year=2025,
        comparison="Annual daily maximum and minimum sea ice extents were "
                   "3rd and 4th lowest. Below average for nearly a decade.",
        record=True,
        note="Surface melt above average on most ice shelves; Antarctic "
             "Peninsula melt approached record levels in early January.",
    ),
    Indicator(
        id="CLIM-GLACIER",
        name="Global reference glacier mass balance",
        value="38th consecutive year of loss",
        year=2025,
        comparison="Loss exceeded 1 m water equivalent for the 4th straight "
                   "year. ~41% of all loss since 1976 occurred in the last "
                   "decade.",
        record=False,
        note="No pathway here. Relevant to communities on glacier-fed "
             "water, which Fairmont is not.",
    ),
]


# ── Queries ───────────────────────────────────────────────────

def indicator_by_id(indicator_id: str,
                    indicators: Optional[List[Indicator]] = None) -> Optional[Indicator]:
    indicators = INDICATORS if indicators is None else indicators
    for indicator in indicators:
        if indicator.id == indicator_id:
            return indicator
    return None


def modelled_indicators(indicators: Optional[List[Indicator]] = None) -> List[Indicator]:
    """Indicators with an actual route into this model's calculations."""
    indicators = INDICATORS if indicators is None else indicators
    return [i for i in indicators if i.pathway]


def unmodelled_indicators(indicators: Optional[List[Indicator]] = None) -> List[Indicator]:
    """Indicators recorded for completeness that change no output here.

    Kept visible on purpose. An indicator with no pathway is not evidence
    about this community, and listing it beside the ones that do carry
    weight is how that stays obvious.
    """
    indicators = INDICATORS if indicators is None else indicators
    return [i for i in indicators if not i.pathway]


def indicators_bearing_on(claim_id: str,
                          indicators: Optional[List[Indicator]] = None) -> List[Indicator]:
    """Which observed indicators strain a given model claim."""
    indicators = INDICATORS if indicators is None else indicators
    return [i for i in indicators if claim_id in i.bears_on]


def strained_claims(indicators: Optional[List[Indicator]] = None) -> dict:
    """Map every claim id this data bears on to the indicators that bear on it."""
    indicators = INDICATORS if indicators is None else indicators
    out = {}
    for indicator in indicators:
        for claim_id in indicator.bears_on:
            out.setdefault(claim_id, []).append(indicator.id)
    return out


# ── Reports ───────────────────────────────────────────────────

def climate_report(indicators: Optional[List[Indicator]] = None) -> str:
    """The observed record, split by whether it reaches this model."""
    indicators = INDICATORS if indicators is None else indicators
    modelled = modelled_indicators(indicators)
    unmodelled = unmodelled_indicators(indicators)

    lines = [
        "=" * 72,
        f"EXTERNAL FORCING BASELINE — {SOURCE_YEAR}",
        "=" * 72,
        SOURCE,
        "",
        f"── REACHES THIS MODEL ({len(modelled)}) " + "─" * 30,
        "",
    ]
    for indicator in modelled:
        lines.append(f"  [{indicator.id}] {indicator.name}")
        lines.append(f"      {indicator.value}")
        lines.append(f"      vs: {indicator.comparison}")
        lines.append(f"      route: {indicator.pathway}")
        if indicator.bears_on:
            lines.append(f"      strains: {', '.join(indicator.bears_on)}")
        if indicator.note:
            lines.append(f"      note: {indicator.note}")
        lines.append("")

    lines += [
        f"── RECORDED, NO PATHWAY INTO THIS MODEL ({len(unmodelled)}) " + "─" * 14,
        "",
        "  These are real and they are not evidence about this community.",
        "  They change no output here. Listed so that stays obvious.",
        "",
    ]
    for indicator in unmodelled:
        flag = " [RECORD]" if indicator.record else ""
        lines.append(f"  [{indicator.id}] {indicator.name}: {indicator.value}{flag}")
        lines.append(f"      {indicator.comparison}")
        if indicator.note:
            lines.append(f"      note: {indicator.note}")
    lines += ["", "=" * 72]
    return "\n".join(lines)


def stationarity_report(indicators: Optional[List[Indicator]] = None) -> str:
    """Which model assumptions rest on a baseline the data says has moved."""
    indicators = INDICATORS if indicators is None else indicators
    mapping = strained_claims(indicators)

    lines = [
        "=" * 72,
        "STATIONARITY CHECK",
        "=" * 72,
        "This model's numbers are calibrated on historical conditions. That is",
        "an assumption, and it is now a claim on record — CLIMATE-01.",
        "",
        "The single most load-bearing line in the source report is not a record",
        "value. It is that the warmth was reached with NO El Nino support. A",
        "record set on a cyclical boost is a warm year; a record set without one",
        "is a moved baseline. Every historical calibration in this repo assumes",
        "the opposite.",
        "",
        f"── CLAIMS STRAINED BY OBSERVED DATA ({len(mapping)}) " + "─" * 22,
        "",
    ]
    for claim_id in sorted(mapping):
        lines.append(f"  {claim_id:<12} strained by: {', '.join(sorted(mapping[claim_id]))}")
    lines += [
        "",
        "── WHAT THIS DOES NOT DO " + "─" * 46,
        "",
        "  No constant in this repo was changed on the strength of this data.",
        "  A global indicator does not license a specific local number: knowing",
        "  that growing seasons are lengthening does not tell you what Zone 4",
        "  corn yields next year. The strain is recorded, the unknowns are",
        "  named, and the numbers stay put until something local is measured.",
        "",
        "  Changing them now would produce a model that is differently wrong",
        "  and newly confident, which is worse than one that is honestly stale.",
        "=" * 72,
    ]
    return "\n".join(lines)


# ── Demo ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print(climate_report())
    print("")
    print(stationarity_report())
