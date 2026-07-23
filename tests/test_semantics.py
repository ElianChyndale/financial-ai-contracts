from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from financial_ai_contracts.models import (
    UINT256_MAX,
    RiskAttestation,
)
from financial_ai_contracts.validation import validate_record


def test_open_valid_time_interval_is_allowed(valid_records: dict[str, dict[str, Any]]) -> None:
    record = deepcopy(valid_records["evidence-unit"])
    record["valid_time"]["end"] = None
    assert validate_record(record, "evidence-unit").valid


def test_bounding_box_must_have_positive_area(valid_records: dict[str, dict[str, Any]]) -> None:
    record = deepcopy(valid_records["evidence-unit"])
    record["bounding_box"] = {"x0": 0.5, "y0": 0.2, "x1": 0.5, "y1": 0.3}
    result = validate_record(record, "evidence-unit")
    assert not result.valid
    assert result.issues[0].layer == "semantic"


@pytest.mark.parametrize("field", ["risk_score", "confidence"])
def test_probability_boundaries(
    field: str,
    valid_records: dict[str, dict[str, Any]],
) -> None:
    for value in ("0", "1", "0.000001", "1.000000"):
        record = deepcopy(valid_records["risk-attestation"])
        record[field] = value
        assert validate_record(record, "risk-attestation").valid
    record = deepcopy(valid_records["risk-attestation"])
    record[field] = "0.0000001"
    assert not validate_record(record, "risk-attestation").valid


def test_uint256_maximum_is_allowed(valid_records: dict[str, dict[str, Any]]) -> None:
    record = deepcopy(valid_records["risk-attestation"])
    record["nonce"] = str(UINT256_MAX)
    assert validate_record(record, "risk-attestation").valid


def test_unanswerable_case_rules(valid_records: dict[str, dict[str, Any]]) -> None:
    record = deepcopy(valid_records["benchmark-case"])
    record.update(
        {
            "question_type": "unanswerable",
            "answerable": False,
            "gold_answer": None,
            "gold_evidence_ids": [],
            "abstention_expected": True,
            "unanswerable_reasons": ["No supporting evidence is present."],
        }
    )
    assert validate_record(record, "benchmark-case").valid


def test_currency_answer_requires_currency(valid_records: dict[str, dict[str, Any]]) -> None:
    record = deepcopy(valid_records["benchmark-case"])
    record["gold_answer"]["currency"] = None
    result = validate_record(record, "benchmark-case")
    assert not result.valid
    assert result.issues[0].layer == "semantic"


def test_model_json_normalizes_timezone(valid_records: dict[str, dict[str, Any]]) -> None:
    record = deepcopy(valid_records["risk-attestation"])
    record["issued_at"] = "2025-03-01T13:00:00+01:00"
    model = RiskAttestation.model_validate(record)
    dumped = model.model_dump(mode="json")
    assert dumped["issued_at"] == "2025-03-01T12:00:00Z"

