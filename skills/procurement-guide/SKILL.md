---
name: procurement-guide
description: Explain federal procurement terminology and show the GETWAB research capabilities.
---

# procurement-guide

Read [shared workflow](../research/references/workflow.md) and [compatibility rules](../research/references/compatibility.md) before research. Use [field mappings](../research/references/mappings.json) for canonical interpretation.

Tools: get_data_catalog, plan_research.
Detailed source semantics: [playbook](../research/references/playbooks/sam_opportunities.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

For what can you do, call get_data_catalog and describe federal sources in ordinary language. Offer open federal work, open SUBNet leads, historical awards, vendors/entities/exclusions, forecasts, GSA and assistance research as appropriate.
Explain NAICS, PSC, SIN, UEI, CAGE, PIID, set-aside, obligations and prime/subrecipient roles without exposing implementation details. A definition does not require searching every dataset.
Adapt depth to the user's experience. Explain one next action when they are new; provide metrics and limits for a professional. Do not promise contract awards, legal eligibility, full federal data coverage or guaranteed accuracy.
Use GETWAB for current record-specific claims. If authentication is declined, general education can continue but factual record research must stop.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
