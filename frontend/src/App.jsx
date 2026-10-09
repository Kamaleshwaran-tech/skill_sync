import ResumeAnalysisPanel from "./features/resume-analysis/components/ResumeAnalysisPanel";
import JobDetails, { SkillSummary } from "./JobDetails";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createSessionCache } from "./sessionCache";
import {
  apiClient,
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  setAuthTokens,
} from "./shared/api/apiClient";
import {
  errorMessage,
  formatSalary,
  formattedDate,
  safeLink,
  isEvidenceAnalysis,
} from "./core";

function BuildIdentifier() {
  return (
    <span className="build-identifier">
      Interface: screenshot-fixes-v1 · Build{" "}
      {import.meta.env.VITE_SKILLSYNC_BUILD?.sourceHash?.slice(0, 8) ||
        "development"}
    </span>
  );
}

function Brand({ onHome }) {
  return (
    <a
      className="brand"
      href="/"
      aria-label="SkillSync home"
      onClick={
        onHome
          ? (event) => {
              event.preventDefault();
              onHome();
            }
          : undefined
      }
    >
      <span className="brand-icon">
        S<span>↗</span>
      </span>
      SkillSync<span className="brand-dot">.</span>
    </a>
  );
}
function Notice({ children, tone = "info" }) {
  return children ? (
    <div
      className={`notice ${tone}`}
      role={tone === "error" ? "alert" : "status"}
    >
      {children}
    </div>
  ) : null;
}

function Authentication({ onLogin }) {
  const [register, setRegister] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      if (register) {
        await apiClient.post("/auth/register", {
          email: values.email,
          password: values.password,
          full_name: values.name,
        });
        setRegister(false);
        setMessage("Account created. Sign in to upload your resume.");
      } else {
        const { data } = await apiClient.post("/auth/login", {
          email: values.email,
          password: values.password,
        });
        setAuthTokens(data);
        onLogin((await apiClient.get("/auth/me")).data);
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth-shell">
      <header className="topbar">
        <Brand />
        <span className="quiet">RESUME → OPPORTUNITY</span>
      </header>
      <main className="auth-grid">
        <section className="auth-intro">
          <span className="eyebrow">A clearer next step</span>
          <h1>
            Your experience.
            <br />
            The right
            <br />
            <em>opportunities.</em>
          </h1>
          <p>
            Turn your resume into an explainable shortlist of current job
            openings. Less guessing. More relevant applications.
          </p>
          <div className="journey">
            <span>
              01 <b>Upload a resume</b>
            </span>
            <span>
              02 <b>Search Adzuna</b>
            </span>
            <span>
              03 <b>See the evidence</b>
            </span>
          </div>
          <div className="privacy-note">
            ◈ Your resume stays on this server. Only job-search keywords and
            filters go to Adzuna.
          </div>
        </section>
        <section className="auth-card">
          <span className="eyebrow">YOUR WORKSPACE</span>
          <h2>{register ? "Create your account" : "Welcome back"}</h2>
          <p className="muted">
            {register
              ? "Start with your resume, not a generic job feed."
              : "Sign in to find opportunities that fit your resume."}
          </p>
          <Notice tone="error">{error}</Notice>
          <Notice>{message}</Notice>
          <form onSubmit={submit} key={register ? "register" : "login"}>
            {register && (
              <label>
                Full name
                <input
                  name="name"
                  autoComplete="name"
                  required
                  maxLength={100}
                />
              </label>
            )}
            <label>
              Email address
              <input name="email" type="email" autoComplete="email" required />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                autoComplete={register ? "new-password" : "current-password"}
                minLength={8}
                maxLength={128}
                required
              />
            </label>
            {register && (
              <small>
                At least 8 characters, with uppercase, lowercase and a number.
              </small>
            )}
            <button className="primary wide" disabled={busy}>
              {busy ? "Please wait…" : register ? "Create account" : "Sign in"}{" "}
              <span>↗</span>
            </button>
          </form>
          <p className="auth-switch">
            {register ? "Already have an account?" : "New to SkillSync?"}{" "}
            <button
              className="text-button"
              onClick={() => {
                setRegister(!register);
                setError("");
                setMessage("");
              }}
            >
              {register ? "Sign in" : "Create account"}
            </button>
          </p>
          <small className="muted">
            Account-recovery email is not available in this version.
          </small>
        </section>
      </main>
      <footer>
        SkillSync · Focused on resume-to-job matching <BuildIdentifier />
      </footer>
    </div>
  );
}

const ResumeEvidence = memo(function ResumeEvidence({ analysis }) {
  const profile = analysis.profile;
  return (
    <div className="evidence">
      <div className="section-label">EXTRACTED FROM THIS RESUME</div>
      <h3>{profile.name || "Name not detected"}</h3>
      <p className="muted small">
        {profile.personal_info?.email || "Email not detected"}
        {profile.personal_info?.location
          ? ` · ${profile.personal_info.location}`
          : ""}
      </p>
      <div className="skill-pills">
        {(profile.technical_skills || []).map((skill) => (
          <span key={skill.name} title={skill.evidence}>
            {skill.name}
          </span>
        ))}
      </div>
      <div className="fact">
        <span>Experience</span>
        <strong>
          {profile.experience_years == null
            ? "Not determined"
            : `${profile.experience_years} years`}
        </strong>
      </div>
      <small className="muted">
        {profile.experience_method === "estimated_from_month_ranges"
          ? "Estimated from dated experience entries; overlapping dates are merged."
          : "Only explicit resume evidence is used. Missing details are not invented."}
      </small>
      {profile.education_text && (
        <details>
          <summary>Education evidence</summary>
          <p className="prewrap small">{profile.education_text}</p>
        </details>
      )}
      {profile.experience_text && (
        <details>
          <summary>Experience evidence</summary>
          <p className="prewrap small">{profile.experience_text}</p>
        </details>
      )}
      <details>
        <summary>Review extracted text</summary>
        <p className="prewrap raw-text">{profile.raw_text}</p>
      </details>
      {(profile.warnings || []).map((warning) => (
        <p className="muted small" key={warning}>
          {warning}
        </p>
      ))}
    </div>
  );
});

const JobCard = memo(function JobCard({ job, rank, onDetails }) {
  const [explanationOpen, setExplanationOpen] = useState(false);
  const url = safeLink(job.application_url);
  return (
    <article className="job-card screenshot-job-card">
      <div className="screenshot-job-header">
        <h3>{job.title}</h3>
        <span className="rank" aria-label={`Result ${rank}`}>
          {String(rank).padStart(2, "0")}
        </span>
      </div>
      <p className="screenshot-company">
        ▦ <span>{job.company || "Company not supplied"}</span>
      </p>
      <div className="screenshot-job-meta">
        <p>
          ⌖ <span>{job.location || "Location not supplied"}</span>
        </p>
        <p>
          ▣{" "}
          <span>
            {job.contract_time?.replaceAll("_", " ") ||
              "Working hours not supplied"}
          </span>
        </p>
      </div>
      <p className="salary">{formatSalary(job)}</p>
      <div className="screenshot-score-row">
        <span className="muted small">
          Posted{" "}
          {job.posted_at
            ? new Date(job.posted_at).toLocaleDateString()
            : "date unavailable"}
        </span>
        <strong className="match-percentage">{job.match_score}%</strong>
        <span className="match-badge">Match</span>
        <span className="muted small">{job.match_label}</span>
      </div>
      <div className="screenshot-description">
        <p className="job-snippet">
          {job.description || "No description supplied by Adzuna."}
        </p>
      </div>
      <SkillSummary job={job} />
      <details
        className="match-details"
        onToggle={(event) => setExplanationOpen(event.currentTarget.open)}
      >
        <summary>
          Why this match? <span>View evidence + score breakdown</span>
        </summary>
        {explanationOpen && (
          <>
            <div className="comparison-list">
              {job.comparisons.map((row) => (
                <div className="comparison" key={row.skill}>
                  <strong>
                    {row.skill}{" "}
                    <small>
                      ·{" "}
                      {row.requirement_type === "mentioned"
                        ? "mentioned, not an explicit requirement"
                        : row.requirement_type}
                    </small>
                  </strong>
                  <p>Job: “{row.job_evidence}”</p>
                  <p>
                    Resume:{" "}
                    {row.found_in_resume
                      ? `“${row.resume_evidence}”`
                      : "Not found in this resume — not proof that you lack this skill."}
                  </p>
                </div>
              ))}
            </div>
            <div className="breakdown">
              {job.score_breakdown.map((row) => (
                <div className="fact" key={row.signal}>
                  <span>{row.signal.replaceAll("_", " ")}</span>
                  <span>
                    {row.score}% × {Math.round(row.weight * 100)}% weight ={" "}
                    <b>{row.contribution} pts</b>
                  </span>
                </div>
              ))}
            </div>
            {job.warnings.map((warning) => (
              <p className="muted small" key={warning}>
                {warning}
              </p>
            ))}
          </>
        )}
      </details>
      <div className="job-bottom screenshot-card-actions">
        <button
          type="button"
          className="screenshot-details-button"
          aria-haspopup="dialog"
          onClick={() => onDetails(job)}
        >
          Details
        </button>
        {url ? (
          <a
            className="screenshot-apply-button"
            href={url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Apply ↗
          </a>
        ) : (
          <span className="screenshot-link-unavailable">
            Application link unavailable
          </span>
        )}
      </div>
    </article>
  );
});

function Workspace({ user, onLogout }) {
  const [resumes, setResumes] = useState([]);
  const [section, setSection] = useState(() =>
    window.location.hash === "#resume-analysis" ||
    window.location.pathname.includes("/resume-analysis")
      ? "resume-analysis"
      : "job-matching",
  );
  function changeSection(next) {
    setSection(next);
    setResults((previous) =>
      previous && !previous.from_saved_search
        ? { ...previous, from_saved_search: true }
        : previous,
    );
    window.history.replaceState(null, "", `#${next}`);
  }

  const [detailJob, setDetailJob] = useState(null);
  const [provider, setProvider] = useState(null);
  const [selectedId, setSelectedId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [savedResults, setResults] = useState(null);
  const [cache] = useState(() => createSessionCache());
  const [reloadVersion, setReloadVersion] = useState(0);
  const [loadedMatchId, setLoadedMatchId] = useState(null);
  const [visibleCount, setVisibleCount] = useState(20);
  const formEdited = useRef(false);
  const restoredSavedFilters = useRef(false);
  const defaultCountry = useRef("in");
  const searching = useRef(false);
  // Guard UI callbacks too: a fulfilled GET callback can still be queued when a mutation wins.
  const dataVersion = useRef({ analysis: 0, matches: 0 });
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [country, setCountry] = useState("in");
  const [limit, setLimit] = useState(50);
  const [maxDays, setMaxDays] = useState(30);
  const [busy, setBusy] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [minScore, setMinScore] = useState(0);
  const fileInput = useRef(null);
  const autoSearchId = useRef(null);
  const searchRef = useRef(null);
  const selected = resumes.find((resume) => String(resume.id) === selectedId);

  const selectedStatus = selected?.status;
  const results =
    savedResults?.resume_id === Number(selectedId) &&
    savedResults?.analysis_id === analysis?.id
      ? savedResults
      : null;
  const loadData = useCallback(
    (key, path) =>
      cache.load(
        key,
        async (signal) => (await apiClient.get(path, { signal })).data,
      ),
    [cache],
  );
  const restoreFields = useCallback((result) => {
    if (!result || formEdited.current) return;
    restoredSavedFilters.current = true;
    setQuery(result.query);
    setLocation(result.location);
    setCountry(result.country);
    setLimit(result.requested_limit);
    setMaxDays(result.max_days);
  }, []);
  const selectResume = useCallback(
    (id) => {
      dataVersion.current.analysis++;
      dataVersion.current.matches++;
      const value = id ? String(id) : "";
      const parsed = cache.peek(`analysis:${value}`)?.data;
      const previous = cache.peek(`matches:${value}`)?.data?.result;
      const valid = isEvidenceAnalysis(parsed);
      const saved =
        valid && previous?.analysis_id === parsed.id ? previous : null;
      formEdited.current = false;
      restoredSavedFilters.current = Boolean(saved);
      setError("");
      setDetailJob(null);
      setSelectedId(value);
      setMinScore(0);
      setVisibleCount(20);
      setAnalysis(valid ? parsed : null);
      setResults(saved ? { ...saved, from_saved_search: true } : null);
      setLoadedMatchId(cache.peek(`matches:${value}`) ? value : null);
      setQuery(saved?.query || parsed?.profile?.suggested_query || "");
      setLocation(saved?.location || "");
      if (saved) restoreFields(saved);
      else {
        setCountry(defaultCountry.current);
        setLimit(50);
        setMaxDays(30);
      }
    },
    [
      cache,
      restoreFields,
      setDetailJob,
      setSelectedId,
      setAnalysis,
      setResults,
    ],
  );
  useEffect(() => {
    let active = true;
    loadData("resumes", "/resumes/")
      .then((data) => {
        if (!active) return;
        setResumes(data);
        selectResume((data.find((resume) => resume.is_active) || data[0])?.id);
      })
      .catch((err) => {
        if (active && err.code !== "ERR_CANCELED") setError(errorMessage(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    // Provider status must not hold up the resume list or analysis.
    loadData("provider", "/jobs/status")
      .then((status) => {
        if (!active) return;
        setProvider(status);
        defaultCountry.current = status.country;
        if (!formEdited.current && !restoredSavedFilters.current)
          setCountry(status.country);
      })
      .catch((err) => {
        if (active && err.code !== "ERR_CANCELED") setError(errorMessage(err));
      });
    return () => {
      active = false;
      cache.clear();
    };
  }, [loadData, selectResume, cache]);

  useEffect(() => {
    let active = true;
    if (!selectedId || selectedStatus !== "COMPLETED")
      return () => {
        active = false;
      };
    const id = selectedId;
    const analysisVersion = dataVersion.current.analysis;
    const matchesVersion = dataVersion.current.matches;
    const analysisActive = () =>
      active && analysisVersion === dataVersion.current.analysis;
    const matchesActive = () =>
      active && matchesVersion === dataVersion.current.matches;
    // Independent requests: analysis can render while saved jobs are still loading.
    loadData(`analysis:${id}`, `/resumes/${id}/analysis`)
      .then((parsed) => {
        if (!analysisActive()) return;
        if (!isEvidenceAnalysis(parsed)) {
          setAnalysis(null);
          setResults(null);
          setError(
            "This resume uses the old parser. Select Analyse resume to extract fresh evidence before searching.",
          );
          return;
        }
        setAnalysis(parsed);
        const saved = cache.peek(`matches:${id}`)?.data?.result;
        if (saved?.analysis_id === parsed.id) restoreFields(saved);
        else if (!formEdited.current)
          setQuery(parsed.profile.suggested_query || "");
      })
      .catch((err) => {
        if (!analysisActive() || err.code === "ERR_CANCELED") return;
        if (err.response?.status === 404) {
          cache.invalidate(`analysis:${id}`);
          cache.invalidate(`matches:${id}`);
          setAnalysis(null);
          setResults(null);
        }
        setError(errorMessage(err));
      });
    loadData(`matches:${id}`, `/jobs/matches/${id}`)
      .then((saved) => {
        if (!matchesActive()) return;
        setResults(
          saved.result ? { ...saved.result, from_saved_search: true } : null,
        );
        const parsed = cache.peek(`analysis:${id}`)?.data;
        if (saved.result?.analysis_id === parsed?.id)
          restoreFields(saved.result);
      })
      .catch((err) => {
        if (matchesActive() && err.code !== "ERR_CANCELED") {
          if (err.response?.status === 404) setResults(null);
          setError(errorMessage(err));
        }
      })
      .finally(() => {
        if (matchesActive()) setLoadedMatchId(id);
      });
    return () => {
      active = false;
    };
  }, [
    selectedId,
    selectedStatus,
    reloadVersion,
    loadData,
    cache,
    restoreFields,
  ]);

  // Automatic first search after a new upload, using only extracted technical keywords.
  useEffect(() => {
    if (
      analysis &&
      autoSearchId.current === analysis.resume_id &&
      provider?.configured &&
      !busy
    ) {
      autoSearchId.current = null;
      if (analysis.profile.suggested_query) searchRef.current?.requestSubmit();
    }
  }, [analysis, provider, busy]);

  function invalidateResume(id) {
    dataVersion.current.analysis++;
    dataVersion.current.matches++;
    cache.invalidate(`analysis:${id}`);
    cache.invalidate(`matches:${id}`);
  }
  async function refreshResumes(id) {
    cache.invalidate("resumes");
    const data = await loadData("resumes", "/resumes/");
    setResumes(data);
    selectResume(
      data.some((row) => String(row.id) === String(id)) ? id : data[0]?.id,
    );
    setReloadVersion((value) => value + 1);
  }
  async function refreshSavedData() {
    setBusy("Refreshing saved resume data…");
    setError("");
    invalidateResume(selectedId);
    cache.invalidate("provider");
    try {
      await refreshResumes(selectedId);
      const status = await loadData("provider", "/jobs/status");
      defaultCountry.current = status.country;
      if (!formEdited.current && !restoredSavedFilters.current)
        setCountry(status.country);
      setProvider(status);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy("");
    }
  }
  async function upload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError("");
    if (
      !/\.(pdf|docx)$/i.test(file.name) ||
      file.size > 5 * 1024 * 1024 ||
      !file.size
    ) {
      setError("Choose a non-empty PDF or DOCX, up to 5 MB.");
      event.target.value = "";
      return;
    }
    let uploadedId;
    setBusy("Uploading resume…");
    try {
      const form = new FormData();
      form.append("file", file);
      const { data } = await apiClient.post("/resumes/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      uploadedId = data.id;
      setBusy("Extracting resume evidence…");
      await apiClient.post(`/resumes/${data.id}/analyze`, null, {
        timeout: 120_000,
      });
      autoSearchId.current = data.id;
      await refreshResumes(data.id);
    } catch (err) {
      setError(errorMessage(err));
      if (uploadedId) await refreshResumes(uploadedId).catch(() => {});
    } finally {
      setBusy("");
      event.target.value = "";
    }
  }
  async function analyseAgain() {
    setBusy("Extracting resume evidence…");
    setError("");
    try {
      await apiClient.post(`/resumes/${selectedId}/analyze`, null, {
        timeout: 120_000,
      });
      invalidateResume(selectedId);
      await refreshResumes(selectedId);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy("");
    }
  }
  async function removeResume() {
    if (!window.confirm("Delete this resume and its saved job matches?"))
      return;
    setBusy("Deleting resume…");
    setError("");
    try {
      await apiClient.delete(`/resumes/${selectedId}`);
      invalidateResume(selectedId);
      await refreshResumes();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy("");
    }
  }
  async function search(event) {
    event.preventDefault();
    if (
      !analysis ||
      analysis.resume_id !== Number(selectedId) ||
      searching.current
    )
      return;
    searching.current = true;
    setBusy("Fetching current jobs and comparing your resume…");
    setError("");
    setResults((previous) =>
      previous ? { ...previous, from_saved_search: true } : null,
    );
    setMinScore(0);
    setVisibleCount(20);
    try {
      const { data } = await apiClient.post(
        "/jobs/search",
        {
          resume_id: Number(selectedId),
          query,
          location,
          country,
          limit,
          max_days: maxDays,
        },
        { timeout: 120_000 },
      );
      dataVersion.current.matches++;
      cache.put(`matches:${selectedId}`, {
        result: { ...data, from_saved_search: true },
      });
      setResults(data);
      setLoadedMatchId(selectedId);
    } catch (err) {
      setError(
        `${errorMessage(err)}${results ? " Previous saved results are still shown below; no fresh results were received." : ""}`,
      );
    } finally {
      searching.current = false;
      setBusy("");
    }
  }
  const currentAnalysis =
    analysis?.resume_id === Number(selectedId) && isEvidenceAnalysis(analysis);
  const visibleJobs = useMemo(
    () => results?.jobs.filter((job) => job.match_score >= minScore) || [],
    [results, minScore],
  );
  const loadingAnalysis = selectedStatus === "COMPLETED" && !analysis && !error;
  const loadingMatches =
    currentAnalysis && loadedMatchId !== selectedId && !results && !error;
  return (
    <>
      <header className="topbar">
        <Brand onHome={() => changeSection("job-matching")} />
        <div className="header-right">
          <span className="user-name">{user.full_name || user.email}</span>
          <button
            className="secondary small-button"
            disabled={!!busy}
            onClick={() => {
              cache.clear();
              onLogout();
            }}
          >
            Sign out
          </button>
        </div>
      </header>
      <main className="workspace">
        <div className="page-heading">
          <div>
            <span className="eyebrow">YOUR NEXT OPPORTUNITY</span>
            <h1>
              Find your next <em>match.</em>
            </h1>
            <p className="muted">
              One resume. Current openings. A clear reason behind every result.
            </p>
          </div>
          <span
            className={`provider-badge ${provider?.configured ? "ready" : ""}`}
          >
            <i />
            {provider?.configured
              ? "Adzuna configured"
              : "Adzuna setup required"}
          </span>
        </div>
        <Notice tone="error">{error}</Notice>
        {provider && !provider.configured && (
          <Notice>
            Live search needs your Adzuna app ID and API key in the backend .env
            file. Resume extraction still works. No demo vacancies are shown.
          </Notice>
        )}
        {provider?.provider === "test_fixture" && (
          <Notice tone="warning">
            TEST FIXTURES — this test server does not show live vacancies.
          </Notice>
        )}
        {busy && (
          <Notice>
            <span className="spinner" /> {busy}
          </Notice>
        )}
        <nav className="workspace-sections" aria-label="Workspace sections">
          <button
            type="button"
            className={section === "resume-analysis" ? "active" : ""}
            aria-current={section === "resume-analysis" ? "page" : undefined}
            onClick={() => changeSection("resume-analysis")}
          >
            Resume analysis
          </button>
          <button
            type="button"
            className={section === "job-matching" ? "active" : ""}
            aria-current={section === "job-matching" ? "page" : undefined}
            onClick={() => changeSection("job-matching")}
          >
            Job matching
          </button>
        </nav>
        <div className="workspace-grid">
          <aside className="resume-panel">
            <div className="panel-heading">
              <span className="step-dot">1</span>
              <h2>Your resume</h2>
            </div>
            <p className="muted small">
              The selected document is the only evidence used for matching.
            </p>
            <input
              ref={fileInput}
              className="file-input"
              type="file"
              accept=".pdf,.docx"
              aria-label="Upload resume file"
              onChange={upload}
              disabled={!!busy}
            />
            <button
              className="upload-zone"
              onClick={() => fileInput.current?.click()}
              disabled={!!busy}
            >
              <span className="upload-icon">↑</span>
              <strong>Upload a resume</strong>
              <span>PDF or DOCX · Up to 5 MB</span>
            </button>
            {resumes.length > 0 && (
              <>
                <label className="resume-select">
                  Selected resume
                  <select
                    aria-label="Selected resume"
                    value={selectedId}
                    onChange={(event) => selectResume(event.target.value)}
                    disabled={!!busy}
                  >
                    {resumes.map((resume) => (
                      <option key={resume.id} value={resume.id}>
                        {resume.filename} · {resume.status.toLowerCase()}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="resume-actions">
                  <button
                    className="text-button"
                    disabled={!!busy}
                    onClick={refreshSavedData}
                  >
                    Refresh saved data
                  </button>
                  {(!currentAnalysis || selected?.status !== "COMPLETED") && (
                    <button
                      className="secondary small-button"
                      disabled={!!busy}
                      onClick={analyseAgain}
                    >
                      Analyse resume
                    </button>
                  )}
                  <button
                    className="text-button danger"
                    disabled={!!busy}
                    onClick={removeResume}
                  >
                    Delete resume
                  </button>
                </div>
              </>
            )}
            {loadingAnalysis && (
              <Notice>
                <span className="spinner" /> Loading resume analysis…
              </Notice>
            )}
            {analysis && section === "job-matching" && (
              <ResumeEvidence analysis={analysis} />
            )}
            {!analysis && !resumes.length && (
              <div className="empty-resume">
                <span>◈</span>
                <p>Your detected skills and experience will appear here.</p>
                <small>
                  We do not send the resume to Adzuna or an external AI service.
                </small>
              </div>
            )}
          </aside>
          <section className="results-column">
            <div hidden={section !== "resume-analysis"}>
              <ResumeAnalysisPanel analysis={analysis}>
                {analysis && <ResumeEvidence analysis={analysis} />}
              </ResumeAnalysisPanel>
              {loadingAnalysis && <Notice>Loading resume analysis…</Notice>}
            </div>
            <div hidden={section !== "job-matching"}>
              <div className="search-panel">
                <div className="panel-heading">
                  <span className="step-dot">2</span>
                  <h2>Find current openings</h2>
                </div>
                <form
                  ref={searchRef}
                  onChange={() => {
                    formEdited.current = true;
                  }}
                  onSubmit={search}
                >
                  <div className="search-primary">
                    <label>
                      Job title or keywords
                      <input
                        aria-label="Job title or keywords"
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder="e.g. Python developer"
                        maxLength={120}
                        disabled={!!busy}
                        required
                      />
                    </label>
                    <label>
                      <span>
                        Location <small>optional</small>
                      </span>
                      <input
                        aria-label="Location"
                        value={location}
                        onChange={(event) => setLocation(event.target.value)}
                        placeholder="City or region"
                        maxLength={120}
                        disabled={!!busy}
                      />
                    </label>
                  </div>
                  <div className="search-secondary">
                    <label>
                      Country
                      <select
                        value={country}
                        onChange={(event) => setCountry(event.target.value)}
                        disabled={!!busy}
                      >
                        {Object.entries(
                          provider?.countries || { in: "India" },
                        ).map(([code, name]) => (
                          <option value={code} key={code}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Posted within
                      <select
                        value={maxDays}
                        onChange={(event) =>
                          setMaxDays(Number(event.target.value))
                        }
                        disabled={!!busy}
                      >
                        <option value={7}>7 days</option>
                        <option value={30}>30 days</option>
                        <option value={90}>90 days</option>
                      </select>
                    </label>
                    <label>
                      Jobs to compare
                      <select
                        value={limit}
                        onChange={(event) =>
                          setLimit(Number(event.target.value))
                        }
                        disabled={!!busy}
                      >
                        <option value={20}>Up to 20</option>
                        <option value={50}>Up to 50</option>
                        <option value={100}>Up to 100</option>
                      </select>
                    </label>
                    <button
                      className="primary search-button"
                      disabled={
                        !currentAnalysis ||
                        !provider?.configured ||
                        !!busy ||
                        loading
                      }
                    >
                      {busy.startsWith("Fetching")
                        ? "Matching…"
                        : "Find matches"}{" "}
                      <span>↗</span>
                    </button>
                  </div>
                </form>
                <small className="muted">
                  The suggested query comes from extracted skills and is
                  editable. All fetched jobs are scored together, then ranked.
                </small>
              </div>
              {results ? (
                <>
                  <div className="results-heading">
                    <div>
                      <span className="eyebrow">3 · YOUR SHORTLIST</span>
                      <h2>{results.scored_count} jobs compared</h2>
                      <p className="muted small">
                        {results.from_saved_search
                          ? "Saved search"
                          : results.provider === "adzuna"
                            ? "Fetched from Adzuna"
                            : "Test fixtures — not live"}{" "}
                        · {formattedDate(results.fetched_at)}
                      </p>
                    </div>
                    <label className="score-filter">
                      Minimum score
                      <select
                        value={minScore}
                        onChange={(event) => (
                          setMinScore(Number(event.target.value)),
                          setVisibleCount(20)
                        )}
                      >
                        <option value={0}>Show all</option>
                        <option value={45}>45+</option>
                        <option value={75}>75+</option>
                      </select>
                    </label>
                  </div>
                  <p className="muted small">
                    Results for “{results.query}”
                    {results.location ? ` · ${results.location}` : ""}. Showing{" "}
                    {Math.min(visibleCount, visibleJobs.length)} of{" "}
                    {visibleJobs.length} matches.
                  </p>
                  <p className="scope-note">
                    {results.score_notice} We fetched {results.fetched_count}{" "}
                    listings for this query
                    {results.skipped_count
                      ? ` and excluded ${results.skipped_count} duplicate, outdated or invalid listings`
                      : ""}
                    . This is not the entire job market.
                  </p>
                  {results.from_saved_search && (
                    <Notice>
                      These are saved results, not a live availability check.
                      Use Find matches to fetch a fresh set.
                    </Notice>
                  )}
                  {visibleJobs.length ? (
                    visibleJobs
                      .slice(0, visibleCount)
                      .map((job, index) => (
                        <JobCard
                          key={job.id}
                          job={job}
                          rank={index + 1}
                          onDetails={setDetailJob}
                        />
                      ))
                  ) : (
                    <div className="empty-state">
                      <span>⌕</span>
                      <h3>
                        {results.jobs.length
                          ? "No results meet this score filter"
                          : "No current results for this search"}
                      </h3>
                      <p>
                        Try another keyword, nearby city or a broader date
                        range. No results is different from a provider error.
                      </p>
                    </div>
                  )}
                  {visibleJobs.length > visibleCount && (
                    <button
                      type="button"
                      className="secondary show-more-jobs"
                      onClick={() => setVisibleCount((count) => count + 20)}
                    >
                      Show next{" "}
                      {Math.min(20, visibleJobs.length - visibleCount)} jobs
                    </button>
                  )}
                  <p className="adzuna-credit">
                    Job advertisements supplied by{" "}
                    <a
                      href="https://www.adzuna.com"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Adzuna ↗
                    </a>
                    . Check the full listing before applying.
                  </p>
                </>
              ) : (
                <div className="empty-state">
                  <span>⌕</span>
                  <h2>
                    {loading || loadingMatches
                      ? "Loading your saved data…"
                      : busy
                        ? "Working on your next step"
                        : "Your shortlist starts here"}
                  </h2>
                  <p>
                    Upload a readable resume, review its extracted evidence,
                    then find current Adzuna openings. Scores explain overlap,
                    not a guaranteed offer.
                  </p>
                  <div className="empty-steps">
                    <span>RESUME EVIDENCE</span>
                    <b>→</b>
                    <span>CURRENT JOBS</span>
                    <b>→</b>
                    <span>RANKED MATCHES</span>
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
      <JobDetails
        job={detailJob}
        resumeName={results?.resume_filename}
        onClose={() => setDetailJob(null)}
      />
      <footer>
        SkillSync · Your resume, matched with evidence{" "}
        <span>No invented skills. No guaranteed “perfect” matches.</span>
        <BuildIdentifier />
      </footer>
    </>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(() => Boolean(getAccessToken()));
  useEffect(() => {
    let active = true;
    if (!getAccessToken()) return;
    apiClient
      .get("/auth/me")
      .then(({ data }) => {
        if (active) setUser(data);
      })
      .catch(() => {
        if (active) clearAuthTokens();
      })
      .finally(() => {
        if (active) setChecking(false);
      });
    return () => {
      active = false;
    };
  }, []);
  async function logout() {
    try {
      if (getRefreshToken())
        await apiClient.post("/auth/logout", {
          refresh_token: getRefreshToken(),
        });
    } finally {
      clearAuthTokens();
      setUser(null);
    }
  }
  if (checking)
    return (
      <div className="loading-screen">
        <Brand />
        <p>Opening your workspace…</p>
      </div>
    );
  return user ? (
    <Workspace
      key={user.id}
      user={user}
      onLogout={() => logout().catch(() => {})}
    />
  ) : (
    <Authentication onLogin={setUser} />
  );
}
