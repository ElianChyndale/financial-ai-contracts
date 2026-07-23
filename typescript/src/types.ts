export type SchemaVersion = "1.0.0";
export type Identifier = string;
export type DecimalString = string;
export type Bytes32 = `0x${string}`;
export type Address = `0x${string}`;
export type Timestamp = string;
export type DateString = string;

export interface TimeInterval {
  start: Timestamp;
  end: Timestamp | null;
}

export interface BoundingBox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface EvidenceUnit {
  schema_version: SchemaVersion;
  evidence_id: Identifier;
  document_id: Identifier;
  document_hash: Bytes32;
  page: number;
  section: string | null;
  text: string;
  bounding_box: BoundingBox | null;
  source_time: Timestamp;
  valid_time: TimeInterval;
  issuer_id: Identifier | null;
  bond_id: Identifier | null;
}

export type EvidenceSufficiency = "insufficient" | "partial" | "sufficient";
export type DecisionCode = "approve" | "review" | "reject" | "abstain";

export interface RiskAttestation {
  schema_version: SchemaVersion;
  attestation_id: Identifier;
  asset_id: Identifier;
  risk_score: DecimalString;
  confidence: DecimalString;
  evidence_sufficiency: EvidenceSufficiency;
  recommended_haircut_bps: number;
  model_version: string;
  evidence_root: Bytes32;
  evidence_ids: Identifier[];
  issued_at: Timestamp;
  expires_at: Timestamp;
  decision_code: DecisionCode;
  provider: Address;
  signature: string | null;
  nonce: string;
  chain_id: string;
  verifying_contract: Address;
}

export interface CashFlow {
  payment_date: DateString;
  amount: DecimalString;
}

export interface ValuationScenario {
  schema_version: SchemaVersion;
  scenario_id: Identifier;
  bond_id: Identifier;
  currency: string;
  valuation_date: DateString;
  face_value: DecimalString;
  base_yield: DecimalString;
  spread_adjustment_bps: number;
  cash_flows: CashFlow[];
  present_value: DecimalString;
  duration_years: DecimalString;
  convexity_years2: DecimalString;
  z_spread_bps: number;
  assumptions: string[];
}

export interface GoldAnswer {
  text: string;
  numeric_value: DecimalString | null;
  unit: "currency" | "percent" | "basis_points" | "ratio" | "years" | "text" | null;
  currency: string | null;
}

export interface BenchmarkCase {
  schema_version: SchemaVersion;
  case_id: Identifier;
  question: string;
  question_type:
    | "factual"
    | "comparison"
    | "temporal"
    | "numerical"
    | "conflict"
    | "unanswerable";
  answerable: boolean;
  gold_answer: GoldAnswer | null;
  document_ids: Identifier[];
  gold_evidence_ids: Identifier[];
  abstention_expected: boolean;
  unanswerable_reasons: string[];
  split: "train" | "dev" | "test";
  synthetic: boolean;
}

export interface MetricValue {
  name: Identifier;
  value: DecimalString;
  unit: string;
}

export interface EnvironmentInfo {
  runtime: string;
  platform: string;
  dependency_lock_hash: Bytes32;
}

export interface ExperimentRecord {
  schema_version: SchemaVersion;
  experiment_id: Identifier;
  dataset_version: string;
  model_version: string;
  prompt_version: string;
  retriever: string;
  seed: number;
  metrics: MetricValue[];
  commit: string;
  environment: EnvironmentInfo;
  started_at: Timestamp;
  completed_at: Timestamp;
  limitations: string[];
}

export type ContractType =
  | "benchmark-case"
  | "evidence-unit"
  | "experiment-record"
  | "risk-attestation"
  | "valuation-scenario";

export type Contract =
  | BenchmarkCase
  | EvidenceUnit
  | ExperimentRecord
  | RiskAttestation
  | ValuationScenario;

