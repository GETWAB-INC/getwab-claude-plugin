---
name: vendor-due-diligence
description: Research SAM entities, vendor history and official exclusions with exact identifiers and evidence.
---

# vendor-due-diligence

Read [shared workflow](../research/references/workflow.md) and [compatibility rules](../research/references/compatibility.md) before research. Use [field mappings](../research/references/mappings.json) for canonical interpretation.

Tools: search_entities, search_vendors, research_vendor, search_exclusions.
Detailed source semantics: [playbook](../research/references/playbooks/sam_entities.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

Start with UEI/CAGE when supplied; otherwise use legal_name_or_dba for discovery. Keep identical names with different UEIs as distinct registrations. A UEI identifies a registration and does not prove parent ownership.
For all-entity requests paginate search_entities; research_vendor is a small multi-source preview with no group pagination. Do not call it exhaustive. Include UEI, CAGE, SAM status and location only when returned.
Check exclusions using exact UEI/CAGE plus source lifecycle. A name-only exclusion match is a candidate requiring identity verification. Preserve the official classification and reason; never add an inferred offense.
Separate SAM registration status, UEI assigned status, expiry and exclusion lifecycle. An inactive SAM entity is not automatically excluded. A no-match exclusion search means no matching returned record within the searched scope, not a guarantee.
Show which stable ID joins each vendor/award/entity result and which relationships remain name candidates. Keep acquisitions, subsidiaries and joint ventures unconfirmed absent explicit evidence.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
