# Atlas Security Assessment Methodology

Evaluate SEC-01 through SEC-06 when applicable.

## Requirement risk points

For scoring:
- PASS: 0 points
- NOT_APPLICABLE: excluded
- NOT_EVIDENCED: 55 points
- FAIL with LOW severity: 25 points
- FAIL with MEDIUM severity: 45 points
- FAIL with HIGH severity: 75 points
- FAIL with CRITICAL severity: 100 points

Domain risk score = arithmetic mean of applicable requirement points, rounded to nearest integer.

Search narrowly. Prefer queries containing the concrete control:
- "encryption at rest TLS"
- "administrator MFA privileged access"
- "critical vulnerability remediation days"
- "security incident notification hours"
- "RTO disaster recovery annual test"
- "SOC 2 Type II ISO 27001 valid"

Do not score a PASS from marketing language such as "enterprise-grade security" without control-level evidence.
