---
name: subcontract-intelligence
description: Find SBA SUBNet leads, subcontracting plans, historical contract subawards or assistance subawards.
---

# subcontract-intelligence

Read [shared workflow](../research/references/workflow.md) and [compatibility rules](../research/references/compatibility.md) before research. Use [field mappings](../research/references/mappings.json) for canonical interpretation.

Tools: search_subnet_opportunities, search_subcontracting_plans, search_subcontracts, search_assistance_subawards.
Detailed source semantics: [playbook](../research/references/playbooks/sba_subnet.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

Open subcontracting demand routes first to SUBNet. Use structured NAICS as one string. PSC is a relevance request, never an exact SUBNet source filter. response_deadline may be date-only; never invent a time.
On unavailable or empty direct results inspect fallback_evidence. Show historical contract subawards, plan-directory primes and open federal opportunities in distinct sections with their own coverage. The current nested fallbacks lack full availability metadata; an empty list alone cannot prove no source activity.
SBA subcontracting-plan rows may repeat a prime across fiscal years or contracts. Directory presence is not current demand or available money. potentially_ongoing describes date-based possibility only.
Contract subawards are reported procurement activity. Assistance subawards are grant/cooperative-agreement flows and never procurement spend. Keep prime/subcontractor/subrecipient roles and amounts distinct.
search_subcontracts advertises date fields that its current controller ignores: do not claim date-filtered results. Request a supported scope or clearly state that the requested date constraint cannot be guaranteed.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
