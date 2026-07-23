"""Explicit, loss-aware legacy record migrations."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from financial_ai_contracts.validation import validate_record

Migration = Callable[[dict[str, Any]], dict[str, Any]]


def _require_exact_fields(record: dict[str, Any], expected: set[str]) -> None:
    actual = set(record)
    missing = expected - actual
    unknown = actual - expected
    if missing or unknown:
        details: list[str] = []
        if missing:
            details.append(f"missing={sorted(missing)}")
        if unknown:
            details.append(f"unknown={sorted(unknown)}")
        raise ValueError("legacy migration field mismatch: " + ", ".join(details))


def _evidence_0_1_to_1(record: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version",
        "id",
        "documentId",
        "documentSha256",
        "pageIndex",
        "section",
        "text",
        "box",
        "sourceTime",
        "validFrom",
        "validUntil",
        "issuerId",
        "bondId",
    }
    _require_exact_fields(record, expected)
    document_hash = str(record["documentSha256"])
    if not document_hash.startswith("0x"):
        document_hash = "0x" + document_hash
    return {
        "schema_version": "1.0.0",
        "evidence_id": record["id"],
        "document_id": record["documentId"],
        "document_hash": document_hash,
        "page": int(record["pageIndex"]) + 1,
        "section": record["section"],
        "text": record["text"],
        "bounding_box": record["box"],
        "source_time": record["sourceTime"],
        "valid_time": {
            "start": record["validFrom"],
            "end": record["validUntil"],
        },
        "issuer_id": record["issuerId"],
        "bond_id": record["bondId"],
    }


def _risk_0_1_to_1(record: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version",
        "id",
        "assetId",
        "riskScore",
        "confidence",
        "evidenceSufficiency",
        "haircutBps",
        "modelVersion",
        "evidenceRoot",
        "evidenceIds",
        "issuedAt",
        "expiresAt",
        "decision",
        "provider",
        "signature",
        "nonce",
        "chainId",
        "verifyingContract",
    }
    _require_exact_fields(record, expected)
    return {
        "schema_version": "1.0.0",
        "attestation_id": record["id"],
        "asset_id": record["assetId"],
        "risk_score": record["riskScore"],
        "confidence": record["confidence"],
        "evidence_sufficiency": record["evidenceSufficiency"],
        "recommended_haircut_bps": record["haircutBps"],
        "model_version": record["modelVersion"],
        "evidence_root": record["evidenceRoot"],
        "evidence_ids": record["evidenceIds"],
        "issued_at": record["issuedAt"],
        "expires_at": record["expiresAt"],
        "decision_code": record["decision"],
        "provider": record["provider"],
        "signature": record["signature"],
        "nonce": str(record["nonce"]),
        "chain_id": str(record["chainId"]),
        "verifying_contract": record["verifyingContract"],
    }


MIGRATIONS: dict[tuple[str, str, str], Migration] = {
    ("evidence-unit", "0.1.0", "1.0.0"): _evidence_0_1_to_1,
    ("risk-attestation", "0.1.0", "1.0.0"): _risk_0_1_to_1,
}


def migrate_record(
    record: dict[str, Any],
    contract_type: str,
    target_version: str = "1.0.0",
) -> dict[str, Any]:
    """Migrate a supported record and validate the exact target result."""

    source_version = record.get("schema_version")
    if not isinstance(source_version, str):
        raise ValueError("record has no string schema_version")
    if source_version == target_version:
        result = deepcopy(record)
    else:
        migration = MIGRATIONS.get((contract_type, source_version, target_version))
        if migration is None:
            raise ValueError(
                f"unsupported migration: {contract_type} {source_version} -> {target_version}"
            )
        result = migration(deepcopy(record))

    validation = validate_record(result, contract_type)
    if not validation.valid:
        messages = "; ".join(f"{issue.path}: {issue.message}" for issue in validation.issues)
        raise ValueError(f"migrated record is invalid: {messages}")
    assert validation.model is not None
    return validation.model.model_dump(mode="json")
