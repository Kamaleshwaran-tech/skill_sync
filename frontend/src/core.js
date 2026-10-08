export function errorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (detail?.message) return detail.message;
  if (error?.code === "ERR_NETWORK")
    return "Cannot reach the backend. Start the API and check its configuration.";
  return error?.message || "Something went wrong. Please try again.";
}
export function safeLink(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) && !url.username
      ? value
      : null;
  } catch {
    return null;
  }
}
export function formatSalary(job) {
  const values = [job.salary_min, job.salary_max].filter((value) =>
    Number.isFinite(value),
  );
  if (!values.length) return "Salary not supplied";
  const format = (value) =>
    new Intl.NumberFormat("en", {
      style: "currency",
      currency: job.salary_currency,
      maximumFractionDigits: 0,
    }).format(value);
  const salary =
    values.length === 2
      ? `${format(values[0])} – ${format(values[1])}`
      : job.salary_min != null
        ? `From ${format(values[0])}`
        : `Up to ${format(values[0])}`;
  return `${salary}${job.salary_is_predicted ? " · Adzuna estimate" : ""}`;
}
export function formattedDate(value) {
  return value && !Number.isNaN(Date.parse(value))
    ? new Date(value).toLocaleString()
    : "Date not supplied";
}

export function isEvidenceAnalysis(analysis) {
  return analysis?.profile?.parser_version === "evidence-v1";
}
