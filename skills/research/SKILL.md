---
name: research
description: Research U.S. federal procurement with GETWAB, including open opportunities, FPDS markets, SAM entities, exclusions, subcontracting, forecasts, GSA contracts and company capability matching.
---

# GETWAB Federal Procurement AI

Use this skill for GETWAB procurement requests from beginners, analysts and capture managers.
Accept text, dictation or user-supplied documents; PDF is not required.
Respond in the user's language and lead with the useful finding.

Before the first research call read [workflow](references/workflow.md).
For field interpretation read [mappings](references/mappings.json) and
[compatibility](references/compatibility.md). The [Canon](references/canon.md)
defines semantics; live tools/list defines callable parameters. Canon names
must be translated to upstream parameters, never sent blindly.

Use the GETWAB server from the installed MCP configuration. Claude prefixes tool
names by installation; select the discovered tool by its terminal name, such as
search_entities. Never guess a different server or claim a tool was called.

For a focused task load its specialist workflow from the installed plugin.
The standalone skill ZIP includes the specialist workflows in references/workflows.
Read only the relevant workflow and playbook, not all 13 playbooks each time.
Playbooks describe database semantics; they do not grant direct SQL execution.
Only execute capabilities exposed by the GETWAB MCP tools.

For supported filesystem execution, normalize a saved MCP JSON response with
`python3 scripts/adapter.py result TOOL_NAME INPUT.json` from this skill directory.
Use the canonical values for comparison, source_record/display_links for exact
returned links, and report warnings. The adapter operates offline and never
authenticates or calls GETWAB. If Python/files are unavailable, apply the same
mapping manually, disclose ambiguity, and do not claim executable normalization.

Never promise identical prose across AI models. Preserve equivalent filters,
dataset semantics, evidence, coverage and calculation units.

## Specialist workflows

- [FPDS and markets](references/workflows/award-market-intelligence.md)
- [Current and archived opportunities](references/workflows/opportunity-intelligence.md)
- [Company capability matching](references/workflows/opportunity-matching.md)
- [Entities, vendors and exclusions](references/workflows/vendor-due-diligence.md)
- [SUBNet, plans, contract and assistance subawards](references/workflows/subcontract-intelligence.md)
- [Acquisition forecasts](references/workflows/forecast-intelligence.md)
- [GSA contracts and SIN](references/workflows/gsa-intelligence.md)
- [Terminology and capability guidance](references/workflows/procurement-guide.md)
