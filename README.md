# SkillSync — Resume → Adzuna → Ranked job matches

This source edition focuses on one purpose:

**Register/sign in → upload a resume → extract its information locally → fetch current Adzuna results → compare every fetched job against that exact resume → show a ranked, explainable shortlist.**

No career-readiness dashboard, course recommendations, learning roadmaps, employer marketplace, Gemini integration or local-model server is required. See [CORE_REVIEW.md](CORE_REVIEW.md) for the source findings, removals, test results and remaining limits.

> This focused source refactor is based on repository commit `3387cb33803859992efc8a015a931eeef9ad1625`. The instructions below apply to this updated source tree, not the older release.

## Start on Windows — no manual activation needed

For a clean install, extract the updated source ZIP into a **new folder**, not over the old release. For an existing checkout, back up `.env`, the database and uploads; use `git apply --check` on the supplied patch against the documented baseline before applying it (do not force through conflicts).

Install **Python 3.12** and **Node.js 20.19+ or 22.12+ LTS** first. Open Command Prompt in the project root (the folder containing `backend`, `frontend` and `scripts`):

```bat
py -3.12 scripts\setup_local.py
```

This creates `backend\.venv`, installs the hash-locked backend dependencies (including uvicorn), generates a unique JWT secret, migrates SQLite, installs the frontend using `npm ci`, and builds it. It preserves existing `.env` and database files.

Configure your own legitimate Adzuna credentials:

```bat
notepad backend\.env
```

Set:

```dotenv
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key
ADZUNA_COUNTRY=in
```

Obtain credentials from https://developer.adzuna.com/signup. Keep them **only in the backend `.env`**, never in frontend `VITE_*` variables, source control, screenshots or chat. A valid provider account and available quota are required.

Start these commands in **two separate terminals**, both at the project root:

```bat
py -3.12 scripts\run_local.py api
```

```bat
py -3.12 scripts\run_local.py web
```

Open **http://localhost:5173**, create your own account and upload a text-based PDF or DOCX (up to 5 MB). With Adzuna configured, a newly uploaded resume triggers a first search using an editable skill-derived query. You can change the title/keywords, location, country, age limit and result count, then select **Find matches**.

If an existing `.env` contains the old public example JWT secret, startup now rejects it. Generate a new secret **locally**, set it as `JWT_SECRET_KEY` in that file, and sign in again (existing tokens become invalid):

```bat
py -3.12 -c "import secrets; print(secrets.token_hex(48))"
```

Do not share that output. Setup deliberately does not silently overwrite existing credentials.

Restart the API after editing `.env`. No Adzuna keys? Resume extraction still works; the UI explicitly reports configuration is required and does **not** substitute demo vacancies.

Native Windows execution was not available in the audit environment. The scripts use Windows-compatible paths and Python HTTP requests rather than `curl.exe`; actual installation/browser tests were performed on Linux. Please share an exact installation error if your Windows environment differs.

## Linux/macOS commands

Use `python3.12` instead of `py -3.12` and forward slashes:

```bash
python3.12 scripts/setup_local.py
# Separate terminals:
python3.12 scripts/run_local.py api
python3.12 scripts/run_local.py web
```

The tested platform was Debian 13 x86_64, Python 3.12.15 and Node 20.20.2. macOS was not executed in this audit. No GPU, WSL or model downloads are required by this implementation.

## How matching works

1. **Local extraction:** PyMuPDF reads text PDFs; python-docx reads paragraphs, tables and headers/footers. Skills use a bounded term/alias taxonomy. Education/experience sections retain their actual text. Missing contact details, degrees and experience durations remain unknown.
2. **Resume isolation:** parsing creates a saved `ResumeAnalysis`. Matching reads that snapshot, never account-wide skills or another uploaded document. Older analyses from the previous fabricated-default parser require re-analysis.
3. **One bounded provider search:** Adzuna is called over HTTPS with keywords and filters. No resume text, contact details or full extracted profile are sent. Up to 100 results are fetched across pages; default 50. Missing credentials, invalid keys, timeouts, rate limits and invalid provider payloads are explicit errors, not successful empty searches.
4. **Normalize and rank:** IDs are deduplicated; explicitly expired/out-of-window listings are excluded. Every remaining fetched listing is scored before sorting. A good match on provider page 2 can rank above every job on page 1. No background generic job ingestion or shared cross-query result cache is used.
5. **Explain the result:** each job shows skills found/not found in the selected resume, supporting text excerpts, applied score weights, salary currency, provider-estimate flags, posting date and a safe Adzuna link. Unspecified metadata is not invented.
6. **Save by resume:** successful search results persist with resume ID, analysis ID, filters, provider and fetch timestamp. Reloaded results are explicitly marked **saved**, not a new availability check. Refresh to fetch current results again. Failed searches do not overwrite history with a fake successful result.

### Score definition

Base weights: explicitly required skills 45%, preferred skills 10%, other mentioned skills 10%, local TF-IDF-style lexical overlap 25%, experience ratio 10%. Only applicable signals participate; their weights are renormalized and shown in the UI. Unknown requirements/experience do not receive automatic full marks. Education and project counts do not get invented scoring requirements.

Experience uses an explicit years-of-experience statement, or an estimate from month/year ranges in the experience section, merging overlaps. It does not treat the number of jobs as years of experience.

**A score is an overlap heuristic, not a probability of getting hired or a guaranteed perfect match.** Skill mention is not proof of proficiency. The taxonomy is strongest for technical roles; non-technical coverage and complex resume layouts are limited. Adzuna returns **description snippets**, so absence from a snippet/resume is not proof that a qualification is absent from the full document or person. Review the evidence and original vacancy before applying. No application is submitted automatically.

## Tests

From `backend` on Windows:

```bat
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m alembic current
```

Linux: use `.venv/bin/python` instead. From `frontend`:

```bash
npm run lint
npm test
npm run build
npm audit
```

The focused suite replaces tests for the deliberately removed product features. Provider tests intercept HTTP with synthetic responses but run real pagination, parsing, matching, ownership checks and persistence. They never require or consume real Adzuna credentials.

### Optional browser integration test

Install Playwright separately in a development environment (`pip install playwright python-docx`, then `python -m playwright install chromium`; minimal Linux systems may need `install --with-deps chromium`).

1. From `backend`, start `python -m tests.serve_browser_fixture` (port 8001).
2. Start frontend preview on 5174 with `VITE_BACKEND_URL=http://127.0.0.1:8001` set in that terminal.
3. From `backend`, run `python scripts/verify_core_browser.py`.

The test server has isolated temporary data and a prominent **TEST FIXTURES — not live vacancies** banner. It is not a production provider or demo-data mode. Never start it instead of `app.main:app` for normal use.

## Configuration, data and limits

- Local data: `backend/skillsync_ai.db` and `backend/storage/resumes/`. Back up both and `.env` before updating. Upload files and search results contain personal information; keep the development machine private.
- Existing `.env` is preserved. If it points to an old external database, choose the intended database deliberately. There is no silent fallback to a different SQLite database. MySQL/PostgreSQL require their respective drivers and were not tested in this audit.
- Migrations preserve historical tables/data; additive migrations add `resume_match_runs` and a processing lease timestamp. Removed product modules do not have active endpoints. There is no destructive data-drop migration.
- API docs: http://localhost:8000/api/v1/docs. Health: http://localhost:8000/api/v1/health.
- Backend/frontend ports: 8000/5173. Frontend calls relative `/api/v1`; Vite proxies to the backend. Alternative API port: set `VITE_BACKEND_URL` for the web launcher.
- For editing the frontend, use `python scripts/run_local.py web-dev`; rebuild before using `web` again.
- Password-reset email and 2FA are not provided. Registration/login/refresh/logout are implemented. No default accounts are seeded.
- Scanned PDFs need OCR (not included); encrypted PDFs, files over 5 MB, PDFs over 30 pages, expanded DOCX files over 25 MB and extracted text over 100,000 characters are rejected.
- Interrupted extraction can be retried or deleted after its five-minute processing lease expires. A superseded worker cannot overwrite the new extraction.
- Search limits: supported countries India, UK, US, Australia and Canada; 1–90 posting-age days; 20, 50 or 100 fetched results per search (the API accepts those same choices). Not the entire job market. Provider snippets can omit requirements, and vacancy status can change after a fetch.
- This is a local-development implementation. Public deployment needs HTTPS, hardened token storage, distributed rate limiting/provider quotas, retention controls and production load/security testing. Do not expose development servers on an untrusted network.

Official provider reference: https://developer.adzuna.com/docs/search
