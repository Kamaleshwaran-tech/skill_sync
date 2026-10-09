import { safeLink } from "../../../core";
import { ResumeScoreCard } from "./ResumeScoreCard";

export default function ResumeAnalysisPanel({ analysis, children }) {
  if (!analysis)
    return (
      <section className="empty-state">
        <h2>Resume analysis</h2>
        <p>Select and analyse a resume to view its extracted information.</p>
      </section>
    );
  const profile = analysis.profile;
  const info = profile.personal_info || {};
  const fields = [
    ["Email", info.email, "✉"],
    ["Phone", info.phone, "☎"],
    ["Location", info.location, "⌖"],
    ["LinkedIn", info.linkedin, "↗"],
    ["Portfolio", info.portfolio, "↗"],
  ];
  return (
    <div className="resume-analysis-page">
      <section className="personal-info-card">
        <h2>Extracted personal information</h2>
        <div className="personal-info-grid">
          {fields.map(([label, value, icon]) => (
            <div className="personal-info-item" key={label}>
              <span className="personal-info-icon" aria-hidden="true">
                {icon}
              </span>
              <div>
                <span className="small">{label}</span>
                <p>
                  {(label === "LinkedIn" || label === "Portfolio") &&
                  safeLink(value) ? (
                    <a
                      href={safeLink(value)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {value}
                    </a>
                  ) : (
                    value || "Not detected"
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <div className="resume-analysis-grid">
        <ResumeScoreCard
          score={analysis.quality_score ?? profile.resume_quality_score}
        />
        <section className="analysis-evidence-card">{children}</section>
      </div>
    </div>
  );
}
