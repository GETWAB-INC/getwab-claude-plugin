---
name: forecast-intelligence
description: Research agency acquisition forecasts and planned pipeline using GETWAB.
---

# forecast-intelligence

Read [shared workflow](../workflow.md) and [compatibility rules](../compatibility.md) before research. Use [field mappings](../mappings.json) for canonical interpretation.

Tools: search_acquisition_forecasts, search_opportunities, search_awards.
Detailed source semantics: [playbook](../playbooks/forecasting.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

Use source, agency, office, NAICS, PSC, set-aside, incumbent and estimated date filters as exposed. Source publishers are fco, apfs and hhs_sbcx. Record identity must include source + source_record_id.
A forecast is a planning signal that can change or never become a solicitation. Estimated values, solicitation date and award date are not actual obligations or confirmed deadlines. Preserve date precision and unknown timezone.
Distinguish reported incumbent_name from an identifier-confirmed incumbent. For follow-up current opportunity or historical award research, use returned identifiers; title/code similarity produces candidates.
Explain pipeline by timing, capability fit and uncertainty. Do not turn estimated value ranges into a guaranteed addressable market total.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
