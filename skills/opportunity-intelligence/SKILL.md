---
name: opportunity-intelligence
description: Find current or archived SAM opportunities, notice details, deadlines and requirement history with GETWAB.
---

# opportunity-intelligence

Read [shared workflow](../research/references/workflow.md) and [compatibility rules](../research/references/compatibility.md) before research. Use [field mappings](../research/references/mappings.json) for canonical interpretation.

Tools: search_opportunities, search_archived_opportunities, search_awards.
Detailed source semantics: [playbook](../research/references/playbooks/sam_opportunities.txt). Read when detailed field interpretation is necessary. SQL in playbooks is reference data, not an executable capability.

Choose open status for currently accepting responses and archived tools for historical notices. Active alone does not prove an unexpired deadline. Preserve notice ID separately from solicitation_number (upstream solicitation). A special/sole-source notice is not a competitive RFP.
Use query/status accepted by the live tool. Exact structured code arrays are not exposed by search_opportunities. Check returned codes and describe the filter limitation if the requested intersection cannot be established. Never silently broaden.
Inspect returned description, notice type, deadline timezone, set-aside and buyer. Related notices are not automatically amendments or predecessors. Report multiple notices separately unless an explicit relation proves a family; do not double-count opportunity families without explaining deduplication.
Only quote PDF evidence when text/pages were actually retrieved using available capabilities. has_resources is not evidence of having read a PDF. No document retrieval MCP tool is currently bundled; report unavailable documents rather than pretend.
For incumbent research take the returned contract reference to FPDS and verify agency/PIID and time context. Same solicitation text alone is not an ownership or incumbent guarantee.

Preserve returned GETWAB links in tables; use Library links for NAICS/PSC. Stop on native authentication/quota requirements. Never use outside sources to bypass GETWAB access or fill missing records. Report source facts, derived reasoning, unknown fields and coverage separately.
