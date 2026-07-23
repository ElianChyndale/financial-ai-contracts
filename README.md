# Financial AI Contracts

Financial AI Contracts is a small, versioned contract layer for evidence-grounded
financial-AI systems. It publishes interoperable JSON Schema, Python, TypeScript, and
Solidity representations for five records:

- `EvidenceUnit`
- `RiskAttestation`
- `ValuationScenario`
- `BenchmarkCase`
- `ExperimentRecord`

The repository contains no scoring model, valuation engine, lending workflow, wallet,
or private data. Passing validation proves structural conformance; it does not prove
financial correctness, signature authorization, regulatory compliance, or production
fitness.

## Portfolio role

This is a supporting cross-project standards asset. It does not replace or modify the
four portfolio flagships: EcoQuant Pro with PDF Manager support, Auralynq, Green Bond
Lending, and AI Research Engineering Lab. GreenFinanceBench and Research Defence Lab
remain separate supporting assets.

## Why this repository exists

Financial systems frequently disagree on names, units, time semantics, decimal
encoding, and version boundaries. This repository makes those differences explicit:

- one-based pages and bounded evidence;
- `source_time` versus `valid_time`;
- decimal strings and integer basis points;
- issue and expiry ordering;
- answerability and abstention consistency;
- experiment versions, seeds, commits, metrics, and limitations;
- deterministic canonical JSON and cross-language SHA-256 vectors;
- explicit, loss-aware version migrations.

## Quick start

Python 3.11 or newer is required. The default package has no model download and needs
no API key.

```bash
python -m pip install -e ".[dev]"
python -m pytest
financial-ai-contracts validate --catalog fixtures/valid
financial-ai-contracts verify-golden
financial-ai-contracts report --output reports/v0.1
```

TypeScript and Solidity conformance uses Node.js and pnpm:

```bash
pnpm install --frozen-lockfile
pnpm check
```

## CLI

```text
financial-ai-contracts validate PATH [--type CONTRACT]
financial-ai-contracts canonicalize INPUT [--output FILE]
financial-ai-contracts hash INPUT
financial-ai-contracts migrate INPUT --type CONTRACT [--target 1.0.0]
financial-ai-contracts verify-golden
financial-ai-contracts report --output reports/v0.1
```

Validation runs JSON parsing, Draft 2020-12 schema validation, Pydantic validation,
and semantic cross-field checks. `canonicalize` and `hash` refuse invalid records.
`migrate` supports only named paths and rejects unknown legacy fields.

## Repository map

```text
schemas/                         public Draft 2020-12 schemas
src/financial_ai_contracts/      Python models, validators, CLI, migration, reports
typescript/                      strict TypeScript types and conformance code
solidity/                        documented ABI projection and compile target
fixtures/valid/                  five synthetic valid records
fixtures/invalid/                schema and semantic failure records
fixtures/migrations/             documented legacy records
fixtures/golden/                 canonical JSON, SHA-256, and ABI vectors
research/results/v0.1/           machine-readable release evidence
reports/v0.1/                    human-readable release evidence
tests/                           Python conformance and CLI tests
```

## Version status

Repository release `v0.1.0` publishes record schema `1.0.0`. Repository and schema
versions are independent. See [VERSIONING.md](VERSIONING.md) and
[SCHEMA_CHANGELOG.md](SCHEMA_CHANGELOG.md).

## Synthetic fixture notice

Every entity, amount, score, signature byte sequence, document, experiment result,
and address in `fixtures/` is synthetic test data. The fixtures are interoperability
inputs, not observations about real issuers, bonds, models, or markets. The byte
sequence in `signature` is not a trusted or verified signature.

## Documentation

- [Specification](SPEC.md)
- [Data model](DATA_MODEL.md)
- [Acceptance criteria](ACCEPTANCE_CRITERIA.md)
- [Canonicalization](docs/CANONICALIZATION.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)
- [Migration guide](MIGRATION_GUIDE.md)
- [Contract authoring guide](CONTRACT_AUTHORING_GUIDE.md)
- [Limitations](LIMITATIONS.md)
- [Security policy](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).

