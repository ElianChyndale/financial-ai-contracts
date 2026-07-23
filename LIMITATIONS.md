# Limitations

- Structural conformance does not prove that a model, risk score, valuation,
  recommendation, or decision is correct.
- The repository does not implement regulatory rules or determine whether a record is
  legally sufficient in any jurisdiction.
- Currency validation checks uppercase three-letter syntax, not a live ISO registry.
- Signature bytes are opaque. The package does not recover signers or enforce domain,
  nonce, expiry, replay, chain, contract, or authorization policy.
- The Solidity code is a compile-tested ABI reference, not a deployed or audited
  protocol.
- Decimal strings avoid cross-language binary-float differences, but calculation
  precision and rounding remain consumer responsibilities.
- `BenchmarkCase` is a portable common subset and does not replace richer benchmark
  schemas.
- Only two illustrative legacy migrations exist in v0.1.
- Golden vectors are small, deterministic, and synthetic. They are not real financial
  data or research findings.

