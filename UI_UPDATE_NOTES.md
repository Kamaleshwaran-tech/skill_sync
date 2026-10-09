# Job card UI update — 9 October 2026

Based on GitHub `main` commit `02b47514e820f007ff553d98946b365d188d7a47`. This update adds the job-details popup and visible skill gaps described below. Circular resume-score alignment remains pending the requested screenshot.

## Implemented

- Added an operational **Details** button at the bottom of every job card.
- Added a responsive popup showing that specific job's title, company, location, salary, hours, contract type, posting date, stated experience, description snippet, selected-resume match score, and matched/missing skills. Unspecified fields remain unknown.
- Kept the original Adzuna link separate from the popup action. Unsafe links are still rejected and description text is not injected as HTML.
- Added clear **Matched skills** and **Missing skills** headings and counts on every card and in the popup. No skills are hidden behind a count limit. Comparison evidence is used as a fallback when saved summary lists are missing.
- Added accurate zero/unknown states: no detected gaps is different from having no identifiable job requirements. “Missing” means not found in this resume, not proof that the person lacks the skill. Some missing mentions are optional.
- Added keyboard focus containment in both directions, focus restoration to the Details button, Escape dismissal, close buttons and backdrop dismissal. Opening/closing the popup repeatedly does not leave the page scroll-locked.

## Verification

- Backend regression tests: **51 passed**, 2 existing dependency warnings.
- Frontend utility tests: **8 passed**.
- ESLint and production build: passed.
- Chromium integration: passed with no page JavaScript errors. Tested distinct cards opening distinct details, missing skills, no-gap messages, keyboard-only open/close, Tab/Shift+Tab containment, focus restoration, repeated opening, backdrop dismissal, and a 390px mobile viewport without horizontal overflow. Existing upload, saved-result, resume isolation and logout checks also passed.
- Browser tests use explicitly labelled synthetic provider responses, not live Adzuna vacancies.

## Still needs the user's screenshot

The requested **circular resume-score number alignment** cannot be located in this source tree. The current resume-analysis area shows extracted evidence and experience, not a standalone circular resume score. Job cards use a horizontal match bar.

Please provide a screenshot of that circular indicator and, if possible, the page URL/startup command. A previously built frontend may still show an older interface even after a source pull. Rebuild the frontend and restart the web launcher when applying source changes. No new resume score or unrelated circular widget was invented in this update.

## Apply

For an existing clean checkout at the baseline commit, check and apply `skill_sync_job_details_update.patch`, then run `npm ci` and `npm run build` inside `frontend`; restart the web launcher. Do not force a patch through conflicts.

Alternatively, use the updated source ZIP in a new folder and follow the root README. Credentials, databases, uploaded resumes, dependencies and compiled build files are excluded from delivery. Do not overwrite or delete existing private data.
