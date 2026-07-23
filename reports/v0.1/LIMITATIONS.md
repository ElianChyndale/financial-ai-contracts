# Limitations

- Conformance is structural; it does not prove a model, score, valuation, or decision
  is correct.
- Currency validation checks a three-letter syntax, not the current ISO 4217 registry.
- Signatures are opaque bytes. Consumers must implement domain, signer, nonce, expiry,
  replay, and authorization checks.
- The Solidity mapping is a bounded ABI projection, not a deployed protocol.
- Decimal strings avoid binary-float disagreement but consumers still need explicit
  rounding and precision policies for calculations.
- The five golden records are synthetic interoperability fixtures, not research or
  market findings.
- Legacy migrations cover two documented examples and reject every unsupported path.
