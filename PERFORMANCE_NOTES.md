# Navigation and matching performance update

## Diagnosis from the actual source

Baseline: `bc8e470e750ee93a7fafde182febf2425dad9925` (purple screenshot interface).

- Resume bootstrap waited for provider status; analysis waited for saved jobs through `Promise.all`.
- Re-selecting a previously viewed resume fetched its analysis and saved results again.
- Switching the two workspace tabs already used local state, not another API request. However, it unmounted/recreated the job cards and their hidden evidence DOM.
- Up to 100 cards and every closed explanation were eagerly rendered. Editing search fields re-rendered those cards.
- Fresh searches cleared the previous shortlist before a response arrived.
- Backend profiling found repeated taxonomy-pattern construction/lookups and repeated tokenization of the same resume for every job.

## Implemented changes

1. **Session-only snapshots:** per signed-in Workspace instance, 60-second freshness TTL, 16-entry LRU cap and an approximate 8 MiB serialized UTF-16 budget. No resume/job data is placed in localStorage, sessionStorage or a global cross-user cache. Existing authentication-token storage is unchanged. Concurrent identical GETs share one request. Logout/unmount clears the cache and aborts pending GETs.
2. **Independent loading:** resume list, provider status, analysis and saved matches no longer unnecessarily wait for one another. The `/auth/me` identity check is preserved.
3. **Mutation/race safety:** upload/re-analysis/deletion refresh the relevant data; successful searches replace the saved snapshot. Aborted/invalidated GETs cannot reinsert old data, and UI generation guards prevent already-queued callbacks from overwriting a newer selection/search. Displayed results must match both selected resume ID and analysis ID.
4. **Cheaper navigation/rendering:** tab views stay mounted but inactive content is hidden from layout, focus and accessibility navigation. Cards are memoized; explanation content mounts only when opened. Initially render 20 cards, with “Show next 20 jobs” revealing already-ranked results without fetching again. All fetched jobs are still scored and sorted first. The home logo now navigates within the workspace instead of reloading the document.
5. **Honest refresh UX:** existing matches remain visible during a new search and on failure, marked as saved with the previous query and fetch timestamp. A failed provider call remains an error, not a successful empty search. **Find matches always performs a new provider search.** “Refresh saved data” revalidates the resume and saved run, not live vacancy availability.
6. **Faster ranking without changing scores:** compile static skill patterns once, prepare resume tokens/skills once per search, and reuse repeated clause evidence in a bounded 256-entry request-local cache. Pair-specific IDF, scoring weights, evidence, filtering and ordering are preserved. There is no global resume/text/result cache on the backend.
7. **Smaller network payloads:** gzip large analysis/job JSON responses (minimum 1 KiB, level 4) when the client supports it. Login/token responses and file downloads are excluded. API responses use `Cache-Control: private, no-store`; explicit frontend session memory is the data-reuse mechanism, not shared/disk HTTP caching.

The purple appearance, Details popup, visible missing-skill sections and centred/unknown score behaviour are preserved. No database migration, new runtime dependency, external AI API, or provider-key change is needed.

## Measurements — local synthetic tests only

These are not claims about the user's machine, production load or live Adzuna latency.

### Ranking CPU, 100 synthetic jobs and a 23.7K-character resume

Same fixture, machine and five runs per version:

| | Baseline | Optimized |
|---|---:|---:|
| Median ranking time | 1.3203 seconds | 0.2059 seconds |
| Profile call count | 5,164,233 | 270,292 |

**Approximately 6.4× faster / 84.4% less local ranking CPU time.** The fixture deliberately has repeated requirement clauses; improvement will vary with real descriptions. A later verification run measured 0.1923 seconds median.

All 100 complete ranked records were compared byte-for-byte after canonical JSON serialization. Scores, evidence and ordering were identical. Baseline SHA256:

`0e5a84e7515067fad2834d08fcaa205025414bbf9f41aa7724df8678d12218fb`

Reproduce from the repository root:

```bat
py -3.12 backend\scripts\benchmark_matching.py --runs 5
```

On Linux/macOS use `python3.12 backend/scripts/benchmark_matching.py --runs 5`. This benchmark uses only local synthetic data and no provider account. Optional `--output ranking.json` exports that synthetic result. CI checks output identity/work counts, not a hardware-dependent speed threshold.

### Chromium navigation test

Controlled saved-jobs delay: **900 ms**. Controlled provider-status delay: **1,200 ms**.

- Analysis became visible before either delayed response arrived.
- Six warm resume switches plus repeated tab/home navigation: **zero additional API requests**.
- Final production-preview sample: warm switch median **22.5 ms**, maximum **33.6 ms**, including browser automation overhead. Development/StrictMode sample: median 70.3 ms; maximum 105.1 ms. These are observations, not latency guarantees.
- 100 ranked jobs initially created **20 cards**; closed explanations created **zero comparison-content nodes**.
- Existing card DOM survived tab switches. Show more did not fetch again.
- Cards stayed visible during a deliberately held fresh search.
- A delayed old saved response did not replace a newer successful search.
- Repeated fresh searches still issued POST requests; manual refresh re-fetched saved data.
- Signing into a different account did not expose the prior account's snapshots.
- No browser page errors.

## Verification

- **54 backend tests passed**, including baseline-output identity, once-per-search preparation, per-profile isolation and selective compression. Two existing dependency deprecation warnings remain.
- **18 frontend tests passed**, including TTL, in-flight deduplication, invalidation, old-response protection, per-session isolation, bounds, retries and StrictMode-style teardown.
- Frontend lint and production build passed.
- Existing real-API Chromium regression passed: auth, extraction, matching, modal keyboard/mobile behaviour, score geometry, saved results, resume switching/deletion and logout.
- Delayed-response navigation test passed against both production preview and development/StrictMode.

The optional browser environment/setup is documented in README. With the labelled fixture API on 8001 and frontend proxy on 5174, run from `backend`:

```text
python scripts/verify_core_browser.py
python scripts/verify_navigation_performance.py
```

To test another frontend port, set `BASE_URL` before running the navigation script. Never use `tests.serve_browser_fixture` as the normal application API; it has synthetic accounts/jobs and isolated temporary data.

## Applying this update

The performance patch targets the exact `bc8e470` baseline above. Back up `.env`, your database and uploads, and stop both running servers. From an otherwise clean checkout of that baseline:

```bat
git apply --check ..\skill_sync_performance_bc8e470.patch
git apply ..\skill_sync_performance_bc8e470.patch
```

Adjust the patch path to where it was downloaded. Do not force through conflicts. Alternatively, extract the accompanying source ZIP to a new folder and follow README's setup/data-preservation instructions. The archive contains source, not your private configuration or data.

For an already configured checkout, restart in two terminals:

```bat
py -3.12 scripts\run_local.py api
py -3.12 scripts\run_local.py web
```

Open `http://localhost:5173` and hard-refresh once. The web launcher rebuilds when its source fingerprint changes. Confirm the purple UI now includes **Refresh saved data** and, for large shortlists, **Show next 20 jobs**. If your dependencies were not installed in this folder, run `py -3.12 scripts\setup_local.py` first.

## Remaining limits

- A genuinely new Adzuna search still needs the external service, its quota and the network. These tests use clearly labelled HTTP fixtures; no live credentials/latency/load were verified.
- Cache TTL is checked when loading/re-selecting a resume; it is not a periodic polling timer. An older snapshot may appear immediately while revalidation runs. Other tabs/devices do not push invalidations into this session. Use **Refresh saved data** for changed resume data, and **Find matches** for a fresh provider search.
- Cold loads still need authentication and initial data retrieval. Cache eviction can require another GET. Keeping tabs mounted trades modest DOM memory for faster navigation; showing further cards deliberately increases their count.
- This is not a production-load audit or native Windows execution test. Existing OCR, snippet-quality, taxonomy and deployment limitations still apply.
