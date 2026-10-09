# Screenshot UI corrections — 9 October 2026

Based on `main` commit `d542549ac06acb2421d12b68d01c1906e9167dab`. The user supplied screenshots and explicitly chose to preserve the purple cards and resume-analysis layout. This follow-up corrects the active source interface and adds a stale-build guard.

## What was wrong

The screenshots match the earlier `3387cb3` interface. In that source:

- `JobMatchingPage.handleSelectJob` opened a dialog only when `!isDesktop`; the dialog itself was also wrapped in `!isDesktop`. Desktop Details clicks only selected a side preview.
- `MissingSkills` returned `null` for an empty list, hiding the whole section.
- `ResumeScoreCard` centred the number against a relative wrapper without fixed dimensions. A stretched wrapper could be wider than the ring.

The previous update fixed the newer workspace but did not preserve the shown interface. In addition, the old launcher accepted any existing `dist/index.html` without checking whether it matched the current source. The precise reason this user's browser displayed older assets cannot be determined from screenshots alone; an older folder, running process, compiled build or open tab can all cause that mismatch.

## Active fixes

1. Purple job cards with the Details/Apply layout are now active in the current app, retaining the selected-resume backend and evidence-based matching. The Details button opens the selected job's popup at every viewport size. It is not a desktop-only selection action.
2. Matched and missing skills have permanent headings/counts. Empty known gaps and unknown requirements have different messages. No skills are invented to populate a card.
3. The Resume analysis view restores the personal-information cards and circular score layout. The ring and value share an explicit 132 × 132 square; the label is positioned at 50%/50% with translate(-50%, -50%), independent of parent width.
4. The footer displays **Interface: screenshot-fixes-v1 · Build <source hash>**, including on the sign-in page.
5. `npm run preview` and the Python web launcher rebuild a missing/stale frontend before serving it. Bare Vite preview rejects a stale build. Responses use `Cache-Control: no-store`. The launcher prints the actual source folder. Existing running processes and already-open browser tabs still need to be stopped/reloaded by the user.

These are active components, not a patch to unused legacy files. Unrelated old workflows and unsafe account-wide matching were not restored.

## Score integrity

The old `92` was displayed by mapping `analysis.confidence` to a field labelled “quality score”; it was not a validated resume-quality metric. The old adapter also substituted a fixed 88 when confidence was absent. Those defaults are not restored.

The corrected gauge centres an explicitly supplied quality score (`analysis.quality_score` or `profile.resume_quality_score`). The current evidence-only backend does **not** calculate that metric, so real analyses without it show **Not assessed / —**, not a made-up 92 or a reinterpretation of extraction confidence. No scoring algorithm was invented for a layout request.

Geometry tests supply 0, 92 and 100 through a clearly labelled browser-only fixture to verify alignment. These are synthetic test values, not scores from the user's resume.

## Verification

- Backend regression suite: **51 passed**, 2 existing dependency warnings.
- Frontend tests: **10 passed**; includes unknown-score validation and stale-build fingerprint tests.
- ESLint and production build passed.
- Chromium: desktop and mobile popup open/close, different cards/different jobs, visible missing/empty skill states, Tab/Shift+Tab focus containment, Escape/backdrop dismissal, and selected-resume isolation passed with no page errors.
- Score centre measured within **0.75 CSS pixels** on both axes for 0, 92 and 100 at 1440px and 390px widths. No mobile horizontal overflow.
- Actual stale-build experiment: source was changed after compilation; the guard detected the stale build and `npm run prepreview` rebuilt it successfully.
- Provider responses and score geometry values in browser checks were fixtures, not live Adzuna verification. Native Windows execution was not available.

## Use the corrected source

After applying this source update, stop the old API/web processes with Ctrl+C in their terminals. From the updated project folder:

```bat
py -3.12 scripts\setup_local.py
```

Then, in two separate terminals at that same root:

```bat
py -3.12 scripts\run_local.py api
```

```bat
py -3.12 scripts\run_local.py web
```

Open http://localhost:5173 and press **Ctrl+Shift+R** once. Confirm the footer says **Interface: screenshot-fixes-v1**. If that text is absent, the browser is not showing this corrected build. Do not delete databases, uploads or `.env` to address a UI problem.
