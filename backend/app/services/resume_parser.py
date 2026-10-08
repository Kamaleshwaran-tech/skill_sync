"""Local, evidence-based PDF/DOCX extraction. Missing values stay missing."""

import re
from pathlib import Path
import pymupdf
from docx import Document
from app.services.evidence import experience_years, skill_evidence, safe_url

HEADINGS = {
    "professional summary": "summary",
    "summary": "summary",
    "objective": "summary",
    "education": "education",
    "educational qualifications": "education",
    "professional experience": "experience",
    "work experience": "experience",
    "employment history": "experience",
    "experience": "experience",
    "technical skills": "skills",
    "skills": "skills",
    "projects": "projects",
    "certificates": "certifications",
    "certifications": "certifications",
    "contact": "contact",
}


class ResumeParser:
    def extract_text_from_pdf(self, path):
        with pymupdf.open(path) as document:
            if document.needs_pass:
                raise ValueError("Password-protected PDFs are not supported.")
            if len(document) > 30:
                raise ValueError("Resume exceeds the 30-page limit.")
            return "\n".join(page.get_text(sort=True) for page in document)

    def extract_text_from_docx(self, path):
        document = Document(path)
        paragraphs = [p.text for p in document.paragraphs]

        # Tables often contain the entire resume; the original parser ignored them.
        def table_text(table):
            rows = []
            for row in table.rows:
                for cell in row.cells:
                    rows.extend(p.text for p in cell.paragraphs)
                    for nested in cell.tables:
                        rows.extend(table_text(nested))
            return rows

        for table in document.tables:
            paragraphs.extend(table_text(table))
        for section in document.sections:
            paragraphs.extend(p.text for p in section.header.paragraphs)
            paragraphs.extend(p.text for p in section.footer.paragraphs)
        return "\n".join(dict.fromkeys(p.strip() for p in paragraphs if p.strip()))

    def extract(self, path):
        text = (
            self.extract_text_from_pdf(path)
            if Path(path).suffix.lower() == ".pdf"
            else self.extract_text_from_docx(path)
        )
        return self.extract_structured(text)

    def extract_structured(self, text):
        text = re.sub(r"[ \t]+", " ", text.replace("\r", "\n")).strip()
        if len(re.sub(r"\s+", "", text)) < 40:
            raise ValueError(
                "Too little readable text. Use a text-based PDF or DOCX; scanned PDFs require OCR, which is not included."
            )
        if len(text) > 100_000:
            raise ValueError("Resume text exceeds the 100,000-character limit.")
        sections = {}
        current = "other"
        headings = "|".join(
            re.escape(h) for h in sorted(HEADINGS, key=len, reverse=True)
        )
        for line in text.splitlines():
            match = re.match(rf"^\s*({headings})\s*(?::\s*(.*))?$", line, re.I)
            if match:
                current = HEADINGS[match.group(1).lower()]
                if match.group(2):
                    sections.setdefault(current, []).append(match.group(2))
            else:
                sections.setdefault(current, []).append(line)
        sections = {
            k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()
        }
        evidence = skill_evidence(text)
        emails = list(
            dict.fromkeys(re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text))
        )
        phones = re.finditer(
            r"(?:\+\d{1,3}[ -]?)?(?:\(?\d{3,5}\)?[ -]?){2,3}\d{3,5}", text
        )
        phone_value = next(
            (
                p.group(0).strip()
                for p in phones
                if 10 <= len(re.sub(r"\D", "", p.group(0))) <= 15
            ),
            None,
        )
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = (
            lines[0]
            if len(lines[0].split()) in range(2, 6)
            and not re.search(r"[@:/\d]", lines[0])
            and lines[0].lower() not in HEADINGS
            else None
        )
        location = re.search(r"^Location\s*:\s*([^\n]+)", text, re.I | re.M)
        linkedin = re.search(
            r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", text, re.I
        )
        years, years_evidence, years_method = experience_years(
            text, sections.get("experience", "")
        )
        # An inferred search suggestion is editable and is not a verified job title.
        preference = [
            "Python",
            "JavaScript",
            "TypeScript",
            "Java",
            "C#",
            "C++",
            "PHP",
            "Go",
            "Ruby",
            "SQL",
            "Excel",
        ]
        primary = next(
            (s for s in preference if s in evidence), next(iter(evidence), "")
        )
        suggestion = (
            f"{primary} developer"
            if primary and primary not in {"SQL", "Excel"}
            else f"{primary} analyst"
            if primary
            else ""
        )
        warnings = [
            "Local rule-based extraction; review the detected fields before searching."
        ]
        if not evidence:
            warnings.append(
                "No skills in the current taxonomy were detected; enter a job title or keyword to search. Matching will rely on text overlap."
            )
        if years is None:
            warnings.append(
                "Experience duration could not be determined; it will not receive invented points."
            )
        return {
            "confidence": None,
            "profile": {
                "parser_version": "evidence-v1",
                "name": name,
                "personal_info": {
                    "email": emails[0] if emails else None,
                    "phone": phone_value,
                    "location": location.group(1).strip() if location else None,
                    "linkedin": safe_url(
                        "https://"
                        + linkedin.group(0)
                        .removeprefix("https://")
                        .removeprefix("http://")
                    )
                    if linkedin
                    else None,
                },
                "technical_skills": [
                    {"name": name, "evidence": snippet}
                    for name, snippet in sorted(evidence.items())
                ],
                "experience_years": years,
                "experience_method": years_method,
                "experience_evidence": years_evidence,
                "education_text": sections.get("education"),
                "experience_text": sections.get("experience"),
                "projects_text": sections.get("projects"),
                "summary": sections.get("summary"),
                "suggested_query": suggestion,
                "sections": sections,
                "raw_text": text,
                "warnings": warnings,
            },
        }
