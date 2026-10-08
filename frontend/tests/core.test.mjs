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
