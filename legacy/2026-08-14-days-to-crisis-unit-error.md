# Days-to-crisis formula: years added to days

**Date:** 2026-08-14
**Claim:** FOOD-06 (falsified) → FOOD-07 (successor)
**Module:** `community.py` :: `local_production_capacity()`
**Introduced:** commit `3730556`, "Add CLAUDE.md and source files for Urban Resilience Simulator"

---

## Hypothesis

Days a community can last with no resupply is its retail food buffer plus
whatever its local production adds:

```python
"days_until_crisis_no_resupply": round(
    profile.days_food_supply_retail + (total_local_annual / daily_need / 365)
    if daily_need > 0 else 0, 1
),
```

## Run

`python community.py` — the Fairmont, MN demo profile.

```
── FOOD SECURITY: SURPLUS ──
  Daily caloric need:      20,000,000 cal
  Local production:        328.8% of need
  Retail buffer:           3 days
  Days to crisis (no resupply): 6.3
```

## Falsified

The report contradicts itself. A community producing **328.8% of its annual
caloric need** locally is simultaneously reported to reach crisis in **6.3
days**. A town with more than three years of food in the ground does not starve
in a week. Both numbers come from the same function, computed from the same
inputs, and they cannot both be right.

The error is dimensional, in the second term:

| Quantity | Value | Unit |
|---|---:|---|
| `total_local_annual` | 24,001,500,000 | kcal/year |
| `daily_need` | 20,000,000 | kcal/day |
| `total_local_annual / daily_need` | 1,200.08 | **days** |
| `… / 365` | 3.29 | **years** |
| `+ days_food_supply_retail` | 3.29 + 3 | years + days |

Dividing annual calories by daily need already yields a count of days. The
extra `/ 365` converts days into years, and the result is then added to a
figure in days as though the units matched. The headline output was wrong by a
factor of ~191.

Worth noting what did *not* catch this: the module runs clean, raises nothing,
and produces a plausible-looking small number. Only the adjacent line — the
328.8% surplus — made it visibly false. An implausible output next to a
plausible one is worth more than either alone.

## Edited claim

```python
# Claim FOOD-07 (see claims.py). (annual kcal / daily kcal) is already a
# count of days — the earlier formula divided it by 365 again, adding
# years to days. Upper bound only: assumes the full annual harvest is in
# hand on day one and draws down at a flat rate. See legacy/ for FOOD-06.
"days_until_crisis_no_resupply": round(
    profile.days_food_supply_retail + (total_local_annual / daily_need)
    if daily_need > 0 else 0, 1
),
```

## Rerun

```
── FOOD SECURITY: SURPLUS ──
  Daily caloric need:      20,000,000 cal
  Local production:        328.8% of need
  Retail buffer:           3 days
  Days to crisis (no resupply): 1203.1
```

1,203.1 days ≈ 3.3 years, which is now consistent with the 328.8% annual
surplus reported one line above. The internal contradiction is gone.

## Unknowns carried forward

The successor is dimensionally sound but is **an upper bound, not a forecast**.
It assumes the entire annual harvest is in hand on day one and can be drawn
down at a flat daily rate. Three things would have to be known to do better —
all recorded in FOOD-07's `unknowns`:

- **Harvest timing.** Annual production is not available on day one. A
  disruption in March sits at the bottom of the storage curve; the same
  disruption in October sits at the top. The current model cannot tell them
  apart, and the difference is the whole question.
- **Storage losses.** Spoilage, rodents, and freezing over a year of storage
  are not modelled at all.
- **Processing capacity.** Standing corn is not flour. Drying, canning, and
  refrigeration all assume energy that the grid-down scenarios explicitly
  remove.

There is also a separate, larger problem this fix does **not** touch: FOOD-08,
which is `STRAINED`. The 328.8% figure counts commodity corn and soy acreage as
directly edible human calories. The demo profile itself annotates those farms
as "mostly commodity". Fixing the arithmetic made the number self-consistent;
it did not make it true. That one is still open.
