# Contract Authoring Guide

## Decide whether a field belongs here

A field belongs in this repository only when two or more independent consumers need
the same meaning and representation. Project-specific ranking features, UI state,
database keys, prompts, and execution policies remain in their owning projects.

## Adding or changing a field

1. State the interoperability problem.
2. Define the field's type, unit, range, null behavior, and time semantics.
3. Decide whether the change is patch, minor, or major under `VERSIONING.md`.
4. Update the JSON Schema first.
5. Update the Pydantic model and TypeScript interface.
6. Update the Solidity projection only if the field belongs on chain.
7. Add valid, invalid, boundary, canonical, and migration fixtures.
8. Regenerate reports and prove there is no unexplained diff.

## Required design choices

- Prefer integer basis points to binary floating-point percentages.
- Use canonical decimal strings for human financial quantities.
- Use explicit UTC offsets for timestamps.
- Distinguish the time information became knowable from the time a fact applies.
- Use null only when absence has a defined meaning.
- Reject unknown fields so version negotiation is visible.
- Put financial assumptions in the record when they affect interpretation.

## Review checklist

- Can Python and TypeScript serialize the same record to identical bytes?
- Does an invalid unit, interval, range, or state transition fail?
- Can an older consumer identify the version before reading new fields?
- Is a migration deterministic and loss-aware?
- Does the documentation avoid claiming that validation proves correctness?
- Do examples remain synthetic and safe to publish?

