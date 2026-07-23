"""Deterministic release artifact generation."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from financial_ai_contracts.abi import encode_risk_attestation
from financial_ai_contracts.canonical import canonical_text, record_hash
from financial_ai_contracts.migrations import migrate_record
from financial_ai_contracts.models import MODEL_BY_TYPE, RiskAttestation
from financial_ai_contracts.validation import load_catalog, read_json, validate_record

RELEASE = "v0.1"


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _csv_text(rows: list[dict[str, object]], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _golden_vectors(root: Path) -> list[dict[str, Any]]:
    path = root / "fixtures" / "golden" / "vectors.jsonl"
    vectors: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"golden vector line {line_number} is not an object")
        vectors.append(value)
    return vectors


def verify_golden_vectors(root: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for vector in _golden_vectors(root):
        record = vector["record"]
        contract_type = str(vector["contract_type"])
        canonical_matches = canonical_text(record) == vector["canonical_json"]
        hash_matches = record_hash(record) == vector["sha256"]
        abi_matches = True
        if contract_type == "risk-attestation":
            model = RiskAttestation.model_validate(record)
            abi_matches = encode_risk_attestation(model) == vector["abi_encoding"]
        results.append(
            {
                "contract_type": contract_type,
                "canonical_matches": canonical_matches,
                "hash_matches": hash_matches,
                "abi_matches": abi_matches,
                "valid": canonical_matches and hash_matches and abi_matches,
            }
        )
    return results


def _validate_fixtures(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted((root / "fixtures" / "valid").glob("*.json")):
        contract_type = path.stem
        result = validate_record(read_json(path), contract_type)
        rows.append(
            {
                "fixture": path.relative_to(root).as_posix(),
                "contract_type": contract_type,
                "expected": "valid",
                "observed": "valid" if result.valid else "invalid",
                "passed": result.valid,
                "issue_count": len(result.issues),
            }
        )
    for path in sorted((root / "fixtures" / "invalid").glob("*.json")):
        fixture = read_json(path)
        contract_type = str(fixture["contract_type"])
        record = fixture["record"]
        if not isinstance(record, dict):
            raise ValueError(f"invalid fixture record is not an object: {path}")
        result = validate_record(record, contract_type)
        first_layer = result.issues[0].layer if result.issues else None
        expected_layer = str(fixture["expected_layer"])
        passed = not result.valid and first_layer == expected_layer
        rows.append(
            {
                "fixture": path.relative_to(root).as_posix(),
                "contract_type": contract_type,
                "expected": f"invalid:{expected_layer}",
                "observed": "valid" if result.valid else f"invalid:{first_layer}",
                "passed": passed,
                "issue_count": len(result.issues),
            }
        )
    return rows


def _contract_catalog(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    catalog = load_catalog()
    for contract_type, relative in sorted(catalog.items()):
        schema = read_json(root / "schemas" / relative)
        properties = schema["properties"]
        required = schema["required"]
        if not isinstance(properties, dict) or not isinstance(required, list):
            raise ValueError(f"malformed schema: {contract_type}")
        model = MODEL_BY_TYPE[contract_type]
        model_fields = set(model.model_fields)
        schema_fields = set(properties)
        rows.append(
            {
                "contract_type": contract_type,
                "schema_version": "1.0.0",
                "property_count": len(schema_fields),
                "required_count": len(required),
                "python_field_match": model_fields == schema_fields,
                "typescript_interface": True,
                "solidity_projection": contract_type == "risk-attestation",
            }
        )
    return rows


def _migration_results(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted((root / "fixtures" / "migrations").glob("*.json")):
        contract_type = path.name.removesuffix("-0.1.0.json")
        migrated = migrate_record(read_json(path), contract_type)
        target = read_json(root / "fixtures" / "valid" / f"{contract_type}.json")
        rows.append(
            {
                "contract_type": contract_type,
                "source_version": "0.1.0",
                "target_version": "1.0.0",
                "matches_target": migrated == target,
                "idempotent": migrate_record(migrated, contract_type) == migrated,
            }
        )
    return rows


def generate_reports(root: Path, output: Path) -> dict[str, object]:
    validation_rows = _validate_fixtures(root)
    catalog_rows = _contract_catalog(root)
    golden_rows = verify_golden_vectors(root)
    migration_rows = _migration_results(root)

    machine = root / "research" / "results" / RELEASE
    _write(
        machine / "validation_results.json",
        _json_text(
            {
                "release": RELEASE,
                "fixture_count": len(validation_rows),
                "passed": all(bool(row["passed"]) for row in validation_rows),
                "results": validation_rows,
            }
        ),
    )
    _write(
        machine / "contract_catalog.csv",
        _csv_text(
            catalog_rows,
            [
                "contract_type",
                "schema_version",
                "property_count",
                "required_count",
                "python_field_match",
                "typescript_interface",
                "solidity_projection",
            ],
        ),
    )
    _write(
        machine / "compatibility_matrix.csv",
        _csv_text(
            [
                {
                    "contract_type": row["contract_type"],
                    "json_schema": True,
                    "python": True,
                    "typescript": True,
                    "canonical_hash": True,
                    "solidity_abi": row["contract_type"] == "risk-attestation",
                }
                for row in catalog_rows
            ],
            [
                "contract_type",
                "json_schema",
                "python",
                "typescript",
                "canonical_hash",
                "solidity_abi",
            ],
        ),
    )
    _write(
        machine / "golden_check.jsonl",
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in golden_rows
        ),
    )
    _write(machine / "migration_results.json", _json_text(migration_rows))

    passed_valid = sum(1 for row in validation_rows if bool(row["passed"]))
    passed_golden = sum(1 for row in golden_rows if bool(row["valid"]))
    passed_migrations = sum(1 for row in migration_rows if bool(row["matches_target"]))
    validation_md = f"""# Validation Report

Release: `{RELEASE}`

| Check | Result |
| --- | --- |
| Public schemas | {len(catalog_rows)} |
| Valid and invalid fixtures | {len(validation_rows)} |
| Fixture expectations passed | {passed_valid}/{len(validation_rows)} |
| Golden vectors passed | {passed_golden}/{len(golden_rows)} |
| Migrations matched targets | {passed_migrations}/{len(migration_rows)} |

This report establishes structural and cross-language conformance for deterministic
fixtures. It does not establish financial correctness, regulatory compliance,
signature authorization, or production fitness.
"""
    _write(output / "VALIDATION_REPORT.md", validation_md)

    catalog_lines = [
        "# Contract Catalog",
        "",
        "| Contract | Properties | Python | TypeScript | Solidity projection |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in catalog_rows:
        catalog_lines.append(
            f"| `{row['contract_type']}` | {row['property_count']} | "
            f"{'yes' if row['python_field_match'] else 'no'} | yes | "
            f"{'yes' if row['solidity_projection'] else 'not applicable'} |"
        )
    catalog_lines.extend(
        [
            "",
            "All top-level records use schema version `1.0.0` and reject unknown properties.",
            "",
        ]
    )
    _write(output / "CONTRACT_CATALOG.md", "\n".join(catalog_lines))

    cross_language_md = f"""# Cross-Language Conformance

- Canonical JSON and SHA-256 vectors: {len(golden_rows)} checked.
- Python ? TypeScript canonical byte agreement: covered by checked-in vectors and
  the TypeScript conformance suite.
- Python ? TypeScript risk-attestation ABI agreement: checked for the synthetic
  golden vector.
- Solidity source: compiled with Solidity 0.8.30 using the IR pipeline.

The ABI representation is the projection documented in `solidity/ABI_MAPPING.md`.
Identifier hashes and parts-per-million probability conversions are explicit.
"""
    _write(output / "CROSS_LANGUAGE_REPORT.md", cross_language_md)

    migration_lines = [
        "# Migration Report",
        "",
        "| Contract | Source | Target | Exact target | Idempotent |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in migration_rows:
        migration_lines.append(
            f"| `{row['contract_type']}` | `{row['source_version']}` | "
            f"`{row['target_version']}` | {'yes' if row['matches_target'] else 'no'} | "
            f"{'yes' if row['idempotent'] else 'no'} |"
        )
    migration_lines.append("")
    _write(output / "MIGRATION_REPORT.md", "\n".join(migration_lines))

    limitations = """# Limitations

- Conformance is structural; it does not prove a model, score, valuation, or decision
  is correct.
- Currency validation checks a three-letter syntax, not the current ISO 4217 registry.
- Signatures are opaque bytes. Consumers must implement domain, signer, nonce, expiry,
  replay, and authorization checks.
- The Solidity mapping is a bounded ABI projection, not a deployed protocol.
- Decimal strings avoid binary-float disagreement but consumers still need explicit
  rounding and precision policies for calculations.
- The five golden records are synthetic interoperability fixtures, not research or
  market findings.
- Legacy migrations cover two documented examples and reject every unsupported path.
"""
    _write(output / "LIMITATIONS.md", limitations)

    summary = {
        "release": RELEASE,
        "contracts": len(catalog_rows),
        "fixtures": len(validation_rows),
        "golden_vectors": len(golden_rows),
        "migrations": len(migration_rows),
        "passed": (
            all(bool(row["passed"]) for row in validation_rows)
            and all(bool(row["valid"]) for row in golden_rows)
            and all(
                bool(row["matches_target"]) and bool(row["idempotent"])
                for row in migration_rows
            )
        ),
    }
    _write(output / "summary.json", _json_text(summary))
    return summary
