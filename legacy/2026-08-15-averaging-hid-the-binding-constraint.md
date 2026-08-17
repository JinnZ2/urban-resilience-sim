# Averaging hid the binding constraint

**Date:** 2026-08-15
**Claim:** SCORE-01 (falsified) → SCORE-04 (successor), plus SCORE-05 (new)
**Module:** `community.py` :: `score_infrastructure()`
**Introduced:** commit `3730556`

---

## Hypothesis

Overall infrastructure resilience is the unweighted mean of six domain scores.

```python
overall = sum(scores.values()) / len(scores)
if overall >= 70:
    state = InfraState.FUNCTIONAL
elif overall >= 50:
    state = InfraState.STRESSED
...
```

## Run 1 — filed 2026-08-14, verdict INCONCLUSIVE

```
── INFRASTRUCTURE: FUNCTIONAL (score 79.7/100) ──
  Water                94.0/100
  Energy               50.0/100     <- weakest
  Medical              85/100
  Communication        80/100
  Social Cohesion      69/100
  Transportation      100/100
```

Fairmont reports **FUNCTIONAL** while its energy domain sits at 50. Suspicious,
but not yet decisive: a single soft domain inside a strong system may genuinely
be tolerable. Logged as inconclusive and left alone.

## Run 2 — filed 2026-08-15, verdict CONTRADICTS

Building `transition.py` supplied the decisive test. Ranking small interventions
by mean-score gain per dollar produces this ordering:

| lever | pts/$10k by mean | change to weakest domain |
|---|---:|---:|
| SKILLS-MAP | 104.00 | +0.0 |
| MUTUAL-AID | 26.67 | +0.0 |
| HAM-NET | 11.03 | +0.0 |
| HOME-SOLAR | 0.59 | **+5.0** |

The mean ranks `SKILLS-MAP` **176× above** `HOME-SOLAR`. But energy is the
domain that binds, and `HOME-SOLAR` is the only small lever that moves it at
all. A planner following the mean would spend every available dollar on the
domains that were already strongest and leave the constraint exactly where it
was — while watching the headline number climb.

That is worse than an inaccurate score. It is a score that **inverts the
advice**. The failure mode of a resilience model is not being imprecise; it is
telling a community to reinforce its strengths while its binding constraint
goes untouched.

## Edited claim — SCORE-04

The reported state is now the lesser of the mean-derived state and the state
implied by the weakest domain:

```python
binding_domain = min(scores, key=lambda d: scores[d])
floor = scores[binding_domain]
state = min(_state_from_score(overall), _state_from_score(floor),
            key=_STATE_ORDER.index)
```

`leverage_analysis()` sorts levers that raise the floor ahead of levers that
only raise the mean.

## Second finding — SCORE-05, dependency scored as resilience

Reading the scoring closely for the fix turned up a separate problem that was
never claimed at all. Three terms award points for **connection to an external
system**:

| term | points | in the scenarios this model runs |
|---|---:|---|
| `municipal_water` | +30 water | fails |
| `grid_connected` | +20 energy | fails |
| `highway_access` | +30 transport | fails |

A town scores for these right up to the moment they stop mattering. That is
service level, not resilience, and the disruption scenarios in
`supply_chain.py` remove those exact systems.

`autonomy_scores()` now recomputes every domain with the externally-supplied
terms zeroed, reported beside the connected score rather than replacing it:

```
  domain                connected      if disconnected
  Water                     94.0            44.0
  Energy                    50.0            30.0  <- binds
  Medical                   85.0            85.0
  Communication             80.0            40.0
  Social Cohesion           69.0            69.0
  Transportation           100.0            50.0

  Autonomy score: 53.0/100
  Exposure gap:   26.7 points
```

A first attempt rescaled each autonomy domain back to a 0–100 range, which
produced transportation at 100 for a town with no highway. That was wrong for
the obvious reason: if a dependency disappears, its points are **gone**, not
redistributed among the survivors. Rescaling restored exactly the comfort the
decomposition existed to remove. The multipliers came back out before the
change was committed.

## Rerun

```
── INFRASTRUCTURE: STRESSED (score 79.7/100) ──
  Binding constraint: energy at 50.0/100
  Mean score says FUNCTIONAL; the weakest domain holds it to STRESSED.
  Autonomy score (external systems removed): 53.0/100
  Exposure gap: 26.7 points
```

The mean is unchanged. What changed is that the constraint is no longer
invisible.

## Unknowns carried forward

Recorded on SCORE-04 and SCORE-05:

- **The floor thresholds may be too harsh.** A domain at 50 is weak, not
  failed, and it now caps the entire assessment at STRESSED. Same thresholds
  for floor and mean is a choice, not a result.
- **Not every domain should be able to bind.** Losing water and losing
  communication are not equivalent failures, and the model treats them so.
- **Medical scores identically in both views**, which is certainly wrong —
  pharmaceutical resupply and staffing are external and entirely unmodelled.
  The autonomy decomposition is weakest exactly where it looks cleanest.
- **Zero may be too harsh for de-energised systems.** A dead municipal system
  still holds water in the tower and the pipe for some hours.

## Related: SCORE-02 strained, not revised

The same leverage run showed three of seven small levers scoring exactly zero
because their domain term was already capped — a sixth civic organisation and a
twenty-fifth private well are worth something the model has stopped counting.
`SCORE-02` was moved to `STRAINED` rather than revised: softening hard caps to
diminishing returns is a scale change across every scoring function in the
repo, and doing it one domain at a time would leave the domains incomparable.
It is a known problem with no fix on record, which is what `STRAINED` is for.
