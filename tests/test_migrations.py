from __future__ import annotations

from pathlib import Path

import pytest

from financial_ai_contracts.migrations import migrate_record
from financial_ai_contracts.validation import read_json


@pytest.mark.parametrize("contract_type", ["evidence-unit", "risk-attestation"])
def test_legacy_migration_matches_golden_target(project_root: Path, contract_type: str) -> None:
    source = read_json(project_root / "fixtures" / "migrations" / f"{contract_type}-0.1.0.json")
    target = read_json(project_root / "fixtures" / "valid" / f"{contract_type}.json")
    assert migrate_record(source, contract_type) == target


def test_target_migration_is_idempotent(project_root: Path) -> None:
    target = read_json(project_root / "fixtures" / "valid" / "risk-attestation.json")
    assert migrate_record(target, "risk-attestation") == target


def test_legacy_unknown_field_is_not_silently_dropped(project_root: Path) -> None:
    source = read_json(project_root / "fixtures" / "migrations" / "evidence-unit-0.1.0.json")
    source["unexpected"] = "must fail"
    with pytest.raises(ValueError, match="unknown"):
        migrate_record(source, "evidence-unit")


def test_unsupported_migration_fails(project_root: Path) -> None:
    source = read_json(project_root / "fixtures" / "valid" / "benchmark-case.json")
    source["schema_version"] = "0.9.0"
    with pytest.raises(ValueError, match="unsupported migration"):
        migrate_record(source, "benchmark-case")
