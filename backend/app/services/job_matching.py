"""One bounded, resume-specific search. Scores are overlap heuristics, not hiring probabilities."""

from datetime import datetime, timedelta, timezone
import math
import re
from functools import lru_cache
from app.services.evidence import (
    plain_text,
    safe_url,
    skill_evidence,
    job_experience,
    token_counts,
    similarity_from_counts,
)

CURRENCIES = {"in": "INR", "gb": "GBP", "us": "USD", "au": "AUD", "ca": "CAD"}
WEIGHTS = {
    "required_skills": 0.45,
    "preferred_skills": 0.10,
    "mentioned_skills": 0.10,
    "text_overlap": 0.25,
    "experience": 0.10,
}


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return (
            parsed.replace(tzinfo=timezone.utc)
            if parsed.tzinfo is None
            else parsed.astimezone(timezone.utc)
        )
    except (ValueError, TypeError):
        return None


def salary(value):
    try:
        result = float(value)
        return round(result, 2) if math.isfinite(result) and result >= 0 else None
    except (ValueError, TypeError):
        return None


def extract_requirements(title, description, evidence_lookup=None):
    evidence_lookup = evidence_lookup or skill_evidence
    groups = {"required": {}, "preferred": {}, "mentioned": {}}
    positive = set(evidence_lookup(title + "\n" + description))
    description = re.sub(
        r",(?=\s*[^,;:.]+?\s+(?:required|preferred|desirable)\b)",
        ";",
        description,
        flags=re.I,
    )
    description = re.sub(
        r"\b(required|preferred|desirable)\s+(?:and|but)\s+",
        r"\1;",
        description,
        flags=re.I,
    )
    for line in re.split(r"[\n;]|(?<=[.!?])\s+", title + "\n" + description):
        # Split explicit clauses, rather than labelling a whole paragraph "required".
        clauses = re.split(
            r"(?i)(?=\b(?:required|must have|preferred|nice.to.have|bonus|desirable)\b)",
            line,
        )
        for clause in clauses:
            kind = (
                "preferred"
                if re.search(
                    r"\b(preferred|nice.to.have|bonus|desirable|plus)\b", clause, re.I
                )
                else (
                    "required"
                    if re.search(r"\b(required|must|essential|minimum)\b", clause, re.I)
                    else "mentioned"
                )
            )
            groups[kind].update(evidence_lookup(clause))
    # Handle common suffix wording such as "Python required; Docker preferred".
    for line in re.split(r"[\n;]|(?<=[.!?])\s+", description):
        if re.search(r"\b(required|preferred|desirable)\s*[.!?]?\s*$", line, re.I):
            kind = (
                "required"
                if re.search(r"\brequired\s*[.!?]?\s*$", line, re.I)
                else "preferred"
            )
            groups[kind].update(evidence_lookup(line))
    for group in groups.values():
        for name in list(group):
            if name not in positive:
                group.pop(name)
    for name in list(groups["mentioned"]):
        if name in groups["required"] or name in groups["preferred"]:
            groups["mentioned"].pop(name)
    for name in list(groups["preferred"]):
        if name in groups["required"]:
            groups["preferred"].pop(name)
    return groups


def normalize_job(raw, country, evidence_lookup=None):
    external_id = str(raw.get("id") or "").strip()
    title = plain_text(raw.get("title"))
    if not external_id or not title:
        return None
    description = plain_text(raw.get("description"))[:15000]
    created = timestamp(raw.get("created"))
    expires = timestamp(raw.get("expires_at") or raw.get("expiry"))
    return {
        "id": external_id,
        "title": title[:255],
        "company": plain_text(raw.get("company")) or None,
        "location": plain_text(raw.get("location")) or None,
        "country": country,
        "description": description,
        "description_is_snippet": True,
        "posted_at": created.isoformat() if created else None,
        "expires_at": expires.isoformat() if expires else None,
        "application_url": safe_url(raw.get("redirect_url")),
        "salary_min": salary(raw.get("salary_min")),
        "salary_max": salary(raw.get("salary_max")),
        "salary_currency": CURRENCIES[country],
        "salary_is_predicted": str(raw.get("salary_is_predicted", "0")) == "1",
        "contract_time": (
            raw.get("contract_time")
            if raw.get("contract_time") in {"full_time", "part_time"}
            else None
        ),
        "contract_type": (
            raw.get("contract_type")
            if raw.get("contract_type") in {"permanent", "contract"}
            else None
        ),
        "requirements": extract_requirements(title, description, evidence_lookup),
        "experience_required_years": job_experience(description),
    }


def prepare_resume(profile):
    content = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "", profile.get("raw_text", ""))
    if profile.get("name"):
        content = content.replace(profile["name"], "")
    return {
        "skills": {
            s["name"]: s.get("evidence", "")
            for s in profile.get("technical_skills", [])
            if isinstance(s, dict) and s.get("name")
        },
        "tokens": token_counts(content),
    }


def score_job(profile, job, prepared=None):
    prepared = prepared if prepared is not None else prepare_resume(profile)
    resume_skills = prepared["skills"]
    signals = {}
    missing = []
    matched = []
    comparisons = []
    for kind in ["required", "preferred", "mentioned"]:
        requirements = job["requirements"][kind]
        if requirements:
            present = set(requirements) & set(resume_skills)
            signals[kind + "_skills"] = len(present) / len(requirements)
            for name, evidence in sorted(requirements.items()):
                found = name in resume_skills
                (matched if found else missing).append(name)
                comparisons.append(
                    {
                        "skill": name,
                        "requirement_type": kind,
                        "found_in_resume": found,
                        "resume_evidence": resume_skills.get(name),
                        "job_evidence": evidence,
                    }
                )
    if job["description"].strip():
        signals["text_overlap"] = similarity_from_counts(
            prepared["tokens"], token_counts(job["title"] + " " + job["description"])
        )
    expected = job["experience_required_years"]
    actual = profile.get("experience_years")
    if expected is not None and actual is not None and expected > 0:
        signals["experience"] = min(1.0, max(0.0, actual / expected))
    weight_sum = sum(WEIGHTS[key] for key in signals)
    breakdown = (
        [
            {
                "signal": key,
                "score": round(value * 100, 1),
                "weight": round(WEIGHTS[key] / weight_sum, 4),
                "contribution": round(value * 100 * WEIGHTS[key] / weight_sum, 2),
            }
            for key, value in signals.items()
        ]
        if weight_sum
        else []
    )
    score = round(sum(row["contribution"] for row in breakdown), 1)
    score = max(0, min(100, score))
    warnings = [
        "Adzuna supplies a description snippet, not necessarily the full job requirements."
    ]
    if not comparisons:
        warnings.append(
            "No recognised skill requirements in this snippet; score is based on limited text/experience evidence."
        )
    if expected is None:
        warnings.append(
            "Experience requirement not stated in the snippet; no experience points awarded."
        )
    elif actual is None:
        warnings.append(
            "Resume experience duration is unknown; no experience points awarded."
        )
    elif actual < expected:
        warnings.append(
            f"Stated experience: job asks for {expected:g} years; resume indicates {actual:g} years."
        )
    reasons = []
    if matched:
        reasons.append("Resume evidence found for: " + ", ".join(sorted(set(matched))))
    if missing:
        reasons.append("Not found in this resume: " + ", ".join(sorted(set(missing))))
    band = (
        "Limited evidence"
        if not comparisons
        else (
            "Strong overlap"
            if score >= 75
            else "Partial overlap" if score >= 45 else "Limited overlap"
        )
    )
    public_job = {k: v for k, v in job.items() if k != "requirements"}
    return {
        **public_job,
        "match_score": score,
        "match_label": band,
        "matched_skills": sorted(set(matched)),
        "missing_skills": sorted(set(missing)),
        "comparisons": comparisons,
        "score_breakdown": breakdown,
        "reasons": reasons,
        "warnings": warnings,
        "resume_experience_years": actual,
    }


def rank_jobs(profile, raw_jobs, country, max_days, now=None):
    now = now or datetime.now(timezone.utc)
    seen = set()
    jobs = []
    skipped = 0
    prepared = prepare_resume(profile)
    # Bounded to this one search: no cross-user/query/resume cache.
    evidence_lookup = lru_cache(maxsize=256)(skill_evidence)
    for raw in raw_jobs:
        job = normalize_job(raw, country, evidence_lookup)
        if not job or job["id"] in seen:
            skipped += 1
            continue
        posted = timestamp(job["posted_at"])
        expired = timestamp(job["expires_at"])
        if (
            posted
            and (
                posted < now - timedelta(days=max_days)
                or posted > now + timedelta(days=1)
            )
        ) or (expired and expired <= now):
            skipped += 1
            continue
        seen.add(job["id"])
        jobs.append(score_job(profile, job, prepared))
    jobs.sort(
        key=lambda job: (
            -job["match_score"],
            -(
                timestamp(job["posted_at"]).timestamp()
                if timestamp(job["posted_at"])
                else 0
            ),
            job["id"],
        )
    )
    return jobs, skipped
