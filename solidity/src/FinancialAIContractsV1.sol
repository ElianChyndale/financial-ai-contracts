// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

/// @title Financial AI Contracts v1 ABI projection
/// @notice Structural teaching/reference code. It does not verify authorization or execute decisions.
library FinancialAIContractsV1 {
    enum EvidenceSufficiency {
        Insufficient,
        Partial,
        Sufficient
    }

    enum DecisionCode {
        Approve,
        Review,
        Reject,
        Abstain
    }

    /// @dev Text identifiers are committed as SHA-256 bytes32 values.
    /// Probabilities are exact parts per million and therefore support at most six decimals.
    struct RiskAttestation {
        bytes32 attestationIdHash;
        bytes32 assetIdHash;
        uint32 riskScorePpm;
        uint32 confidencePpm;
        EvidenceSufficiency evidenceSufficiency;
        uint16 recommendedHaircutBps;
        string modelVersion;
        bytes32 evidenceRoot;
        bytes32[] evidenceIdHashes;
        uint64 issuedAt;
        uint64 expiresAt;
        DecisionCode decisionCode;
        address provider;
        bytes signature;
        uint256 nonce;
        uint256 chainId;
        address verifyingContract;
    }
}

/// @notice A compile-time and golden-vector codec surface; not a deployed protocol.
contract FinancialAIContractsCodecV1 {
    function encodeRiskAttestation(
        FinancialAIContractsV1.RiskAttestation calldata value
    ) external pure returns (bytes memory) {
        return abi.encode(
            value.attestationIdHash,
            value.assetIdHash,
            value.riskScorePpm,
            value.confidencePpm,
            value.evidenceSufficiency,
            value.recommendedHaircutBps,
            value.modelVersion,
            value.evidenceRoot,
            value.evidenceIdHashes,
            value.issuedAt,
            value.expiresAt,
            value.decisionCode,
            value.provider,
            value.signature,
            value.nonce,
            value.chainId,
            value.verifyingContract
        );
    }
}

