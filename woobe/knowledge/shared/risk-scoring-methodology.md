# Atlas Demo Risk Scoring Methodology

Status: controlled product Knowledge for the Atlas proof of value. This is a fictitious internal scoring policy, not an industry standard.

## Direction

Risk scores use 0–100:
- 0 = lowest observable risk.
- 100 = highest observable risk.

## Domain weights

Default overall weighting:
- SECURITY: 40%
- LEGAL: 35%
- COMPLIANCE: 25%

If a domain is not required by the assessment, remove it and renormalize the remaining weights proportionally.

The final overall score is the weighted mean of the required domain scores, rounded to the nearest integer.

## Recommendation thresholds

- 0–24: APPROVE
- 25–49: APPROVE_WITH_CONDITIONS
- 50–74: MANUAL_REVIEW
- 75–100: REJECT

Critical override:
- Any substantiated CRITICAL finding forces REJECT.
- A NOT_EVIDENCED requirement is not automatically CRITICAL.

## Finding severity

- CRITICAL: creates unacceptable exposure under this demo policy and blocks approval.
- HIGH: material exposure requiring remediation or explicit risk acceptance.
- MEDIUM: meaningful weakness that should be contractually or operationally addressed.
- LOW: limited exposure or improvement opportunity.
- INFO: observation without direct risk increment.

## Evidence discipline

A vendor-specific factual claim is substantiated only when it carries an Atlas evidence reference returned by the Atlas Tool API.
Knowledge documents define criteria. They never prove that a vendor satisfies a criterion.
