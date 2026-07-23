# Data Model

## EvidenceUnit

Represents one bounded evidence item.

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | string | exactly `1.0.0` |
| `evidence_id` | identifier | globally stable within a dataset |
| `document_id` | identifier | source document identifier |
| `document_hash` | bytes32 | SHA-256 of the consumer-defined source bytes |
| `page` | integer | one-based, at least 1 |
| `section` | string/null | optional human-readable section |
| `text` | string | non-empty exact evidence text |
| `bounding_box` | object/null | normalized `x0,y0,x1,y1`; strict ordering |
| `source_time` | timestamp | when the information became knowable |
| `valid_time` | interval | when the represented fact applies |
| `issuer_id` | identifier/null | optional issuer link |
| `bond_id` | identifier/null | optional bond link |

`valid_time.end` is exclusive. A missing end denotes an open interval.

## RiskAttestation

Represents a provider's bounded risk output, not an execution instruction.

| Field | Type | Rule |
| --- | --- | --- |
| `attestation_id` | identifier | stable attestation identifier |
| `asset_id` | identifier | assessed asset |
| `risk_score` | decimal string | inclusive range 0–1 |
| `confidence` | decimal string | inclusive range 0–1 |
| `evidence_sufficiency` | enum | insufficient, partial, sufficient |
| `recommended_haircut_bps` | integer | 0–10000 |
| `model_version` | semver string | producing model/config version |
| `evidence_root` | bytes32 | commitment to ordered evidence references |
| `evidence_ids` | identifier array | non-empty, unique |
| `issued_at` | timestamp | issue time |
| `expires_at` | timestamp | strictly later than issue time |
| `decision_code` | enum | approve, review, reject, abstain |
| `provider` | address | attestation provider address |
| `signature` | bytes/null | optional opaque signature |
| `nonce` | uint256 string | canonical unsigned integer |
| `chain_id` | uint256 string | signature domain chain |
| `verifying_contract` | address | signature domain contract |

An insufficient evidence state MUST use `review`, `reject`, or `abstain`; it cannot
use `approve`.

## ValuationScenario

Represents inputs and auditable outputs for one bond valuation scenario.

- Currency and amounts use decimal strings.
- Yield is a decimal rate; spread values use integer basis points.
- Cash-flow dates MUST be strictly increasing and later than the valuation date.
- `assumptions` MUST contain at least one explicit assumption.
- Duration and convexity are non-negative analytical outputs.

## BenchmarkCase

Provides an interoperable benchmark exchange record. It intentionally contains a
small common subset and does not replace a benchmark's richer native schema.

- Evidence references use stable evidence IDs.
- Answerability and abstention MUST agree.
- Unanswerable cases MUST use a null gold answer and at least one reason.
- Splits are `train`, `dev`, or `test`.
- Synthetic status is explicit.

## ExperimentRecord

Captures reproducibility metadata and scoped results.

- Dataset, model, prompt, and retriever versions are explicit.
- Git commit is a full lowercase SHA-1 or SHA-256 hexadecimal identifier.
- The seed is a non-negative integer.
- Metrics have unique names and decimal-string values.
- Completion cannot precede start.
- Limitations MUST contain at least one non-empty statement.
- Environment metadata includes language/runtime, platform, and dependency-lock hash.
