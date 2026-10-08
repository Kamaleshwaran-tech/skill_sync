# Security boundaries

- Keep `backend/.env`, database files and uploads out of Git. Setup generates a persistent random JWT secret.
- Adzuna credentials are backend-only. HTTP client URL logging is suppressed because the provider requires query-string credentials. Provider errors return sanitized messages, not URLs or keys.
- Resume text is processed locally. Only query keywords/location/country/date limits are sent to Adzuna.
- Resume files, analyses and match history are owner-scoped. Authentication includes refresh rotation and access/refresh revocation on logout.
- Uploads use generated filenames, path checks, size limits and DOCX expanded-size checks. Text extraction cannot guarantee safety/accuracy for every malformed document.
- Historical tables are preserved, not exposed by the removed marketplace/career endpoints. Resume deletion removes the selected file, its analyses and its new matching history; this is not an account-wide legacy-data erasure workflow.
- No default passwords, no real two-factor authentication and no password recovery/email service are included. Test credentials belong only to isolated synthetic test accounts.
- Frontend tokens currently use localStorage. For public deployment, review HttpOnly cookie/token storage, HTTPS, CSP, upload isolation, database/backup protections, retention, provider quota abuse controls and distributed rate limiting. The local development setup is not a production security certification.
- Package advisory scans are point-in-time checks, not a penetration test. Do not expose dev/preview servers publicly.
