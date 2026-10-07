# Extraction Task Contracts

A task contract = a typed input/output schema for one pipeline stage. Models are swappable behind a contract; prompts are per-model implementations of it. Implement each as a pydantic model in `src/twm/pipeline/extract.py`; every LLM call returns JSON validated against the contract, with retry-on-validation-failure (max 2, then flag).

Provenance rule: every extracted value carries `source_ref` — document id + page/section/table coordinates — so any number traces back to its exact location (the audit trail).

## Contract 1: `RateCardExtraction`

Input: document text/tables (one rate card or rate exhibit).
Output:
```
RateCardExtraction:
  document_meta: {issuer, counterparty|null, effective_date|null, expiry|null, currency, rate_unit (hour|day|month), source_ref}
  rows: list[RateRow]
RateRow:
  observed_title: str
  level_raw: str|null            # "Level 2", "SFIA 4" (a vendor's level label), "Senior" — verbatim
  rate_value: Decimal
  rate_qualifier: str|null       # "NTE", "ceiling", "offshore", "not to exceed"
  location_raw: str|null         # verbatim location/tier column label
  years_experience_raw: str|null
  conditions: str|null           # discounts, travel, minimums — verbatim short
  confidence: float              # model self-estimate, 0–1
  source_ref: SourceRef
```
Never normalize inside extraction: verbatim capture here; normalization is a separate stage. Test documents: `corpus/gc15_ratecards/` (extractions to compare against), Texas Appendix C, GSA pricelists.

## Contract 2: `SOWExtraction`

Output:
```
SOWExtraction:
  document_meta: {parties: list[str], document_type (MSA|SOW|task_order|amendment|subcontract), effective_date|null, term|null, governing_msa_ref|null, source_ref}
  pricing_model: (time_and_materials|fixed_fee|milestone|capacity|consumption|resource_unit|mixed|unstated)
  rate_table: list[RateRow]      # reuse RateRow
  named_resources: list[{name_or_role, observed_title, location_raw|null, source_ref}]
  commercial_terms: list[{term_type (discount|minimum_commitment|volume_tier|mfc|escalation|expense_policy|invoicing|credit), verbatim_short, source_ref}]
  amendment_chain: {amends: str|null, amendment_number: str|null}
  redactions_present: bool
  confidence_overall: float
```

## Contract 3: `TitleResolution` (the resolve-once call)

Input: observed_title + full surrounding context (the SOW paragraph/table it appeared in) + candidate roles (from embedding search) + taxonomy definitions.
Output:
```
TitleResolution:
  canonical_role_id: str|null
  twm_band: (junior|intermediate|senior|lead_principal)|null
  attr_technology: str|null      # from tech_vocab only
  attr_location: (onshore|nearshore|offshore)|null
  reasoning: str                 # stored local-tier only; never promoted
  confidence: float
  abstain: bool                  # true → human queue; abstaining beats guessing
```

## Contract 4 (M4+): `ReconciliationFinding` — timecard↔invoice↔SOW discrepancies. Define when the synthetic factory exists; discrepancy classes to plant and detect: rate-above-contract, off-rate-card role, unapproved location premium, hours mismatch, duplicate billing, wrong level billed. (The Fulton County audit in the invoice manifest documents these classes from a real audit.)

## Model client rule

One thin wrapper (`src/twm/llm.py`): `call(task_contract, prompt_bundle, model_config) -> validated_output`. Model name, temperature (=0 for extraction), max retries are config. Log every call: model, tokens, latency, validation pass/fail — this log IS the raw material for stage-level model comparison.
