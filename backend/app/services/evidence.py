"""Evidence-only text helpers shared by the parser and matcher. No LLM or network."""

from collections import Counter
from datetime import date
from html.parser import HTMLParser
import math
import re
from urllib.parse import urlsplit
from app.utils.skill_taxonomy import MASTER_SKILLS, VARIATIONS

EXTRA_SKILLS = [
    "Excel",
    "Power BI",
    "Tableau",
    "Pandas",
    "NumPy",
    "Accounting",
    "Bookkeeping",
    "Salesforce",
    "Figma",
    "Testing",
]
SOFT = {"Problem Solving", "Communication", "Leadership", "Teamwork"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        elif tag in {"p", "li", "br", "div", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        elif tag in {"p", "li", "div"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_text(value):
    if isinstance(value, dict):
        value = value.get("display_name") or value.get("name") or ""
    parser = _Text()
    parser.feed(str(value or ""))
    return "\n".join(
        re.sub(r"[ \t]+", " ", line).strip()
        for line in "".join(parser.parts).splitlines()
    ).strip()


def safe_url(value):
    value = str(value or "").strip()
    try:
        parsed = urlsplit(value)
        return (
            value
            if parsed.scheme in {"http", "https"}
            and parsed.hostname
            and not parsed.username
            else None
        )
    except ValueError:
        return None


def _negated_skill(text, match):
    # Conservative handling of explicit local negation, not general language understanding.
    before = re.split(r"[\n.;,!?]", text[max(0, match.start() - 90) : match.start()])[
        -1
    ]
    after = text[match.end() : match.end() + 55]
    prefix = r"\b(?:no(?: prior)?(?: (?:experience (?:in|with)|knowledge of|proficiency in))?|without|not(?: (?:proficient in|familiar with))?|lack(?:ing)?(?: (?:experience (?:in|with)|knowledge of))?|(?:have not|haven['’]t|never) used)\s*$"
    suffix = r"^\s*(?:(?:experience\s+)?(?:is\s+)?not\s+(?:required|known|used)|:\s*(?:none|no experience))\b"
    return bool(re.search(prefix, before, re.I) or re.match(suffix, after, re.I))


def _compile_skill_patterns():
    aliases = {s: s for s in [*MASTER_SKILLS, *EXTRA_SKILLS]}
    aliases.update(VARIATIONS)
    patterns = []
    for alias, canonical in aliases.items():
        if not alias or canonical in SOFT:
            continue
        if canonical in {"C", "R", "Go"} and alias.lower() == canonical.lower():
            alias = canonical
        flags = 0 if alias in {"C", "R", "Go"} else re.I
        patterns.append(
            (
                canonical,
                re.compile(r"(?<![\w+#])" + re.escape(alias) + r"(?![\w+#])", flags),
            )
        )
    return tuple(patterns)


SKILL_PATTERNS = _compile_skill_patterns()


def skill_evidence(text):
    found = {}
    for canonical, pattern in SKILL_PATTERNS:
        if canonical in found:
            continue
        match = next(
            (m for m in pattern.finditer(text) if not _negated_skill(text, m)),
            None,
        )
        if match and canonical not in found:
            start = max(text.rfind("\n", 0, match.start()) + 1, match.start() - 60)
            end = text.find("\n", match.end())
            found[canonical] = text[
                start : min(end if end >= 0 else len(text), match.end() + 100)
            ].strip()
    return found


DATE_TOKEN = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{1,2}/\d{4}"


def _month(value):
    if "/" in value:
        m, y = map(int, value.split("/"))
    else:
        month, year = value.split()
        m = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ].index(month[:3].lower()) + 1
        y = int(year)
    if not 1 <= m <= 12 or not 1950 <= y <= date.today().year + 1:
        raise ValueError("Invalid date")
    return y * 12 + m - 1


def experience_years(text, section=""):
    explicit = re.search(
        r"\b(\d{1,2}(?:\.\d+)?)(?:\s*(?:[-–—]|to)\s*\d{1,2}(?:\.\d+)?)?\+?\s+years?\s+(?:of\s+)?(?:professional\s+|relevant\s+|work\s+)?experience\b",
        text,
        re.I,
    )
    if explicit:
        return float(explicit.group(1)), explicit.group(0), "self_reported"
    intervals = []
    for match in re.finditer(
        f"({DATE_TOKEN})\\s*[-–—]\\s*({DATE_TOKEN}|Present|Current)", section, re.I
    ):
        try:
            start = _month(match.group(1))
            end = (
                date.today().year * 12 + date.today().month - 1
                if match.group(2).lower() in {"present", "current"}
                else _month(match.group(2))
            )
            if 0 < end - start <= 600:
                intervals.append(
                    (start, min(end, date.today().year * 12 + date.today().month - 1))
                )
        except ValueError:
            continue
    if intervals:
        merged = []
        for start, end in sorted(intervals):
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return (
            round(sum(b - a for a, b in merged) / 12, 2),
            section[:500],
            "estimated_from_month_ranges",
        )
    if re.search(r"\b(fresher|no (?:prior |work )?experience)\b", text, re.I):
        return 0.0, "Explicit fresher/no-experience statement", "self_reported"
    return None, None, "unknown"


def job_experience(text):
    matches = re.findall(
        r"\b(\d{1,2})(?:\s*(?:[-–—]|to)\s*\d{1,2})?\+?\s+years?\s+(?:of\s+)?(?:(?:relevant|professional|commercial|work|hands.on)\s+)?experience",
        text,
        re.I,
    )
    return max(map(float, matches)) if matches else None


STOP_WORDS = set(
    "the a an and or of in on to for with is are be as by at from we you your our will this that it have has job role company team candidate experience skills required preferred work working developer engineer".split()
)


def token_counts(text):
    return Counter(
        t
        for t in re.findall(r"[a-z0-9][a-z0-9+#.\-]*", text.lower())
        if len(t) > 1 and t not in STOP_WORDS
    )


def lexical_similarity(left, right):
    return similarity_from_counts(token_counts(left), token_counts(right))


def similarity_from_counts(left, right):
    # IDF remains pair-specific; only tokenization of the resume is reused.
    docs = [left, right]
    vectors = []
    for doc in docs:
        vectors.append(
            {
                term: (1 + math.log(count))
                * (1 + math.log(3 / (1 + sum(term in d for d in docs))))
                for term, count in doc.items()
            }
        )
    norms = [math.sqrt(sum(v * v for v in vector.values())) for vector in vectors]
    if not all(norms):
        return 0.0
    return min(
        1.0,
        sum(value * vectors[1].get(term, 0) for term, value in vectors[0].items())
        / (norms[0] * norms[1]),
    )
