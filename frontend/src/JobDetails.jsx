import { useEffect, useRef } from "react";
import { formatSalary, formattedDate, safeLink, getSkillSummary } from "./core";

export function SkillSummary({ job }) {
  const { matched, missing } = getSkillSummary(job);
  return (
    <div className="job-skill-summary">
      <section className="matched-skill-section" aria-label="Matched skills">
        <h4>
          Matched skills <span>{matched.length}</span>
        </h4>
        {matched.length ? (
          <div className="match-chips">
            {matched.map((skill) => (
              <span className="matched" key={skill}>
                ✓ {skill}
              </span>
            ))}
          </div>
        ) : (
          <p className="muted small">
            No skill overlap identified in this snippet.
          </p>
        )}
      </section>
      <section className="missing-skill-section" aria-label="Missing skills">
        <h4>
          Missing skills <span>{missing.length}</span>
        </h4>
        {missing.length ? (
          <>
            <div className="match-chips">
              {missing.map((skill) => (
                <span className="missing" key={skill}>
                  {skill}
                </span>
              ))}
            </div>
            <p className="muted small">
              Not found in the selected resume—not proof you lack these skills.
              Some may be optional.
            </p>
          </>
        ) : (
          <p className="muted small">
            {matched.length
              ? "None among the skills identified in this job snippet."
              : "No skill requirements identified; missing skills cannot be determined."}
          </p>
        )}
      </section>
    </div>
  );
}

export default function JobDetails({ job, resumeName, onClose }) {
  const dialogRef = useRef(null);
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!job) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialog.showModal();
    return () => {
      dialog.close();
      document.body.style.overflow = previousOverflow;
    };
  }, [job]);
  const url = safeLink(job?.application_url);
  function close() {
    onClose();
  }
  function trapFocus(event) {
    if (event.key !== "Tab") return;
    const dialog = dialogRef.current;
    const focusable = [
      ...dialog.querySelectorAll(
        'button:not([disabled]), a[href], [tabindex="0"]',
      ),
    ];
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (!first) {
      event.preventDefault();
      return;
    }
    if (
      event.shiftKey &&
      (document.activeElement === first ||
        !dialog.contains(document.activeElement))
    ) {
      event.preventDefault();
      last.focus();
    } else if (
      !event.shiftKey &&
      (document.activeElement === last ||
        !dialog.contains(document.activeElement))
    ) {
      event.preventDefault();
      first.focus();
    }
  }
  function backdrop(event) {
    if (event.target !== event.currentTarget) return;
    const box = event.currentTarget.getBoundingClientRect();
    if (
      event.clientX < box.left ||
      event.clientX > box.right ||
      event.clientY < box.top ||
      event.clientY > box.bottom
    )
      close();
  }
  return (
    <dialog
      ref={dialogRef}
      className="job-dialog"
      aria-labelledby="job-details-title"
      onCancel={(event) => {
        event.preventDefault();
        close();
      }}
      onClick={backdrop}
      onKeyDown={trapFocus}
    >
      {job && (
        <>
          <header className="job-dialog-header">
            <div>
              <span className="section-label">JOB DETAILS</span>
              <h2 id="job-details-title">{job.title}</h2>
              <p className="muted small">
                {job.company || "Company not supplied"}
              </p>
            </div>
            <button
              type="button"
              className="dialog-close"
              aria-label="Close job details"
              onClick={close}
              autoFocus
            >
              ×
            </button>
          </header>
          <div className="job-dialog-body">
            <div className="dialog-match">
              <strong>
                {job.match_score}
                <small>/100</small>
              </strong>
              <div>
                {job.match_label}
                <p className="muted small">
                  Compared with {resumeName || "the selected resume"}. Evidence
                  overlap, not a hiring probability.
                </p>
              </div>
            </div>
            <dl className="job-facts">
              <div>
                <dt>Location</dt>
                <dd>{job.location || "Not supplied"}</dd>
              </div>
              <div>
                <dt>Salary</dt>
                <dd>{formatSalary(job)}</dd>
              </div>
              <div>
                <dt>Working hours</dt>
                <dd>
                  {job.contract_time?.replaceAll("_", " ") || "Not supplied"}
                </dd>
              </div>
              <div>
                <dt>Contract</dt>
                <dd>
                  {job.contract_type?.replaceAll("_", " ") || "Not supplied"}
                </dd>
              </div>
              <div>
                <dt>Posted</dt>
                <dd>{formattedDate(job.posted_at)}</dd>
              </div>
              <div>
                <dt>Experience mentioned</dt>
                <dd>
                  {job.experience_required_years == null
                    ? "Not specified in the snippet"
                    : `${job.experience_required_years} years`}
                </dd>
              </div>
            </dl>
            <section className="dialog-description">
              <h3>Job summary</h3>
              <p className="prewrap small">
                {job.description || "No description supplied by Adzuna."}
              </p>
              <p className="muted small">
                Adzuna provides a snippet, not necessarily the full description.
                Check the original listing for complete requirements and current
                availability.
              </p>
            </section>
            <SkillSummary job={job} />
          </div>
          <div className="job-dialog-footer">
            <button
              type="button"
              className="secondary small-button"
              onClick={close}
            >
              Close
            </button>
            {url ? (
              <a
                className="apply-link"
                href={url}
                target="_blank"
                rel="noopener noreferrer"
              >
                View on Adzuna ↗
              </a>
            ) : (
              <span className="muted small">Application link unavailable</span>
            )}
          </div>
        </>
      )}
    </dialog>
  );
}
