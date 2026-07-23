"""Pydantic representations and semantic rules for the v1 contracts."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

Identifier = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9._:-]{2,127}$")]
Bytes32 = Annotated[str, Field(pattern=r"^0x[0-9a-f]{64}$")]
Address = Annotated[str, Field(pattern=r"^0x[0-9a-f]{40}$")]
DecimalString = Annotated[
    str,
    Field(pattern=r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$"),
]
NonNegativeDecimalString = Annotated[
    str,
    Field(pattern=r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$"),
]
Uint256String = Annotated[str, Field(pattern=r"^(?:0|[1-9][0-9]*)$", max_length=78)]
SCHEMA_VERSION = "1.0.0"
UINT256_MAX = 2**256 - 1


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return value


def _decimal(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal string") from exc
    if not result.is_finite():
        raise ValueError("decimal value must be finite")
    return result


class StrictModel(BaseModel):
    """Shared strict object behavior and UTC serialization."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @field_serializer("*", when_used="json")
    def serialize_values(self, value: object) -> object:
        if isinstance(value, datetime):
            normalized = value.astimezone(UTC)
            return normalized.isoformat(timespec="seconds").replace("+00:00", "Z")
        if isinstance(value, date):
            return value.isoformat()
        return value


class ContractModel(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"


class TimeInterval(StrictModel):
    start: datetime
    end: datetime | None

    @field_validator("start", "end")
    @classmethod
    def aware_times(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _require_aware(value)

    @model_validator(mode="after")
    def ordered(self) -> TimeInterval:
        if self.end is not None and self.end <= self.start:
            raise ValueError("valid_time.end must be later than start")
        return self


class BoundingBox(StrictModel):
    x0: Annotated[float, Field(ge=0, le=1)]
    y0: Annotated[float, Field(ge=0, le=1)]
    x1: Annotated[float, Field(ge=0, le=1)]
    y1: Annotated[float, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def ordered(self) -> BoundingBox:
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("bounding box must have positive width and height")
        return self


class EvidenceUnit(ContractModel):
    evidence_id: Identifier
    document_id: Identifier
    document_hash: Bytes32
    page: Annotated[int, Field(ge=1)]
    section: Annotated[str, Field(min_length=1, max_length=256)] | None
    text: Annotated[str, Field(min_length=1, max_length=20000)]
    bounding_box: BoundingBox | None
    source_time: datetime
    valid_time: TimeInterval
    issuer_id: Identifier | None
    bond_id: Identifier | None

    @field_validator("source_time")
    @classmethod
    def aware_source_time(cls, value: datetime) -> datetime:
        return _require_aware(value)


class RiskAttestation(ContractModel):
    attestation_id: Identifier
    asset_id: Identifier
    risk_score: NonNegativeDecimalString
    confidence: NonNegativeDecimalString
    evidence_sufficiency: Literal["insufficient", "partial", "sufficient"]
    recommended_haircut_bps: Annotated[int, Field(ge=0, le=10000)]
    model_version: Annotated[
        str,
        Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$"),
    ]
    evidence_root: Bytes32
    evidence_ids: Annotated[list[Identifier], Field(min_length=1)]
    issued_at: datetime
    expires_at: datetime
    decision_code: Literal["approve", "review", "reject", "abstain"]
    provider: Address
    signature: Annotated[str, Field(pattern=r"^0x(?:[0-9a-f]{2})+$")] | None
    nonce: Uint256String
    chain_id: Uint256String
    verifying_contract: Address

    @field_validator("risk_score", "confidence")
    @classmethod
    def probability_range(cls, value: str) -> str:
        number = _decimal(value)
        if number < 0 or number > 1:
            raise ValueError("probability must be between 0 and 1")
        if "." in value and len(value.split(".", maxsplit=1)[1]) > 6:
            raise ValueError("probability supports at most six decimals")
        return value

    @field_validator("nonce", "chain_id")
    @classmethod
    def uint256_range(cls, value: str) -> str:
        if int(value) > UINT256_MAX:
            raise ValueError("value exceeds uint256")
        return value

    @field_validator("issued_at", "expires_at")
    @classmethod
    def aware_times(cls, value: datetime) -> datetime:
        return _require_aware(value)

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids must be unique")
        return value

    @model_validator(mode="after")
    def semantic_rules(self) -> RiskAttestation:
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be later than issued_at")
        if self.evidence_sufficiency == "insufficient" and self.decision_code == "approve":
            raise ValueError("insufficient evidence cannot produce approve")
        return self


class CashFlow(StrictModel):
    payment_date: date
    amount: NonNegativeDecimalString


class ValuationScenario(ContractModel):
    scenario_id: Identifier
    bond_id: Identifier
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    valuation_date: date
    face_value: NonNegativeDecimalString
    base_yield: DecimalString
    spread_adjustment_bps: Annotated[int, Field(ge=-100000, le=100000)]
    cash_flows: Annotated[list[CashFlow], Field(min_length=1)]
    present_value: NonNegativeDecimalString
    duration_years: NonNegativeDecimalString
    convexity_years2: NonNegativeDecimalString
    z_spread_bps: Annotated[int, Field(ge=-100000, le=100000)]
    assumptions: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=500)]],
        Field(min_length=1),
    ]

    @field_validator("assumptions")
    @classmethod
    def unique_assumptions(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("assumptions must be unique")
        return value

    @model_validator(mode="after")
    def cash_flow_order(self) -> ValuationScenario:
        dates = [flow.payment_date for flow in self.cash_flows]
        if dates != sorted(dates) or len(dates) != len(set(dates)):
            raise ValueError("cash flow dates must be strictly increasing")
        if any(payment_date <= self.valuation_date for payment_date in dates):
            raise ValueError("cash flows must occur after valuation_date")
        return self


class GoldAnswer(StrictModel):
    text: Annotated[str, Field(min_length=1, max_length=5000)]
    numeric_value: DecimalString | None
    unit: Literal["currency", "percent", "basis_points", "ratio", "years", "text"] | None
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")] | None

    @model_validator(mode="after")
    def unit_currency_consistency(self) -> GoldAnswer:
        if self.unit == "currency" and self.currency is None:
            raise ValueError("currency answer requires currency code")
        if self.unit != "currency" and self.currency is not None:
            raise ValueError("currency code is only valid for currency answers")
        if self.numeric_value is None and self.unit not in (None, "text"):
            raise ValueError("non-text unit requires numeric_value")
        return self


class BenchmarkCase(ContractModel):
    case_id: Identifier
    question: Annotated[str, Field(min_length=1, max_length=2000)]
    question_type: Literal[
        "factual",
        "comparison",
        "temporal",
        "numerical",
        "conflict",
        "unanswerable",
    ]
    answerable: bool
    gold_answer: GoldAnswer | None
    document_ids: Annotated[list[Identifier], Field(min_length=1)]
    gold_evidence_ids: list[Identifier]
    abstention_expected: bool
    unanswerable_reasons: list[Annotated[str, Field(min_length=1, max_length=500)]]
    split: Literal["train", "dev", "test"]
    synthetic: bool

    @field_validator("document_ids", "gold_evidence_ids", "unanswerable_reasons")
    @classmethod
    def unique_lists(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("list values must be unique")
        return value

    @model_validator(mode="after")
    def answerability_rules(self) -> BenchmarkCase:
        if self.answerable:
            if self.gold_answer is None:
                raise ValueError("answerable case requires gold_answer")
            if self.abstention_expected:
                raise ValueError("answerable case cannot expect abstention")
            if self.unanswerable_reasons:
                raise ValueError("answerable case cannot have unanswerable reasons")
        else:
            if self.gold_answer is not None:
                raise ValueError("unanswerable case must have null gold_answer")
            if not self.abstention_expected:
                raise ValueError("unanswerable case must expect abstention")
            if not self.unanswerable_reasons:
                raise ValueError("unanswerable case requires a reason")
        if self.question_type == "unanswerable" and self.answerable:
            raise ValueError("unanswerable question type cannot be answerable")
        return self


class MetricValue(StrictModel):
    name: Identifier
    value: DecimalString
    unit: Annotated[str, Field(min_length=1, max_length=64)]


class EnvironmentInfo(StrictModel):
    runtime: Annotated[str, Field(min_length=1, max_length=128)]
    platform: Annotated[str, Field(min_length=1, max_length=128)]
    dependency_lock_hash: Bytes32


class ExperimentRecord(ContractModel):
    experiment_id: Identifier
    dataset_version: Annotated[str, Field(min_length=1, max_length=128)]
    model_version: Annotated[str, Field(min_length=1, max_length=128)]
    prompt_version: Annotated[str, Field(min_length=1, max_length=128)]
    retriever: Annotated[str, Field(min_length=1, max_length=128)]
    seed: Annotated[int, Field(ge=0, le=4294967295)]
    metrics: Annotated[list[MetricValue], Field(min_length=1)]
    commit: Annotated[str, Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")]
    environment: EnvironmentInfo
    started_at: datetime
    completed_at: datetime
    limitations: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=1000)]],
        Field(min_length=1),
    ]

    @field_validator("started_at", "completed_at")
    @classmethod
    def aware_times(cls, value: datetime) -> datetime:
        return _require_aware(value)

    @field_validator("limitations")
    @classmethod
    def unique_limitations(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("limitations must be unique")
        return value

    @field_validator("metrics")
    @classmethod
    def unique_metrics(cls, value: list[MetricValue]) -> list[MetricValue]:
        names = [metric.name for metric in value]
        if len(names) != len(set(names)):
            raise ValueError("metric names must be unique")
        return value

    @model_validator(mode="after")
    def ordered_times(self) -> ExperimentRecord:
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot precede started_at")
        return self


Contract = EvidenceUnit | RiskAttestation | ValuationScenario | BenchmarkCase | ExperimentRecord
MODEL_BY_TYPE: dict[str, type[ContractModel]] = {
    "benchmark-case": BenchmarkCase,
    "evidence-unit": EvidenceUnit,
    "experiment-record": ExperimentRecord,
    "risk-attestation": RiskAttestation,
    "valuation-scenario": ValuationScenario,
}


def contract_type_from_record(record: dict[str, object]) -> str | None:
    """Infer the contract type only from stable top-level identifiers."""

    matches = {
        "benchmark-case": "case_id",
        "evidence-unit": "evidence_id",
        "experiment-record": "experiment_id",
        "risk-attestation": "attestation_id",
        "valuation-scenario": "scenario_id",
    }
    present = [contract_type for contract_type, key in matches.items() if key in record]
    return present[0] if len(present) == 1 else None


def is_canonical_decimal(value: str) -> bool:
    """Return whether a value follows the documented decimal grammar."""

    return bool(re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value))
