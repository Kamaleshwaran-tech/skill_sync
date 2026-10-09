# SkillSync frontend

A focused React workspace for authentication, resume extraction review, Adzuna filters, evidence-based ranking and saved results. No roadmap/course/readiness dashboards or employer screens.

Use the root setup/launcher scripts. For development, run `npm ci` and `npm run dev`; `/api` is proxied to port 8000 by default. `VITE_BACKEND_URL` changes the server-side proxy target. Never put provider credentials into a `VITE_*` variable.

Checks: `npm run lint`, `npm test`, `npm run build`. Actual browser workflow is tested separately with explicitly labelled synthetic Adzuna HTTP responses; see the root README.

## Screenshot corrections

The active interface preserves purple job cards and a Resume analysis view. Details opens a popup at every viewport width; missing skills are always labelled; the circular score has a fixed-size ring and centred label. Unknown quality scores remain unknown.

The footer must show `Interface: screenshot-fixes-v1`. `npm run preview` automatically rebuilds stale source; direct Vite preview refuses stale output. Stop old processes and hard-refresh the browser once after updating. See root `UI_UPDATE_NOTES.md`.
