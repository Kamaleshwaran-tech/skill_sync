# SkillSync backend

See the root [README](../README.md) for Windows/Linux setup and Adzuna configuration, and [CORE_REVIEW](../CORE_REVIEW.md) for findings and verification.

Active APIs: authentication, health, resume upload/analysis/download/deletion, Adzuna configuration status, resume-specific job search and saved match retrieval. OpenAPI is at `/api/v1/docs`.

Only the selected resume analysis is used for scoring. Provider credentials stay on the server. There is no external resume/AI call, default account, seeded job feed or silent database fallback.

Legacy ORM tables/migrations remain to preserve existing databases; removed product modules are not mounted as API routes.
