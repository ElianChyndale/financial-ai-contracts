"""Deterministic Solidity ABI projection for RiskAttestation."""

from __future__ import annotations

import hashlib
from datetime import UTC
from decimal import Decimal
from typing import Any

from financial_ai_contracts.models import RiskAttestation

RISK_ATTESTATION_ABI_TYPES = [
    "bytes32",
    "bytes32",
    "uint32",
    "uint32",
    "uint8",
    "uint16",
    "string",
    "bytes32",
    "bytes32[]",
    "uint64",
    "uint64",
    "uint8",
    "address",
    "bytes",
    "uint256",
    "uint256",
    "address",
]

SUFFICIENCY_CODES = {"insufficient": 0, "partial": 1, "sufficient": 2}
DECISION_CODES = {"approve": 0, "review": 1, "reject": 2, "abstain": 3}


def identifier_hash(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


def _probability_ppm(value: str) -> int:
    scaled = Decimal(value) * 1_000_000
    integral = int(scaled)
    if Decimal(integral) != scaled:
        raise ValueError("Solidity projection supports at most six probability decimals")
    return integral


def risk_attestation_abi_values(model: RiskAttestation) -> list[Any]:
    issued = int(model.issued_at.astimezone(UTC).timestamp())
    expires = int(model.expires_at.astimezone(UTC).timestamp())
    signature = b"" if model.signature is None else bytes.fromhex(model.signature[2:])
    return [
        identifier_hash(model.attestation_id),
        identifier_hash(model.asset_id),
        _probability_ppm(model.risk_score),
        _probability_ppm(model.confidence),
        SUFFICIENCY_CODES[model.evidence_sufficiency],
        model.recommended_haircut_bps,
        model.model_version,
        bytes.fromhex(model.evidence_root[2:]),
        [identifier_hash(item) for item in model.evidence_ids],
        issued,
        expires,
        DECISION_CODES[model.decision_code],
        model.provider,
        signature,
        int(model.nonce),
        int(model.chain_id),
        model.verifying_contract,
    ]


def encode_risk_attestation(model: RiskAttestation) -> str:
    """ABI-encode the documented Solidity projection."""

    try:
        from eth_abi.abi import encode
    except ImportError as exc:  # pragma: no cover - exercised without dev extra
        raise RuntimeError("ABI encoding requires installation with .[dev]") from exc
    encoded = encode(RISK_ATTESTATION_ABI_TYPES, risk_attestation_abi_values(model))
    return "0x" + encoded.hex()
