import { AbiCoder, sha256, toUtf8Bytes } from "ethers";

import type { RiskAttestation } from "./types.js";

export const riskAttestationAbiTypes = [
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
] as const;

const sufficiencyCodes = {
  insufficient: 0,
  partial: 1,
  sufficient: 2,
} as const;

const decisionCodes = {
  approve: 0,
  review: 1,
  reject: 2,
  abstain: 3,
} as const;

function probabilityPpm(value: string): number {
  const [whole, fraction = ""] = value.split(".");
  if (whole === undefined || fraction.length > 6) {
    throw new Error("Solidity projection supports at most six probability decimals");
  }
  const padded = fraction.padEnd(6, "0");
  return Number(BigInt(whole) * 1_000_000n + BigInt(padded || "0"));
}

function unixSeconds(value: string): bigint {
  const millis = Date.parse(value);
  if (!Number.isFinite(millis) || millis % 1000 !== 0) {
    throw new Error(`timestamp is not an exact second: ${value}`);
  }
  return BigInt(millis / 1000);
}

export function riskAttestationAbiValues(record: RiskAttestation): unknown[] {
  return [
    sha256(toUtf8Bytes(record.attestation_id)),
    sha256(toUtf8Bytes(record.asset_id)),
    probabilityPpm(record.risk_score),
    probabilityPpm(record.confidence),
    sufficiencyCodes[record.evidence_sufficiency],
    record.recommended_haircut_bps,
    record.model_version,
    record.evidence_root,
    record.evidence_ids.map((value) => sha256(toUtf8Bytes(value))),
    unixSeconds(record.issued_at),
    unixSeconds(record.expires_at),
    decisionCodes[record.decision_code],
    record.provider,
    record.signature ?? "0x",
    BigInt(record.nonce),
    BigInt(record.chain_id),
    record.verifying_contract,
  ];
}

export function encodeRiskAttestation(record: RiskAttestation): string {
  return AbiCoder.defaultAbiCoder().encode(
    [...riskAttestationAbiTypes],
    riskAttestationAbiValues(record),
  );
}

