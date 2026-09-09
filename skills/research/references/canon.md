# GETWAB Federal Procurement AI Canon

**Version:** 1.0.0
**Status:** baseline specification
**Scope:** all GETWAB AI integrations: ChatGPT, Claude, Gemini, Grok, and future clients.

## 1. Authority and purpose

This document is the single semantic contract for GETWAB Federal Procurement AI. It defines what each dataset means, the canonical names for fields and filters, and the functional rules used to answer research requests.

An AI client may have its own transport, OAuth flow, UI, skill format, or tool format. It may not rename a business concept, merge distinct record types, or reinterpret a source record. Platform adapters translate this Canon into the client-specific schema.

This Canon does **not** change the currently submitted ChatGPT plugin. It is a stable reference for future work and for a later, controlled migration of existing tools.

## 2. Non-negotiable principles

1. **One concept, one canonical name.** A concept must not acquire a second name in another dataset or AI adapter.
2. **A record type is never inferred from a similar name.** An open subcontracting lead, awarded contract subaward, subcontracting-plan directory row, assistance subaward, opportunity, forecast, and FPDS award are different record types.
3. **Stable identifiers outrank names.** UEI, CAGE, PIID, Notice ID, FAIN, record key, and source-specific IDs are evidence; a name is a search term unless a returned record establishes the relation.
4. **No false completeness.** A response can say “all” only when pagination is exhausted and `coverage_status` is `complete`.
5. **No false zero.** `unavailable`, `unsupported`, or `partial` data is not evidence of zero matches.
6. **Facts and interpretation remain separate.** Source fields are facts. Capture advice, matching rationale, and market interpretation are derived analysis.
7. **The Canon precedes adapters.** A new Claude/Gemini/Grok integration starts from this document, not from copied ChatGPT prompt text.

## 3. Canonical dataset registry

| `dataset_id` | Human name | Canonical `record_type` | What it is | What it is not |
|---|---|---|---|---|
| `fpds_awards` | FPDS historical awards | `contract_award_transaction` | Historical procurement award and transaction activity | An open opportunity or a market forecast |
| `sam_opportunities` | SAM.gov opportunities | `contract_opportunity_notice` | Current procurement notice, solicitation, special notice, or related notice | An awarded contract by itself |
| `sam_opportunities_archive` | Archived opportunities | `archived_contract_opportunity_notice` | Historical/archived opportunity record | A currently open notice |
| `sam_entities` | SAM.gov entities | `sam_entity_registration` | A SAM entity registration | Proof of a parent, subsidiary, division, or ownership relationship |
| `sam_exclusions` | SAM.gov exclusions | `sam_exclusion_record` | An official exclusion record published in SAM.gov | An independent legal conclusion beyond the record |
| `sam_contract_subawards` | Contract subawards | `contract_subaward` | A reported, awarded procurement subcontract | An open subcontracting opportunity |
| `sba_subnet_opportunities` | SBA SUBNet opportunities | `open_subcontracting_lead` | A prime contractor’s current subcontracting demand | An awarded subcontract or a federal prime opportunity |
| `sba_subcontracting_plans` | SBA subcontracting plans | `subcontracting_plan_directory_record` | A directory record associated with a prime and subcontracting plan | A promise of available work or paid subcontract spend |
| `sam_assistance_subawards` | Assistance subawards | `assistance_subaward` | A reported grant/cooperative-agreement flow-down | A procurement contract subcontract or open solicitation |
| `gsa_elibrary_contracts` | GSA eLibrary contracts | `gsa_schedule_contract` | GSA schedule/vehicle contract context | FPDS spending or an open opportunity |
| `acquisition_forecasts` | Acquisition forecasts | `acquisition_forecast` | Agency planning signal for a potential procurement | A guaranteed forthcoming solicitation |

`dataset_id` and `record_type` are mandatory in every normalized record and must never be overloaded.

## 4. Canonical record envelope

Every adapter eventually normalizes source data to this logical shape. A platform may omit a field only when the source does not supply it.

```text
record = {
  dataset_id,
  record_type,
  record_id,
  source_record_id,
  source_name,
  source_updated_at,
  title,
  status,
  identifiers,
  organizations,
  agencies,
  classifications,
  dates,
  financials,
  locations,
  acquisition,
  evidence
}
```

### 4.1 Record identity

| Canonical field | Meaning | Rules |
|---|---|---|
| `record_id` | GETWAB’s stable identifier for one normalized record | Required; string; not a display label |
| `source_record_id` | Stable identifier from the original source | Required when supplied by source; may equal `record_id` only when GETWAB uses the source ID directly |
| `source_name` | Source system name | One of `FPDS`, `SAM.gov`, `SBA SUBNet`, `SBA subcontracting plans`, `GSA eLibrary`, or an approved forecast source |
| `source_updated_at` | Latest source record update | ISO 8601 timestamp when known |
| `title` | Human-readable record title | Never used as an identifier |
| `status` | Record-type-specific controlled value | Never replace a source status with a guessed lifecycle |

### 4.2 Identifiers

```text
identifiers = {
  uei,
  cage,
  piid,
  solicitation_number,
  notice_id,
  fain,
  award_number,
  subaward_number,
  gsa_contract_number
}
```

Rules:

- `uei`: uppercase 12-character UEI when present.
- `cage`: uppercase 5-character CAGE code when present.
- `piid`, `solicitation_number`, `award_number`, `subaward_number`, `fain`, and `gsa_contract_number` retain source formatting; normalized search forms may be stored separately but must not replace the source value.
- `notice_id` is the SAM notice identifier, not a solicitation number.
- The fields `entity_id`, `record_key`, `award_key`, and `opportunity_id` are GETWAB/source implementation keys. They map to `record_id` or `source_record_id`; they are not interchangeable business identifiers.

### 4.3 Organizations

```text
organizations = {
  subject,
  vendor,
  awardee,
  prime,
  subcontractor,
  subrecipient,
  incumbent,
  ultimate_parent
}

organization = {
  legal_name,
  dba_name,
  uei,
  cage,
  relationship_type,
  relationship_evidence
}
```

Use the role that the source actually supplies. For example, `prime` and `subcontractor` belong to a contract subaward; `subrecipient` belongs to an assistance subaward. Do not replace them with generic `vendor`.

`relationship_type` may be `source_role`, `identifier_confirmed`, `explicit_source_statement`, `name_match_candidate`, or `unknown`. A name-only search result must never be labeled a subsidiary, division, affiliate, incumbent, or parent without record-level evidence.

### 4.4 Agencies and offices

```text
agencies = {
  department: { code, name },
  agency: { code, name },
  office: { code, name }
}
```

- `department` is not an `agency`; `agency` is not an `office`.
- Preserve supplied codes (`cgac`, agency code, office code, AAC, FPDS code) in adapter-specific source detail. Do not substitute a code when it was not returned.

### 4.5 Classifications

```text
classifications = {
  naics: [{ code, description, role }],
  psc: [{ code, description, role }],
  gsa_sin: [{ code, description }],
  set_aside: { code, name },
  business_designations: []
}
```

- `naics` and `psc` are arrays, even when one code exists.
- `role` is one of `primary`, `principal`, `secondary`, `reported`, or `unknown`.
- A GSA `category`/SIN is **not** NAICS. It belongs in `gsa_sin`.
- Do not transform a NAICS or PSC code into a description-only value; preserve both when supplied.

### 4.6 Dates

All canonical timestamps use ISO 8601. A source display string may be preserved in `evidence.source_value`.

```text
dates = {
  posted_at,
  response_deadline_at,
  archive_at,
  award_at,
  action_at,
  performance_start_at,
  performance_end_at,
  solicitation_estimated_at,
  award_estimated_at,
  fiscal_year
}
```

- `response_deadline_at` is the only canonical deadline field.
- `posted_at` is the notice/listing publication timestamp.
- Forecast dates are estimates and must use `solicitation_estimated_at` / `award_estimated_at`, never the same fields as confirmed award dates.
- `fiscal_year` is an integer U.S. federal fiscal year, not a calendar-year label.

### 4.7 Financial values

```text
financials = {
  currency,
  obligated_amount,
  award_amount,
  subaward_amount,
  total_contract_value,
  estimated_value_min,
  estimated_value_max,
  projected_obligation,
  amount_plausibility
}
```

- Amounts are numeric, never formatted currency strings.
- `obligated_amount` is the FPDS transaction amount and can be negative because of deobligations.
- `award_amount` is not interchangeable with `obligated_amount`.
- `subaward_amount` and assistance amounts must never be rolled into FPDS obligations without an explicitly defined analytical calculation.
- Forecast estimates remain estimates; they are not obligations or awards.

### 4.8 Locations

```text
locations = {
  entity: { address, city, state, postal_code, country },
  place_of_performance: { address, city, state, postal_code, country },
  office: { city, state, postal_code, country }
}
```

State and country codes are uppercase when a code is available. The source name may be retained separately.

## 5. Canonical search input vocabulary

All adapters accept this semantic vocabulary, even if a platform exposes a friendlier prompt.

| Canonical filter | Meaning | Do not confuse with |
|---|---|---|
| `query` | Free-text search phrase | A verified identifier |
| `naics_codes` | One or more NAICS codes | GSA SIN/category |
| `psc_codes` | One or more PSC codes | Free-text product description |
| `uei` | One or more exact UEIs | Vendor-name search |
| `cage` | One or more exact CAGE codes | Generic entity ID |
| `agency` | Agency code or source-supported name filter | Department or office unless explicitly requested |
| `office` | Contracting/issuing office | Agency |
| `state` | State/territory code or source-supported state filter | Place of performance unless requested |
| `date_from`, `date_to` | Inclusive source-query date range | Fiscal year |
| `status` | Dataset-specific lifecycle filter | Availability or record type |
| `page`, `page_size` | Pagination controls | Search limit or total count |

The following are intentionally dataset-specific and must stay explicit: `availability` (GSA), `match_mode` (SAM entities), `group_by` (FPDS analysis), `set_aside`, `incumbent`, `fiscal_year`, `source`, `solicitation_from`, `award_from`, and `designation`.

## 6. Functional routing rules

| User intent | Primary dataset/tool class | Required distinction |
|---|---|---|
| Find open federal work | Current SAM opportunities | Do not substitute historical awards |
| Research prior requirement language | Archived opportunities | Do not call archived notices current opportunities |
| Find open subcontracting work | SBA SUBNet opportunities | If no result/unavailable, label historical subawards, plans, and federal opportunities as separate fallback evidence |
| See awarded subcontract activity | Contract subawards | Do not call it a current opening |
| Find prime subcontracting-plan context | SBA subcontracting plans | Do not call it available subcontracting work |
| Market size, spend, vendors, trends | FPDS aggregation | Use structured aggregation, not text-search zero results |
| Find a contractor/entity | SAM entities and/or vendor history | Name matches do not establish corporate-family relationships |
| Check exclusion | SAM exclusions | Report official source classification; do not invent the legal reason |
| Search acquisition pipeline | Acquisition forecasts | Present as planning signals, not promises |
| GSA vehicle research | GSA eLibrary contracts | Keep GSA SIN separate from NAICS and FPDS obligations |
| Assistance flows | Assistance subawards | Keep separate from procurement subawards |

For multi-part questions, the adapter creates a research plan with named datasets and returns source-separated findings before any combined conclusion.

## 7. Coverage, evidence, and result rules

Every result set must expose:

```text
coverage = {
  status: complete | partial | unavailable | unsupported,
  total_matches,
  returned_records,
  page,
  page_size,
  next_page
}
```

- `complete`: the source query completed and no additional page exists.
- `partial`: another page exists, a source is stale, or only part of a multi-source workflow completed.
- `unavailable`: the source query failed or cannot be reached. This never means zero.
- `unsupported`: the requested filter, join, or calculation is not supported by that dataset.

An answer claiming “all entities,” “all awards,” or “no matches” must cite this coverage state in its reasoning. When `next_page` exists, the AI must either continue pagination or explicitly say that it shows only the returned page.

## 8. Cross-dataset joining rules

Allowed joins, in priority order:

1. Exact stable identifier match: UEI, CAGE, PIID, Notice ID, solicitation number, FAIN, or explicit source relation.
2. Explicit source-provided relationship field.
3. Name match only, labeled `name_match_candidate`.

Never infer corporate ownership, a predecessor/successor relationship, incumbent status, or a competitor solely from shared words, location, NAICS, PSC, or a general web fact.

## 9. Adapter requirements for AI platforms

Every ChatGPT, Claude, Gemini, Grok, or future adapter must:

1. Expose the Canonical dataset registry and usable tool set.
2. Map platform inputs to Canonical search vocabulary.
3. Normalize source-specific fields to the Canonical record envelope before model reasoning.
4. Preserve dataset boundaries and coverage states in the model instructions.
5. Use Canonical field names in skills, prompts, tests, and internal planning.
6. Maintain a platform adapter map instead of changing Canonical names to suit one host.

Platform-specific UI, authentication, subscriptions, logging, rate limits, deep-link rendering, and app-store metadata are outside the field/function Canon and are governed separately.

## 10. Change control

A Canon update is required before a change that:

- adds a dataset or record type;
- renames a Canonical field;
- changes the meaning of an identifier, date, amount, status, or relationship;
- permits a new cross-dataset join;
- changes the meaning of `complete`, `partial`, `unavailable`, or `unsupported`.

A platform-only change may be made without changing this Canon only if the same Canonical inputs, outputs, and functional meaning remain intact.

Every future adapter should maintain a short mapping table:

| Canon version | Platform | Adapter version | Exceptions | Verified |
|---|---|---|---|---|
| 1.0.0 | ChatGPT | pending controlled migration | Existing field names remain compatibility aliases | pending |
| 1.0.0 | Claude | not started | none | pending |
| 1.0.0 | Gemini | not started | none | pending |
| 1.0.0 | Grok | not started | none | pending |
