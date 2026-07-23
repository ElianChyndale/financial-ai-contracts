# Acceptance Criteria

v0.1 is complete only when all items below are proven.

## Contracts

- Exactly five top-level v1 schemas exist and advertise Draft 2020-12.
- Pydantic models and TypeScript interfaces cover every required schema field.
- Solidity compiles and exposes the documented ABI-compatible attestation subset.
- Valid, invalid, boundary, and legacy migration fixtures exist.
- All identifiers, decimal strings, timestamps, intervals, units, hashes, addresses,
  and cross-field rules have tests.

## Interoperability

- Python and TypeScript produce byte-identical canonical JSON and SHA-256 hashes for
  every golden vector.
- Python and TypeScript produce the same ABI bytes for the Solidity attestation
  subset.
- Checked-in generated artifacts are reproducible.
- Unsupported versions and unknown fields fail explicitly.

## Commands

```text
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests scripts
python -m mypy src/financial_ai_contracts
pnpm install --frozen-lockfile
pnpm check
financial-ai-contracts validate --catalog fixtures/valid
financial-ai-contracts verify-golden
financial-ai-contracts report --output reports/v0.1
```

## Release Evidence

- Generated CSV, JSON, and JSONL files parse and contain at least one record.
- Repeated report generation produces identical SHA-256 hashes.
- CI passes on Ubuntu and Windows with Python 3.11 and 3.12.
- The public repository is tagged `v0.1.0` only after the release commit passes CI.
- The portfolio task log records commands, results, release URL, and remaining risks.
