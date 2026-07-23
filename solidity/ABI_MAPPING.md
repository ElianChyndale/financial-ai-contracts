# Solidity ABI Mapping

The Solidity representation is an explicit projection of `RiskAttestation`, not a
second source of truth.

| JSON field | Solidity field | Mapping |
| --- | --- | --- |
| `attestation_id` | `attestationIdHash` | SHA-256 of UTF-8 identifier |
| `asset_id` | `assetIdHash` | SHA-256 of UTF-8 identifier |
| `risk_score` | `riskScorePpm` | exact decimal ? 1,000,000 |
| `confidence` | `confidencePpm` | exact decimal ? 1,000,000 |
| `evidence_sufficiency` | enum | declared ordinal 0?2 |
| `recommended_haircut_bps` | `uint16` | unchanged |
| `model_version` | `string` | unchanged UTF-8 |
| `evidence_root` | `bytes32` | decoded hex |
| `evidence_ids` | `bytes32[]` | ordered SHA-256 identifier hashes |
| `issued_at`, `expires_at` | `uint64` | UTC Unix seconds |
| `decision_code` | enum | declared ordinal 0?3 |
| `provider` | `address` | unchanged |
| `signature` | `bytes` | decoded hex or empty bytes |
| `nonce`, `chain_id` | `uint256` | parsed canonical integers |
| `verifying_contract` | `address` | unchanged |

A real integration MUST independently authorize the provider address under its own
governance. Structural conformance does not establish that authorization.
