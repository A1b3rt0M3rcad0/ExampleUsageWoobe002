# Atlas Evaluation Plan

This is the minimum evaluation material for the PoV once the Woobe Evaluator pipeline is available.

Evaluate a candidate Agent/Network release against deterministic Atlas fixtures. Do not use live customer assessments as the first test dataset.

## Core metrics

1. Structured output validity — target 100%.
2. Evidence integrity — every material vendor claim has a valid Atlas evidence_id.
3. Fabricated evidence rate — target 0%.
4. Critical requirement recall — compare against curated expected requirement outcomes.
5. False positive rate.
6. Domain risk-score agreement with fixture expectation.
7. Network success rate.
8. Agent Runs per Network Run.
9. Median/P95 latency.
10. Cost per completed assessment.

## Blocking rules

Candidate is not qualified when:
- fabricated evidence rate > 0%;
- structured output validity < 100% on the critical suite;
- critical requirement recall regresses versus production;
- a CRITICAL expected finding is missed;
- production policy Knowledge is not the snapshot under test.

## Fixture principle

Atlas Tool endpoints should be backed by fixed demo assessment documents so candidate and production releases receive the same external evidence. Comparison then isolates AI product changes rather than changing case data.
