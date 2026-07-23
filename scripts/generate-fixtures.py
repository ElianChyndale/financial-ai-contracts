"""Generate deterministic conformance fixtures and golden vectors."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from financial_ai_contracts.abi import encode_risk_attestation
from financial_ai_contracts.canonical import canonical_text, record_hash
from financial_ai_contracts.models import RiskAttestation


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def valid_records() -> dict[str, dict[str, Any]]:
    evidence = {
        "schema_version": "1.0.0",
        "evidence_id": "ev.synthetic.001",
        "document_id": "doc.synthetic.001",
        "document_hash": "0x" + "12" * 32,
        "page": 2,
        "section": "Use of proceeds",
        "text": "The synthetic issuer allocated EUR 40 million to clean transport.",
        "bounding_box": {"x0": 0.1, "y0": 0.2, "x1": 0.9, "y1": 0.3},
        "source_time": "2025-02-01T09:30:00Z",
        "valid_time": {
            "start": "2025-01-01T00:00:00Z",
            "end": "2026-01-01T00:00:00Z",
        },
        "issuer_id": "issuer.synthetic.001",
        "bond_id": "bond.synthetic.001",
    }
    risk = {
        "schema_version": "1.0.0",
        "attestation_id": "att.synthetic.001",
        "asset_id": "asset.synthetic.001",
        "risk_score": "0.275",
        "confidence": "0.8",
        "evidence_sufficiency": "sufficient",
        "recommended_haircut_bps": 750,
        "model_version": "1.2.0",
        "evidence_root": "0x" + "34" * 32,
        "evidence_ids": ["ev.synthetic.001", "ev.synthetic.002"],
        "issued_at": "2025-03-01T12:00:00Z",
        "expires_at": "2025-03-08T12:00:00Z",
        "decision_code": "review",
        "provider": "0x" + "56" * 20,
        "signature": "0x" + "11" * 65,
        "nonce": "42",
        "chain_id": "31337",
        "verifying_contract": "0x" + "78" * 20,
    }
    valuation = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.synthetic.001",
        "bond_id": "bond.synthetic.001",
        "currency": "EUR",
        "valuation_date": "2025-01-01",
        "face_value": "1000.00",
        "base_yield": "0.04",
        "spread_adjustment_bps": 50,
        "cash_flows": [
            {"payment_date": "2026-01-01", "amount": "50.00"},
            {"payment_date": "2027-01-01", "amount": "1050.00"},
        ],
        "present_value": "1000.00",
        "duration_years": "1.90",
        "convexity_years2": "4.25",
        "z_spread_bps": 50,
        "assumptions": [
            "Annual cash flows",
            "Flat synthetic discount curve",
        ],
    }
    benchmark = {
        "schema_version": "1.0.0",
        "case_id": "case.synthetic.001",
        "question": "How much was allocated to clean transport?",
        "question_type": "numerical",
        "answerable": True,
        "gold_answer": {
            "text": "EUR 40 million",
            "numeric_value": "40000000",
            "unit": "currency",
            "currency": "EUR",
        },
        "document_ids": ["doc.synthetic.001"],
        "gold_evidence_ids": ["ev.synthetic.001"],
        "abstention_expected": False,
        "unanswerable_reasons": [],
        "split": "train",
        "synthetic": True,
    }
    experiment = {
        "schema_version": "1.0.0",
        "experiment_id": "experiment.synthetic.001",
        "dataset_version": "synthetic-1.0.0",
        "model_version": "baseline-1.0.0",
        "prompt_version": "none",
        "retriever": "bm25",
        "seed": 42,
        "metrics": [
            {"name": "mrr", "value": "0.75", "unit": "ratio"},
            {"name": "latency_ms", "value": "12.5", "unit": "milliseconds"},
        ],
        "commit": "a" * 40,
        "environment": {
            "runtime": "python-3.11",
            "platform": "synthetic-fixture",
            "dependency_lock_hash": "0x" + "9a" * 32,
        },
        "started_at": "2025-03-01T12:00:00Z",
        "completed_at": "2025-03-01T12:00:01Z",
        "limitations": [
            "Synthetic fixture; not an external research result.",
        ],
    }
    return {
        "benchmark-case": benchmark,
        "evidence-unit": evidence,
        "experiment-record": experiment,
        "risk-attestation": risk,
        "valuation-scenario": valuation,
    }


def invalid_records(valid: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(
        name: str,
        contract_type: str,
        mutate: Any,
        expected_layer: str,
    ) -> None:
        record = deepcopy(valid[contract_type])
        mutate(record)
        cases.append(
            {
                "name": name,
                "contract_type": contract_type,
                "expected_layer": expected_layer,
                "record": record,
            }
        )

    add("unknown-field", "evidence-unit", lambda r: r.update({"extra": True}), "schema")
    add(
        "bounding-box-order",
        "evidence-unit",
        lambda r: r.update({"bounding_box": {"x0": 0.8, "y0": 0.2, "x1": 0.1, "y1": 0.3}}),
        "semantic",
    )
    add(
        "valid-time-order",
        "evidence-unit",
        lambda r: r.update(
            {
                "valid_time": {
                    "start": "2025-01-02T00:00:00Z",
                    "end": "2025-01-01T00:00:00Z",
                }
            }
        ),
        "semantic",
    )
    add(
        "risk-expired-at-issue",
        "risk-attestation",
        lambda r: r.update({"expires_at": r["issued_at"]}),
        "semantic",
    )
    add(
        "insufficient-approve",
        "risk-attestation",
        lambda r: r.update({"evidence_sufficiency": "insufficient", "decision_code": "approve"}),
        "semantic",
    )
    add(
        "uint256-overflow",
        "risk-attestation",
        lambda r: r.update({"nonce": str(2**256)}),
        "semantic",
    )
    add(
        "cash-flow-order",
        "valuation-scenario",
        lambda r: r.update({"cash_flows": list(reversed(r["cash_flows"]))}),
        "semantic",
    )
    add(
        "cash-flow-before-valuation",
        "valuation-scenario",
        lambda r: r["cash_flows"][0].update({"payment_date": "2024-12-31"}),
        "semantic",
    )
    add(
        "answerable-without-answer",
        "benchmark-case",
        lambda r: r.update({"gold_answer": None}),
        "semantic",
    )
    add(
        "unanswerable-with-answer",
        "benchmark-case",
        lambda r: r.update(
            {
                "answerable": False,
                "abstention_expected": True,
                "unanswerable_reasons": ["Evidence is absent."],
            }
        ),
        "semantic",
    )
    add(
        "duplicate-metric",
        "experiment-record",
        lambda r: r["metrics"].append(deepcopy(r["metrics"][0])),
        "semantic",
    )
    add(
        "completion-before-start",
        "experiment-record",
        lambda r: r.update({"completed_at": "2025-02-28T12:00:00Z"}),
        "semantic",
    )
    add(
        "naive-timestamp",
        "experiment-record",
        lambda r: r.update({"started_at": "2025-03-01T12:00:00"}),
        "schema",
    )
    add(
        "noncanonical-decimal",
        "valuation-scenario",
        lambda r: r.update({"face_value": "01.0"}),
        "schema",
    )
    add(
        "bad-currency",
        "valuation-scenario",
        lambda r: r.update({"currency": "eur"}),
        "schema",
    )
    return cases


def migration_records(valid: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    evidence = valid["evidence-unit"]
    legacy_evidence = {
        "schema_version": "0.1.0",
        "id": evidence["evidence_id"],
        "documentId": evidence["document_id"],
        "documentSha256": evidence["document_hash"][2:],
        "pageIndex": evidence["page"] - 1,
        "section": evidence["section"],
        "text": evidence["text"],
        "box": evidence["bounding_box"],
        "sourceTime": evidence["source_time"],
        "validFrom": evidence["valid_time"]["start"],
        "validUntil": evidence["valid_time"]["end"],
        "issuerId": evidence["issuer_id"],
        "bondId": evidence["bond_id"],
    }
    risk = valid["risk-attestation"]
    legacy_risk = {
        "schema_version": "0.1.0",
        "id": risk["attestation_id"],
        "assetId": risk["asset_id"],
        "riskScore": risk["risk_score"],
        "confidence": risk["confidence"],
        "evidenceSufficiency": risk["evidence_sufficiency"],
        "haircutBps": risk["recommended_haircut_bps"],
        "modelVersion": risk["model_version"],
        "evidenceRoot": risk["evidence_root"],
        "evidenceIds": risk["evidence_ids"],
        "issuedAt": risk["issued_at"],
        "expiresAt": risk["expires_at"],
        "decision": risk["decision_code"],
        "provider": risk["provider"],
        "signature": risk["signature"],
        "nonce": int(risk["nonce"]),
        "chainId": int(risk["chain_id"]),
        "verifyingContract": risk["verifying_contract"],
    }
    return {
        "evidence-unit-0.1.0": legacy_evidence,
        "risk-attestation-0.1.0": legacy_risk,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    fixture_root = root / "fixtures"
    valid = valid_records()
    for contract_type, record in valid.items():
        _write_json(fixture_root / "valid" / f"{contract_type}.json", record)

    invalid = invalid_records(valid)
    for fixture in invalid:
        _write_json(fixture_root / "invalid" / f"{fixture['name']}.json", fixture)

    for name, record in migration_records(valid).items():
        _write_json(fixture_root / "migrations" / f"{name}.json", record)

    vectors = []
    for contract_type, record in sorted(valid.items()):
        vector: dict[str, Any] = {
            "contract_type": contract_type,
            "record": record,
            "canonical_json": canonical_text(record),
            "sha256": record_hash(record),
        }
        if contract_type == "risk-attestation":
            vector["abi_encoding"] = encode_risk_attestation(RiskAttestation.model_validate(record))
        vectors.append(vector)
    golden_path = fixture_root / "golden" / "vectors.jsonl"
    golden_path.parent.mkdir(parents=True, exist_ok=True)
    golden_path.write_text(
        "".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n" for item in vectors),
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
