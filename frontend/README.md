# SkillSync frontend

A focused React workspace for authentication, resume extraction review, Adzuna filters, evidence-based ranking and saved results. No roadmap/course/readiness dashboards or employer screens.

Use the root setup/launcher scripts. For development, run `npm ci` and `npm run dev`; `/api` is proxied to port 8000 by default. `VITE_BACKEND_URL` changes the server-side proxy target. Never put provider credentials into a `VITE_*` variable.

Checks: `npm run lint`, `npm test`, `npm run build`. Actual browser workflow is tested separately with explicitly labelled synthetic Adzuna HTTP responses; see the root README.
