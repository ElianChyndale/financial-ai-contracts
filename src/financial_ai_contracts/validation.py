"""Schema and typed validation entry points."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from financial_ai_contracts.models import MODEL_BY_TYPE, ContractModel, contract_type_from_record


@dataclass(frozen=True)
class ValidationIssue:
    layer: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    contract_type: str | None
    issues: tuple[ValidationIssue, ...]
    model: ContractModel | None = None


def package_schema_root() -> Path:
    root = Path(__file__).resolve().parent / "schema_data"
    if not root.exists():
        raise RuntimeError("packaged schema data is missing")
    return root


def load_catalog(schema_root: Path | None = None) -> dict[str, str]:
    root = schema_root or package_schema_root()
    data = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    contracts = data.get("contracts")
    if not isinstance(contracts, dict) or not contracts:
        raise ValueError("schema catalog has no contracts")
    return {str(key): str(value) for key, value in contracts.items()}


def load_schema(contract_type: str, schema_root: Path | None = None) -> dict[str, Any]:
    root = schema_root or package_schema_root()
    catalog = load_catalog(root)
    relative = catalog.get(contract_type)
    if relative is None:
        raise KeyError(f"unknown contract type: {contract_type}")
    loaded = json.loads((root / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"schema is not an object: {contract_type}")
    schema = cast(dict[str, Any], loaded)
    Draft202012Validator.check_schema(schema)
    return schema


def _json_path(parts: list[object]) -> str:
    if not parts:
        return "$"
    return "$." + ".".join(str(part) for part in parts)


def validate_record(
    record: dict[str, Any],
    contract_type: str | None = None,
    *,
    schema_root: Path | None = None,
) -> ValidationResult:
    resolved_type = contract_type or contract_type_from_record(record)
    if resolved_type is None:
        issue = ValidationIssue("dispatch", "$", "cannot infer exactly one contract type")
        return ValidationResult(False, None, (issue,))
    if resolved_type not in MODEL_BY_TYPE:
        issue = ValidationIssue("dispatch", "$", f"unknown contract type: {resolved_type}")
        return ValidationResult(False, resolved_type, (issue,))

    schema = load_schema(resolved_type, schema_root)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_issues = tuple(
        ValidationIssue("schema", _json_path(list(error.absolute_path)), error.message)
        for error in sorted(
            validator.iter_errors(record),
            key=lambda item: list(item.absolute_path),
        )
    )
    if schema_issues:
        return ValidationResult(False, resolved_type, schema_issues)

    model_class = MODEL_BY_TYPE[resolved_type]
    try:
        model = model_class.model_validate(record)
    except ValidationError as exc:
        issues = tuple(
            ValidationIssue(
                "semantic",
                _json_path(list(item["loc"])),
                str(item["msg"]),
            )
            for item in exc.errors()
        )
        return ValidationResult(False, resolved_type, issues)
    return ValidationResult(True, resolved_type, (), model)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON must be an object: {path}")
    return value
