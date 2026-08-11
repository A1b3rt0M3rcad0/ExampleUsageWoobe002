# Atlas Demo Security Requirements

These requirements are fictitious Atlas internal demo policy.

## SEC-01 — Encryption

For HIGH or CRITICAL vendors handling PII or financial data, evidence must state:
- encryption in transit using a modern TLS configuration; and
- encryption at rest for customer data.

Missing either element is NOT_EVIDENCED. Explicit absence is FAIL/HIGH.

## SEC-02 — Privileged access

Privileged/administrative access must require MFA.
Explicit lack of MFA is FAIL/CRITICAL for CRITICAL vendors and FAIL/HIGH otherwise.

## SEC-03 — Vulnerability remediation

The vendor must evidence a vulnerability-management process.
Critical vulnerabilities must have a target remediation time of 30 calendar days or less.
A longer explicit target is FAIL/HIGH.

## SEC-04 — Incident notification

For vendors handling PII, the documented customer security-incident notification target must be 24 hours or less after confirmed impact requiring notification under the vendor agreement/policy.
A longer explicit commitment is FAIL/HIGH.

## SEC-05 — Business continuity

For HIGH or CRITICAL vendors:
- target RTO must be 4 hours or less;
- continuity/disaster-recovery testing must occur at least annually.

Explicit RTO above 4 hours is FAIL/HIGH.

## SEC-06 — Independent assurance

HIGH or CRITICAL vendors should provide evidence of a current independent security assurance such as SOC 2 Type II or ISO/IEC 27001 certification.
The Agent must not infer validity dates that are not present in assessment evidence.
Missing assurance is NOT_EVIDENCED/MEDIUM.
