# legacy/

Superseded work. Kept, not deleted.

## The precedence rule

**A falsified claim keeps its precedence.** When something in this repo is
tested and found wrong, the wrong version is not quietly overwritten — it is
moved here with the evidence that killed it and a pointer to whatever replaced
it. Its claim id is never reused.

This costs a little repo size and buys something worth more: the next person to
look at a number can see whether it has already been tried and rejected, and
why. A model that only shows its current answers hides its own error history,
and an error history is the most informative part of a model that has been
worked on for a while.

The rule applies to whole files, single formulas, constants, and thresholds
alike. Granularity does not matter; provenance does.

## The loop this folder serves

```
    hypothesize   a claim enters claims.py as UNTESTED
         │
         ▼
       run        a module is executed, or its output inspected
         │
         ▼
    falsified     an Observation is filed with verdict CONTRADICTS;
         │        the claim is marked FALSIFIED — never edited in place
         ▼
   edit claim     a NEW claim is written with revision_of pointing back,
         │        and the old one gets superseded_by pointing forward
         ▼
    unknowns      what would be needed to test the successor is written
         │        into its unknowns list
         ▼
      rerun       the successor is observed in turn
```

`claims.py` holds the live ledger. This folder holds the archived record of
what fell out of it. `lineage(claim_id)` in `claims.py` walks any claim back
through every version it replaced, so nothing archived here becomes unreachable
from the working code.

## Archival protocol

When something is superseded:

1. Mark the old claim `FALSIFIED` (evidence killed it) or `SUPERSEDED`
   (replaced without being disproven) in `claims.py`. Do not edit its
   statement — the statement is what was claimed.
2. Write the successor as a new claim with a new id and `revision_of` set.
   Set `superseded_by` on the old one. Supersession is two-way;
   `audit_ledger()` fails the build of the record if it is not.
3. File an `Observation` recording the run that forced the change: the date,
   how it was observed, and what was found. Observations are append-only.
4. Add a dated record in this folder: the old code, its output, and the
   reasoning. One file per falsification, named `YYYY-MM-DD-short-slug.md`.
5. Carry any unresolved questions into the successor's `unknowns` list. A
   revision that answers one question usually opens two.

Whole files that stop being load-bearing move into this folder unchanged, with
a dated note explaining what replaced them.

## Contents

| Record | Claim | What happened |
|--------|-------|---------------|
| [`2026-08-14-days-to-crisis-unit-error.md`](2026-08-14-days-to-crisis-unit-error.md) | FOOD-06 → FOOD-07 | Days-to-crisis formula divided a day count by 365, adding years to days. Falsified by its own demo output. |

## What is not here yet

No whole module has been retired. Everything in the repo root is still
load-bearing. This folder was set up when the practice started, not after a
backlog built up — which is the point. The record is only useful if it exists
before the first thing gets thrown away.

One dead constant is documented but left in place: `CALORIES_PER_ACRE_GARDEN`
in `community.py` is defined and never referenced (claim FOOD-04, status
`RETIRED`). It is annotated rather than deleted because the right resolution —
either wire it up to garden acreage or drop it — depends on a yield observation
nobody has made yet. Deleting it would erase the question.
