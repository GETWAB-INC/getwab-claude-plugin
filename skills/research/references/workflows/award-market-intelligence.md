---
name: award-market-intelligence
description: Analyze FPDS spending, award history, agencies, vendors and NAICS/PSC markets using GETWAB.
---

# award-market-intelligence

Read [shared workflow](../workflow.md) and [compatibility rules](../compatibility.md) before research. Use [field mappings](../mappings.json) for canonical interpretation.

Tools: analyze_awards, search_awards, search_vendors.
Detailed source semantics: [playbook](../playbooks/fpds_awards.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

For spending, ranks, trends or competitors call analyze_awards with structured naics/psc arrays and group_by=market or the requested dimension. State the signed-date range and federal fiscal-year basis. Net obligations include negative modifications; never equate them to ceilings, outlays or total potential value.
search_awards is for contract records, not total market calculation. Its rows aggregate agency/PIID; do not call each row a transaction. Vendor rankings group by UEI; missing UEIs can collapse into an unidentified group, never present that as one company.
Rankings are limited by limit. total_groups is returned groups, not market population. Do not sum top-vendor rows to claim entire-market spending. If aggregation fails, say it is unavailable and offer a narrower supported query; do not interpret text-search zero as zero spending.
A returned awardee is evidence of winning that award, not universally the incumbent for a new solicitation. Explain exact contract evidence versus comparable contractor activity.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
