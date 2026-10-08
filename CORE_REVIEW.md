# Focused source review and verification

**Review date:** 8 October 2026
**Repository:** https://github.com/Kamaleshwaran-tech/skill_sync.git
**Source baseline:** `3387cb33803859992efc8a015a931eeef9ad1625`
**Delivery:** focused source refactor of the repository. This report records code verification, not troubleshooting or repackaging the old release.

## Decision

Keep one active product flow: **login → upload → evidence extraction → fresh Adzuna search → rank against the selected resume → explain/save results**.

A “perfect match” cannot be guaranteed by this or another automated ranking system. This implementation instead fixes provenance, resume isolation, provider failure handling, ranking consistency and reproducibility. Scores are labelled evidence-overlap heuristics, not hiring probabilities. Adzuna descriptions are snippets and the returned candidate pool is bounded.

## Findings and corrections

| Original source finding | Why it mattered | Correction |
|---|---|---|
| Resume parsing supplied guessed/default personal, education or experience information | Fabricated evidence could affect the result | Replaced parser with local PDF/DOCX text extraction, real source excerpts and null unknowns. DOCX tables are included. Old unversioned analyses are hidden from the evidence view until re-analysis. |
| Matching could draw on account-level skills rather than the selected document | Two resumes for the same user could contaminate each other | Search requires a resume ID owned by the user and its current `evidence-v1` analysis. Account `UserSkill` rows are not matching inputs. |
| Provider ingestion/cache paths mixed general or previous-query results | Results could be stale or unrelated to current filters | Removed ingestion/global job-cache matching. Every explicit search calls the official Adzuna API with the current query, filters and bounded pagination. |
| Provider failures were swallowed into empty-result behavior | Invalid credentials and outages looked like “no jobs” | Typed, sanitized configuration/auth/quota/timeout/payload errors. A genuine empty response is a separate successful result. No fake-job fallback. |
| Multiple overlapping match/recommendation services and frontend fan-out | Different screens could use different scoring or duplicate requests | One provider implementation, one normalizer/scorer and one selected-resume search endpoint. |
| Score components could reward missing or unsupported information | Scores appeared more certain than the evidence | Required/preferred/mentioned skill evidence, lexical similarity and explicit/estimated experience only. Available weights are renormalized and displayed. No fabricated degree/project bonus. |
| Skill boundaries, negation and mixed requirement clauses were error-prone | JavaScript could imply Java, or an explicitly negative mention could receive credit | Boundary-aware aliases, conservative handling of common explicit negatives, required/preferred clause handling and tested year ranges. These remain heuristics, not comprehensive language understanding. |
| Old scores could survive resume switching/reload without clear provenance | Users could mistake another resume’s result or an old search for a fresh fetch | `ResumeMatchRun` ties snapshots to user, resume and analysis. Saved results show their timestamp and a non-live warning. The frontend clears stale results when changing selection. |
| A killed parser could leave a resume permanently PROCESSING | Retry/deletion could remain blocked | Additive processing timestamp and five-minute lease; stale processing can be retried/deleted. A superseded worker cannot overwrite newer work. |
| Resume/analysis could change during the provider request | Results could be saved against stale/deleted evidence | Recheck ownership and current analysis after the network call; handle a final FK race with a retryable conflict, not a successful orphan result. |
| Validation/logging could expose sensitive inputs or provider URLs | Passwords or query-string credentials could appear in logs | Log field locations rather than validation input values; hide settings input in validation errors and suppress HTTP URL debug logging. Never return credentials in provider errors. |
| Setup and runtime depended on unrelated product/AI machinery | Missing uvicorn/models/services obscured the real pipeline | Slim hash-locked backend, minimal React dependencies, portable Python setup/launch scripts, unique JWT secret, rejection of the old public example secret, explicit SQLite migration and no model downloads. |

Principal replaced/removed paths in the baseline included `app/services/resume_parser.py`, `job_match_service.py`, `semantic_job_matching.py`, `job_ingestion_service.py`, the integration/provider abstractions and the parallel `app/ai` implementation tree. Current matching lives in `app/services/adzuna.py`, `evidence.py`, `job_matching.py` and `app/routers/jobs.py`.

## Removed from the active application

- Roadmaps, courses, learning recommendations and career-readiness dashboards.
- Employer/admin marketplace workflows, job CRUD, applications and unrelated profile/skill-management screens.
- External/local LLM providers, model installer/server, model weights and unrelated AI dependencies.
- Demo/default account setup, fake vacancy fallback, redundant matching services and obsolete release/audit documentation.
- Generated bytecode/build/runtime data from the source delivery.

**Preserved deliberately:** authentication, ownership checks, historical ORM tables and migration history. Removing an unused screen is not permission to erase existing user data. Migrations `20261008_0011` (matching snapshots) and `20261008_0012` (processing lease) are additive. Legacy tables are not active product endpoints.

## End-to-end data contract

1. Register/login with candidate credentials; access and refresh tokens are separate and logout revokes the session.
2. Upload a PDF/DOCX; reject incorrect types, invalid containers, oversized files and excessive DOCX expansion. Store using a generated private filename.
3. Extract locally; save a versioned, immutable analysis. Repeated successful analysis does not create unnecessary copies. Only a newly uploaded document changes the evidence.
4. `POST /api/v1/jobs/search` validates ownership, completed extraction, query/location lengths, country, posting age and a result count of **20, 50 or 100**. These choices align with provider pagination so the fetched candidate set is ranked in full.
5. Fetch Adzuna results over HTTPS with bounded retries/timeouts. Send keywords and filters, not the resume or contact data. Normalize metadata, deduplicate IDs and exclude explicitly stale/expired listings before scoring.
6. Rank by score, then recency and ID for deterministic ties. Explain the required/preferred/mentioned comparisons, evidence and score breakdown.
7. Save results with the exact analysis ID and fetch timestamp. Retrieve only the latest snapshot for the current analysis. Deletion removes that resume’s new matching history and extraction records.

Base weights: required skills **45%**, preferred **10%**, other mentions **10%**, lexical overlap **25%**, experience **10%**; omit unavailable signals and renormalize. Experience uses an explicit statement or non-overlapping month/year intervals, not the number of past jobs.

## Verification actually performed

| Check | Result |
|---|---|
| Focused backend tests | **51 passed**, 2 dependency deprecation warnings |
| Frontend utility tests | **5 passed** |
| ESLint | Passed |
| Frontend production build | Passed; 74 modules |
| Installed backend dependency consistency | `pip check` passed |
| Python locked-dependency advisory scan | `pip-audit`: **0 known vulnerabilities** at scan time |
| Frontend advisory scan | `npm audit`: **0 vulnerabilities** at scan time |
| Fresh SQLite migrations | Passed through `20261008_0012` |
| Upgrade of a copy of the prior local database | Passed; row counts in all historical tables retained; original left untouched |
| Chromium desktop/mobile workflow | Passed; no page JavaScript errors; no horizontal overflow at 390px |
| Real local API/frontend smoke checks | Health, HTML and OpenAPI returned 200; only root/core route groups exposed |
| Sanitized ZIP installation | Setup, locked install, migrations, frontend build and focused tests passed in a separate extracted copy |
| Patch verification | Applied to the documented baseline; patched source tree byte-identical to packaged files |
| Real Adzuna account/vacancy retrieval | **Not verified — no credentials supplied** |
| Native Windows/macOS execution | **Not verified**; Linux/Python 3.12.15/Node 20.20.2 tested |
| Production security/load or external database engines | **Not verified** |

Backend coverage includes auth/token rotation/logout, owner isolation, actual PDF/DOCX parsing, table extraction, unknown values, skill boundaries and explicit negation, overlapping experience ranges, selected-resume vs account-skill isolation, full fetched-set ranking, deduplication/expiry, currency/unsafe URLs, search snapshots, legacy re-analysis, rejected files/ZIP expansion, provider HTTP errors/timeouts/invalid/partial responses, credential redaction, interrupted processing and changed-analysis races.

Provider tests intercept **HTTP transport only**, allowing real provider pagination, extraction, scoring and persistence code to run. These are synthetic tests, not proof of live Adzuna access.

Browser verification (`backend/scripts/verify_core_browser.py`) covers registration/login, DOCX upload, automatic first search, visible evidence explanations, saved reload, token refresh, switching between two distinct resumes, provider failure versus zero results, mobile layout, deletion/switching and logout. The separate fixture server uses temporary data and visibly labels all jobs **TEST FIXTURES — not live vacancies**. It is not part of normal app startup.

The two backend warnings are upstream Starlette TestClient/httpx and passlib `crypt` deprecations. They are not failing tests; Python 3.12 remains the documented runtime. Advisory scans are point-in-time checks, not a security certification.

## Important remaining limits

- **Live integration is the next external gate:** configure valid `ADZUNA_APP_ID` and `ADZUNA_API_KEY`, restart the API, then search using an actual resume and check that returned links resolve. Never share keys in chat. Account entitlement, quota, country-specific behavior and actual live response completeness were not tested.
- There is no labelled resume/job relevance benchmark, hiring-outcome calibration, OCR or general semantic model. Complex layouts, unconventional headings, negation scope, abbreviations and nuanced job requirements can still be misread. A detected phone/name or self-reported experience figure is not verified identity or skill proficiency.
- Required skills not found in a resume are labelled **not found**, not asserted to be absent from the person. Requirements missing from an Adzuna snippet remain unknown.
- The editable search suggestion can be poor for non-technical roles or multi-skill resumes. Refine the job title/location; the bounded provider subset is not the entire job market.
- A job can close after retrieval. Saved results are historical. The application does not submit applications or guarantee employment.
- This is a local-development app, not production-ready infrastructure: localStorage tokens, process-local throttling, provider quotas/retention and upload isolation need deployment-specific hardening. Password recovery/email and 2FA are not implemented.
- No destructive legacy-data cleanup was attempted. Account-wide historical-data erasure and search-history retention policy remain separate work.

## Reproduce / use the delivery

Follow [README.md](README.md). It includes direct Windows commands that create the virtual environment and install uvicorn, Adzuna configuration, separate API/web launchers, test commands and optional browser-test instructions. Keep existing data backed up before migrating.

Official Adzuna reference: https://developer.adzuna.com/docs/search — documents endpoint/query fields and explicitly describes returned descriptions as snippets.
