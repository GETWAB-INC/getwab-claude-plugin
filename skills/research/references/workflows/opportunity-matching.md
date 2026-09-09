---
name: opportunity-matching
description: Match a business profile supplied by text, dictation or documents to GETWAB federal opportunities.
---

# opportunity-matching

Read [shared workflow](../workflow.md) and [compatibility rules](../compatibility.md) before research. Use [field mappings](../mappings.json) for canonical interpretation.

Tools: match_opportunities, search_opportunities, search_awards.
Detailed source semantics: [playbook](../playbooks/sam_opportunities.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

Extract user-provided capabilities, past performance, NAICS/PSC, geography, certifications, clearances, size and constraints. Distinguish supplied facts from suggested codes and unverified credentials. Ask for material missing constraints only.
Call match_opportunities with company_profile, discriminating keywords, naics arrays and agencies when supplied. PSC is not a supported structured parameter here; assess returned scope and disclose the limitation.
The backend fallback keyword extraction is a frequency heuristic. Supply meaningful keywords yourself; do not assume it semantically matches a long capability statement. Do not assign fabricated match percentages.
For each candidate state fit, gaps, deadline, buyer and set-aside evidence, then a conditional pursue/monitor/pass suggestion. Award history supports experience research; it does not prove future eligibility or likelihood of winning.
If nothing matches, explain the exact attempted scope and propose a controlled relaxation. Clearly label relaxed results instead of presenting them as satisfying the original constraints.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
