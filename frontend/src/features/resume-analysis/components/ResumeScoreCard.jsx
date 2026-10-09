import { normaliseResumeScore } from "../../../core";

// The ring and its value share a fixed square. Parent grid/stack stretching
// cannot move the label relative to the ring (the old MUI wrapper could stretch).
export function ResumeScoreCard({ score }) {
  const value = normaliseResumeScore(score);
  return (
    <section className="resume-score-card" aria-label="Resume quality score">
      <div
        className="resume-score-ring"
        role="img"
        aria-label={
          value == null
            ? "Resume quality score not assessed"
            : `Resume quality score ${value} out of 100`
        }
        style={{
          width: 132,
          height: 132,
          position: "relative",
          marginInline: "auto",
          flexShrink: 0,
        }}
      >
        <svg
          width="132"
          height="132"
          viewBox="0 0 132 132"
          aria-hidden="true"
          style={{ display: "block", width: 132, height: 132 }}
        >
          <circle
            cx="66"
            cy="66"
            r="56"
            fill="none"
            stroke="#ededfa"
            strokeWidth="18"
          />
          {value != null && (
            <circle
              cx="66"
              cy="66"
              r="56"
              pathLength="100"
              fill="none"
              stroke="#514ef0"
              strokeWidth="18"
              strokeDasharray={`${value} 100`}
              transform="rotate(-90 66 66)"
            />
          )}
        </svg>
        <span
          className="resume-score-value"
          aria-hidden="true"
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            lineHeight: 1,
            margin: 0,
            textAlign: "center",
            whiteSpace: "nowrap",
          }}
        >
          {value ?? "—"}
        </span>
      </div>
      <h3>Resume quality score</h3>
      <p className="muted small">
        {value == null
          ? "Not assessed. The current parser does not supply a resume-quality rating."
          : "Score supplied by the analysis. Not a hiring probability."}
      </p>
    </section>
  );
}
