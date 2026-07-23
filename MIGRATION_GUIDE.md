# Migration Guide

## Supported v0.1 paths

| Contract | Source | Target |
| --- | --- | --- |
| `EvidenceUnit` | `0.1.0` example | `1.0.0` |
| `RiskAttestation` | `0.1.0` example | `1.0.0` |

The `0.1.0` records are documented legacy examples, not previously released
standards.

```bash
financial-ai-contracts migrate \
  fixtures/migrations/evidence-unit-0.1.0.json \
  --type evidence-unit \
  --output migrated.json
```

The migration checks the exact legacy field set, transforms the record, validates the
target schema and semantic rules, and writes normalized JSON. An unknown source field
causes failure because silently discarding it could lose evidence or risk information.

Passing a valid `1.0.0` record through the same command is idempotent. All other
source/target pairs fail explicitly.
