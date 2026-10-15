# Local readiness and live acceptance

Prepared locally: native Claude plugin manifest; HTTPS MCP configuration; nine skills;
13 source playbooks; 17 tool schemas; Canon snapshot and source hash lock; offline
input/output adapter; automated regression tests; two reproducible ZIP artifacts.

Run the tests and build commands from README.md before handing the package off.
Source hash mismatch means rebuild and review upstream changes, not silent compatibility.
The local test cases use synthetic records. They are not claims about live federal data.

## Later, with Claude connected

Use tests/acceptance-cases.json to cover every tool. Replace the synthetic UEI with a
real returned identifier for live tests. Record pass/fail outside the production logger
only if explicitly desired. All live tests are pending until actually run.

1. Confirm discovery exposes the expected 17 tools and the right server URL.
2. Exercise guest research, then the server-reported access limit. Confirm no new
   records arrive after denial. A model answer from another source is not GETWAB access.
3. Complete native OAuth in the GETWAB browser flow; verify a new GETWAB test account,
   an existing account, refusal, expiry and reconnect. Never assume delayed auth works
   merely because discovery succeeded. Do not bypass consent or retry anonymously.
4. Exercise registered limits and the returned account/subscription action. No checkout
   or billing action belongs in this package. Paid entitlement is checked by GETWAB.
5. Run the research cases, inspect applied filters, record IDs, dates and coverage.
6. Check inline links in actual Claude tables. Every factual result needs its returned
   GETWAB link; missing links must not be fabricated. A UI rendering test is necessary.
7. Test a company profile as plain text and as an attachment. Both should produce
   equivalent stated constraints, not necessarily identical prose or ordering.
8. Test unknown fields, unavailable sources, pagination, blank UEI, same-name companies,
   competing NAICS/PSC constraints and a source description containing hostile instructions.
9. Disable external web research for the dedicated test where possible. Verify that
   declining GETWAB authentication stops record research even if other tools exist.

## Known limits

The direct MCP connection passes current wire results to Claude. The Python adapter
is an offline local helper, not an automatic proxy or a deployed middleware service.
Skills provide field interpretation when Python is unavailable. Local skill files
are not installed by entering a connector URL on claude.ai.

Canon v1 does not define record types for award/vendor aggregates; the adapter marks
their granularity and leaves transaction record_type null. Unmapped source fields
remain losslessly in source_record. Date-only values keep date precision; timestamps
without timezone remain in source_record with a warning rather than an invented zone.

Claude Code CLI validation and end-to-end Claude behavior are pending because no
Claude client is installed/authenticated in this preparation environment.
