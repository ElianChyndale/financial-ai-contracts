# Integration Guide

## Producer

1. Select an exact schema version.
2. Construct the record using documented units and UTC time rules.
3. Validate it.
4. Canonicalize and hash it.
5. Persist the record, version, and hash together.

## Consumer

1. Reject unsupported schema versions before interpretation.
2. Validate structure and semantic rules.
3. Recompute the canonical hash if integrity matters.
4. Apply local business, authorization, financial, and regulatory rules.
5. Preserve the original record for audit.

## Boundary with portfolio projects

This repository is not imported into the existing portfolio projects in v0.1. Future
adoption should occur through explicit adapters and compatibility tests. An adapter
must not rename a project field or convert a unit without recording the transformation.

GreenFinanceBench may map its richer native benchmark records into the common
`BenchmarkCase` subset. EcoQuant and Green Bond Lending may later exchange evidence,
valuation, and attestation records. Those integrations require separate plans and
must not be inferred from the presence of these schemas.

