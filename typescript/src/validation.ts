import { Ajv2020, type ErrorObject } from "ajv/dist/2020.js";

import type {
  BenchmarkCase,
  Contract,
  ContractType,
  EvidenceUnit,
  ExperimentRecord,
  RiskAttestation,
  ValuationScenario,
} from "./types.js";

export interface ValidationIssue {
  layer: "schema" | "semantic";
  path: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  issues: ValidationIssue[];
}

function duplicate(values: string[]): boolean {
  return new Set(values).size !== values.length;
}

function evidenceIssues(record: EvidenceUnit): string[] {
  const issues: string[] = [];
  const box = record.bounding_box;
  if (box !== null && (box.x1 <= box.x0 || box.y1 <= box.y0)) {
    issues.push("bounding box must have positive width and height");
  }
  if (record.valid_time.end !== null) {
    if (Date.parse(record.valid_time.end) <= Date.parse(record.valid_time.start)) {
      issues.push("valid_time.end must be later than start");
    }
  }
  return issues;
}

function riskIssues(record: RiskAttestation): string[] {
  const issues: string[] = [];
  if ([record.risk_score, record.confidence].some((value) => (value.split(".")[1]?.length ?? 0) > 6)) {
    issues.push("probability supports at most six decimals");
  }
  if (Date.parse(record.expires_at) <= Date.parse(record.issued_at)) {
    issues.push("expires_at must be later than issued_at");
  }
  if (record.evidence_sufficiency === "insufficient" && record.decision_code === "approve") {
    issues.push("insufficient evidence cannot produce approve");
  }
  if (duplicate(record.evidence_ids)) {
    issues.push("evidence_ids must be unique");
  }
  const uintMax = (1n << 256n) - 1n;
  if (BigInt(record.nonce) > uintMax || BigInt(record.chain_id) > uintMax) {
    issues.push("value exceeds uint256");
  }
  return issues;
}

function valuationIssues(record: ValuationScenario): string[] {
  const dates = record.cash_flows.map((flow) => flow.payment_date);
  const sorted = [...dates].sort();
  if (dates.some((value, index) => value !== sorted[index]) || duplicate(dates)) {
    return ["cash flow dates must be strictly increasing"];
  }
  if (dates.some((value) => value <= record.valuation_date)) {
    return ["cash flows must occur after valuation_date"];
  }
  if (duplicate(record.assumptions)) {
    return ["assumptions must be unique"];
  }
  return [];
}

function benchmarkIssues(record: BenchmarkCase): string[] {
  const issues: string[] = [];
  if (record.answerable) {
    if (record.gold_answer === null) issues.push("answerable case requires gold_answer");
    if (record.abstention_expected) issues.push("answerable case cannot expect abstention");
    if (record.unanswerable_reasons.length > 0) {
      issues.push("answerable case cannot have unanswerable reasons");
    }
  } else {
    if (record.gold_answer !== null) issues.push("unanswerable case must have null gold_answer");
    if (!record.abstention_expected) issues.push("unanswerable case must expect abstention");
    if (record.unanswerable_reasons.length === 0) {
      issues.push("unanswerable case requires a reason");
    }
  }
  if (record.question_type === "unanswerable" && record.answerable) {
    issues.push("unanswerable question type cannot be answerable");
  }
  return issues;
}

function experimentIssues(record: ExperimentRecord): string[] {
  const issues: string[] = [];
  if (Date.parse(record.completed_at) < Date.parse(record.started_at)) {
    issues.push("completed_at cannot precede started_at");
  }
  if (duplicate(record.metrics.map((metric) => metric.name))) {
    issues.push("metric names must be unique");
  }
  if (duplicate(record.limitations)) issues.push("limitations must be unique");
  return issues;
}

function semanticIssues(contractType: ContractType, record: Contract): string[] {
  switch (contractType) {
    case "evidence-unit":
      return evidenceIssues(record as EvidenceUnit);
    case "risk-attestation":
      return riskIssues(record as RiskAttestation);
    case "valuation-scenario":
      return valuationIssues(record as ValuationScenario);
    case "benchmark-case":
      return benchmarkIssues(record as BenchmarkCase);
    case "experiment-record":
      return experimentIssues(record as ExperimentRecord);
  }
}

function schemaIssue(error: ErrorObject): ValidationIssue {
  return {
    layer: "schema",
    path: error.instancePath || "$",
    message: error.message ?? error.keyword,
  };
}

export function validateRecord(
  contractType: ContractType,
  record: unknown,
  schema: object,
): ValidationResult {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  ajv.addFormat("date", {
    type: "string",
    validate: (value: string) =>
      /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(`${value}T00:00:00Z`)),
  });
  ajv.addFormat("date-time", {
    type: "string",
    validate: (value: string) =>
      /(?:Z|[+-]\d{2}:\d{2})$/.test(value) && !Number.isNaN(Date.parse(value)),
  });
  const validator = ajv.compile(schema);
  if (!validator(record)) {
    return {
      valid: false,
      issues: (validator.errors ?? []).map(schemaIssue),
    };
  }
  const semantic = semanticIssues(contractType, record as Contract);
  return {
    valid: semantic.length === 0,
    issues: semantic.map((message) => ({ layer: "semantic", path: "$", message })),
  };
}
