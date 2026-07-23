from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from financial_ai_contracts.abi import encode_risk_attestation
from financial_ai_contracts.canonical import canonical_text, record_hash
from financial_ai_contracts.models import RiskAttestation
from financial_ai_contracts.reporting import verify_golden_vectors


def _vectors(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_canonical_profile_is_order_independent() -> None:
    first = {"é": [3, {"b": True, "a": None}], "a": "text"}
    second = {"a": "text", "é": [3, {"a": None, "b": True}]}
    assert canonical_text(first) == canonical_text(second)
    assert record_hash(first) == record_hash(second)


def test_golden_vectors_match_python(project_root: Path) -> None:
    rows = verify_golden_vectors(project_root)
    assert len(rows) == 5
    assert all(row["valid"] for row in rows)


def test_risk_abi_encoding_matches_golden(project_root: Path) -> None:
    vectors = _vectors(project_root / "fixtures" / "golden" / "vectors.jsonl")
    vector = next(item for item in vectors if item["contract_type"] == "risk-attestation")
    model = RiskAttestation.model_validate(vector["record"])
    encoded = encode_risk_attestation(model)
    assert encoded == vector["abi_encoding"]
    assert encoded.startswith("0x")
    assert len(encoded) > 64

