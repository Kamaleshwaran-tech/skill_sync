import { normaliseResumeScore } from "../src/core.js";
import { getSkillSummary } from "../src/core.js";
import test from "node:test";
import assert from "node:assert/strict";
import {
  safeLink,
  formatSalary,
  errorMessage,
  formattedDate,
  isEvidenceAnalysis,
} from "../src/core.js";
test("unsafe application URLs are not executable", () => {
  for (const value of [
    "javascript:alert(1)",
    "data:text/html,hi",
    "https://user:pass@example.com",
    null,
  ])
    assert.equal(safeLink(value), null);
  assert.equal(
    safeLink("https://www.adzuna.in/jobs/land/ad/123"),
    "https://www.adzuna.in/jobs/land/ad/123",
  );
});
test("missing salary stays unknown and INR is not displayed as dollars", () => {
  assert.equal(
    formatSalary({ salary_min: null, salary_max: null }),
    "Salary not supplied",
  );
  assert.match(
    formatSalary({
      salary_min: 500000,
      salary_max: null,
      salary_currency: "INR",
    }),
    /₹|INR/,
  );
  assert.match(
    formatSalary({
      salary_min: 0,
      salary_max: 40000,
      salary_currency: "GBP",
      salary_is_predicted: true,
    }),
    /Adzuna estimate/,
  );
});
test("structured provider failures are visible instead of empty-job success", () => {
  assert.equal(
    errorMessage({
      response: {
        data: {
          detail: {
            code: "provider_authentication",
            message: "Check server credentials",
          },
        },
      },
    }),
    "Check server credentials",
  );
});
test("unknown job dates are not called recently posted", () => {
  assert.equal(formattedDate(null), "Date not supplied");
  assert.equal(formattedDate("invalid"), "Date not supplied");
});

test("legacy guessed analyses cannot be treated as evidence", () => {
  assert.equal(
    isEvidenceAnalysis({ profile: { name: "Old guessed name" } }),
    false,
  );
  assert.equal(isEvidenceAnalysis(null), false);
  assert.equal(
    isEvidenceAnalysis({ profile: { parser_version: "evidence-v1" } }),
    true,
  );
});

test("missing skills include comparison evidence even when summary is absent", () => {
  assert.deepEqual(
    getSkillSummary({
      comparisons: [
        { skill: "Python", found_in_resume: true },
        { skill: "Docker", found_in_resume: false },
      ],
    }),
    { matched: ["Python"], missing: ["Docker"] },
  );
});
test("skill summaries retain all missing skills without duplication", () => {
  assert.deepEqual(
    getSkillSummary({
      missing_skills: ["Docker", " SQL ", "Docker", null],
      comparisons: [{ skill: "Docker", found_in_resume: false }],
    }).missing,
    ["Docker", "SQL"],
  );
});
test("unknown skill evidence is not invented as a match or a gap", () => {
  assert.deepEqual(getSkillSummary(), { matched: [], missing: [] });
  assert.deepEqual(
    getSkillSummary({
      missing_skills: "Python",
      comparisons: [null, { skill: "Java" }],
    }),
    { matched: [], missing: [] },
  );
});

test("resume gauge uses only an explicit valid score, never a made-up default", () => {
  for (const value of [null, undefined, "", NaN, Infinity, -1, 101, "92"])
    assert.equal(normaliseResumeScore(value), null);
  for (const value of [0, 92, 100])
    assert.equal(normaliseResumeScore(value), value);
});
