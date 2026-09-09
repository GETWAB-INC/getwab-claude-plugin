---
name: gsa-intelligence
description: Research GSA eLibrary contracts, schedules, SIN categories and contractor registrations.
---

# gsa-intelligence

Read [shared workflow](../research/references/workflow.md) and [compatibility rules](../research/references/compatibility.md) before research. Use [field mappings](../research/references/mappings.json) for canonical interpretation.

Tools: search_gsa_contracts, search_entities, analyze_awards.
Detailed source semantics: [playbook](../research/references/playbooks/gsa_contracts.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

Use query, vendor, uei, contract, category, availability and designation per live schema. category may be SIN such as 54151S; it is not a NAICS code. Preserve large_category/sub_category as source taxonomy rather than forcing them into NAICS.
Open availability means the vehicle's reported new-award availability, not an open solicitation. closed_for_new_award and option/ultimate end dates have distinct meanings.
Use returned UEI for exact SAM entity follow-up. Multiple contracts or SIN rows may represent one entity; deduplicate only with declared identity keys. Do not collapse all Leidos-named entities into one.
A schedule contract proves directory/vehicle context, not sales volume. Use FPDS analysis separately for spending with supported identifiers and explicit counting rules.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
