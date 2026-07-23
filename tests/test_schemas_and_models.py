from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from financial_ai_contracts.models import MODEL_BY_TYPE
from financial_ai_contracts.validation import load_catalog, load_schema, validate_record


def test_exactly_five_v1_contracts() -> None:
    catalog = load_catalog()
    assert set(catalog) == {
        "benchmark-case",
        "evidence-unit",
        "experiment-record",
        "risk-attestation",
        "valuation-scenario",
    }


def test_all_schemas_are_valid_draft_2020_12() -> None:
    for contract_type in load_catalog():
        schema = load_schema(contract_type)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)


def test_top_level_schema_and_python_fields_match() -> None:
    for contract_type, model in MODEL_BY_TYPE.items():
        schema = load_schema(contract_type)
        assert set(schema["properties"]) == set(model.model_fields)
        assert set(schema["required"]) == set(model.model_fields)


def test_public_and_packaged_schemas_are_identical(project_root: Path) -> None:
    packaged = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "financial_ai_contracts"
        / "schema_data"
    )
    for public_path in sorted((project_root / "schemas").rglob("*.json")):
        relative = public_path.relative_to(project_root / "schemas")
        assert (packaged / relative).read_bytes() == public_path.read_bytes()


def test_all_valid_fixtures_pass(valid_records: dict[str, dict[str, Any]]) -> None:
    assert len(valid_records) == 5
    for contract_type, record in valid_records.items():
        result = validate_record(record, contract_type)
        assert result.valid, (contract_type, result.issues)
        assert result.model is not None


@pytest.mark.parametrize(
    "path",
    sorted((Path(__file__).resolve().parents[1] / "fixtures" / "invalid").glob("*.json")),
)
def test_invalid_fixture_fails_at_declared_layer(path: Path) -> None:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    result = validate_record(fixture["record"], fixture["contract_type"])
    assert not result.valid
    assert result.issues
    assert result.issues[0].layer == fixture["expected_layer"]


def test_dispatch_rejects_ambiguous_record() -> None:
    result = validate_record({"case_id": "case.one", "evidence_id": "ev.one"})
    assert not result.valid
    assert result.contract_type is None
    assert result.issues[0].layer == "dispatch"
