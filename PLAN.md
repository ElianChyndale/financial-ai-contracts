# Financial AI Contracts v0.1 Implementation Plan

## Objective

Create an independent, versioned contract repository for interoperable financial-AI
evidence, risk, valuation, benchmark, and experiment records. The repository is a
supporting standards asset and is not a fifth portfolio flagship.

## Scope

1. Publish JSON Schema Draft 2020-12 contracts for:
   - `EvidenceUnit`
   - `RiskAttestation`
   - `ValuationScenario`
   - `BenchmarkCase`
   - `ExperimentRecord`
2. Provide equivalent Pydantic 2 models and TypeScript types.
3. Provide Solidity ABI-compatible structs for the on-chain subset of a risk
   attestation and its evidence references.
4. Define canonical JSON, cross-language hashes, golden vectors, invalid fixtures,
   and deterministic v0-to-v1 migrations.
5. Provide an offline CLI for validation, canonicalization, hashing, migration,
   golden-vector checks, and report generation.
6. Verify Python 3.11/3.12 and Node.js behavior in CI on Ubuntu and Windows.

## Exclusions

- No business logic from EcoQuant, Auralynq, Green Bond Lending, GreenFinanceBench,
  or AI Research Engineering Lab.
- No API server, database, frontend, wallet, private key, model download, or API key.
- No claim that a schema validates financial correctness, regulatory compliance,
  signature authenticity, or production fitness.
- No automatic migration that silently discards unknown fields.

## Milestones

1. Specification and acceptance criteria.
2. Schemas, typed models, validation, canonicalization, and migration.
3. TypeScript and Solidity representations with golden vectors.
4. CLI, fixtures, reports, documentation, and tests.
5. Reproducibility audit, public release, CI, and `v0.1.0` tag.
