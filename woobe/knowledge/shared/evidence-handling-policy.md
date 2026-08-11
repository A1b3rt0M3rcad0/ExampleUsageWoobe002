# Atlas Evidence Handling Policy

Status: controlled product Knowledge for the Atlas proof of value.

## Two information classes

1. Policy Knowledge
   - Lives in Woobe Collections.
   - Defines how Atlas evaluates.
   - Includes scoring, requirements and analyst methodology.

2. Assessment Evidence
   - Lives in Atlas.
   - Belongs to a specific assessment.
   - Includes uploaded vendor PDF/TXT/MD content and Atlas case metadata.
   - Is retrieved by Agents only through Atlas HTTP Tools.

These classes must never be conflated.

## Evidence rules

Every material vendor-specific finding must include:
- evidence_id;
- document_id;
- document_name;
- page_number when the source has pages;
- a short supporting quote copied from Tool output.

Do not invent evidence identifiers or page numbers.

A search with no result means only that the search did not retrieve evidence. It does not prove the opposite claim.

Use NOT_EVIDENCED when an applicable requirement cannot be substantiated.
Use NOT_APPLICABLE only when the assessment context makes the requirement irrelevant.

When evidence conflicts:
- preserve both evidence references;
- explain the conflict in unknowns;
- do not silently choose whichever text is more convenient.
