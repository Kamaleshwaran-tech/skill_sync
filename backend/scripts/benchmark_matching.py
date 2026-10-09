"""Reproducible synthetic CPU benchmark; no network, database, or private resumes.
Run: python backend/scripts/benchmark_matching.py [--runs 5] [--output ranking.json]
Compare medians on the same machine. This does not measure live Adzuna latency.
"""

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.job_matching import rank_jobs

# SHA256 of the complete baseline output from published commit bc8e470.
BASELINE_SHA256 = "0e5a84e7515067fad2834d08fcaa205025414bbf9f41aa7724df8678d12218fb"


def make_fixture():
    profile = {
        "name": "Synthetic Candidate",
        "raw_text": "Python SQL Docker APIs testing backend applications data software development. "
        * 300,
        "technical_skills": [
            {"name": s, "evidence": f"Skills: {s}"} for s in ["Python", "SQL", "Docker"]
        ],
        "experience_years": 3,
    }
    now = datetime(2026, 10, 9, tzinfo=timezone.utc)
    jobs = [
        {
            "id": str(i),
            "title": f"Python Developer {i}",
            "description": (
                "Required: Python, SQL. Preferred: Docker, AWS. Build applications with tested API integration. "
                + f"Project {i} documentation. "
            )
            * 4,
            "created": now.isoformat(),
            "location": {"display_name": "Chennai"},
        }
        for i in range(100)
    ]
    return profile, jobs, now


def canonical_output(result):
    return json.dumps(result, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.runs <= 100:
        parser.error("--runs must be between 1 and 100")
    profile, jobs, now = make_fixture()
    runs = []
    for _ in range(args.runs):
        start = time.perf_counter()
        result = rank_jobs(profile, jobs, "in", 30, now=now)
        runs.append(time.perf_counter() - start)
    output = canonical_output(result)
    digest = hashlib.sha256(output.encode()).hexdigest()
    print(
        json.dumps(
            {
                "fixture": "Synthetic 100 jobs; no provider/network",
                "median_seconds": statistics.median(runs),
                "runs": runs,
                "baseline_output_identical": digest == BASELINE_SHA256,
                "output_sha256": digest,
            },
            indent=2,
        )
    )
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    if digest != BASELINE_SHA256:
        raise SystemExit(
            "Output changed from the baseline: review scoring/evidence changes."
        )


if __name__ == "__main__":
    main()
