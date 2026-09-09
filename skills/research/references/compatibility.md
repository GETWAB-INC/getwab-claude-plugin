# Canon v1.0.0 compatibility decisions

These are existing upstream limitations, not promises to fix or deploy them here.

- search_awards returns grouped agency/PIID summaries, not individual FPDS transactions.
  analyze_awards returns groups, search_vendors returns vendor aggregates. These outputs
  retain source_record and record_granularity; their transaction record_type is null
  because Canon v1.0.0 defines no aggregate record type. Do not manufacture a transaction.
- research_vendor reports complete when its sources answer, even when each group is limited.
  Local normalization treats groups without pagination/completeness metadata as partial.
- analyze_awards total_groups counts returned groups after LIMIT, not total market groups.
  Treat rankings as limited unless independent completeness evidence exists.
- search_subcontracts and search_archived_opportunities advertise dates, but controller
  search methods do not apply them. The input adapter rejects those date filters.
- search_opportunities accepts query/status, not structured NAICS/PSC arrays. Compose an
  explicit query for the existing parser only when appropriate, inspect actual results,
  and disclose that exact structured filtering is unavailable in that tool schema.
- SUBNet accepts a PSC relevance request but does not filter a source PSC column.
- Monetary totals, fiscal years, booleans, roles and source identifiers remain distinct.
- Missing IDs are reported as null plus a warning; no fabricated stable ID.
- Source-updated timestamps are not the same as loaded_at, fetched_at or scraped_at.
- Forecast identity is source + source_record_id; the local record_id is a JSON tuple
  to prevent two forecast publishers with the same ID from colliding.
- Existing Markdown values are preserved in source_record. Parsing their label for local
  canonical interpretation does not alter the server or current ChatGPT output.
- Logging, billing, OAuth implementation and public metadata are outside this package's
  Canon field adapter. Actual client authentication still requires acceptance testing.
