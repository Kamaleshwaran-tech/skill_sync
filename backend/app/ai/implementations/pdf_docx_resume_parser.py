from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional

from app.ai.interfaces.resume_parser import (
    EducationItem,
    ExperienceItem,
    ExtractedSkill,
    ParsedResume,
    ProjectItem,
    ResumeParserInterface,
)
from app.utils.skill_taxonomy import normalize_skill, MASTER_SKILLS, VARIATIONS

log = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import docx
except Exception:
    docx = None

try:
    import spacy
    from spacy.matcher import PhraseMatcher
    from spacy.lang.en import English
except Exception:
    spacy = None
    PhraseMatcher = None
    English = None

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{6,}\d)")

SOFT_SKILLS_TAXONOMY = {
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "adaptability", "collaboration",
    "work ethic", "creativity", "emotional intelligence", "conflict resolution",
    "negotiation", "decision making"
}


class PdfDocxResumeParser(ResumeParserInterface):
    """Resume parser using PyMuPDF, python-docx, and spaCy entity matching."""

    def __init__(self):
        self.nlp = None
        self.matcher = None
        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    self.nlp = English()
                    self.nlp.add_pipe("sentencizer")
                except Exception:
                    self.nlp = None
        if self.nlp and PhraseMatcher:
            self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            patterns = [self.nlp.make_doc(s) for s in MASTER_SKILLS]
            self.matcher.add("SKILL", patterns)

    def parse_file(self, file_path: str, file_type: str) -> ParsedResume:
        ftype = file_type.lower()
        if "pdf" in ftype:
            raw_text = self._extract_pdf(file_path)
        elif "doc" in ftype:
            raw_text = self._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported resume file format: {file_type}")

        return self.parse_text(raw_text)

    def parse_text(self, text: str) -> ParsedResume:
        cleaned = self._clean_text(text)
        sections = self._detect_sections(cleaned)
        emails = list(set(EMAIL_RE.findall(cleaned)))
        phones = list(set([re.sub(r"[^\d+]+", "", p) for p in PHONE_RE.findall(cleaned)]))
        name = self._extract_name(cleaned)

        tech_skills, soft_skills = self._extract_skills(cleaned)
        education = self._extract_education(sections.get("education", ""))
        projects = self._extract_projects(sections.get("projects", ""))
        experiences = self._extract_experiences(sections.get("experience", "") or sections.get("work experience", ""))

        confidence = min(0.95, 0.4 + 0.05 * (len(tech_skills) + len(soft_skills) + len(education) + len(projects)))

        return ParsedResume(
            name=name,
            emails=emails,
            phones=phones,
            technical_skills=tech_skills,
            soft_skills=soft_skills,
            education=education,
            projects=projects,
            experiences=experiences,
            sections=sections,
            raw_text=cleaned,
            confidence=round(confidence, 2),
        )

    def _extract_pdf(self, path: str) -> str:
        if not fitz:
            raise RuntimeError("PyMuPDF (fitz) is not installed")
        doc = fitz.open(path)
        texts = []
        for page in doc:
            try:
                texts.append(page.get_text())
            except Exception:
                continue
        return "\n".join(texts)

    def _extract_docx(self, path: str) -> str:
        if not docx:
            raise RuntimeError("python-docx is not installed")
        d = docx.Document(path)
        return "\n".join([p.text for p in d.paragraphs if p.text and p.text.strip()])

    def _clean_text(self, raw: str) -> str:
        if not raw:
            return ""
        text = raw.replace("\r\n", "\n").replace("\r", "\n")
        return re.sub(r"\n{2,}", "\n\n", text).strip()

    def _detect_sections(self, text: str) -> Dict[str, str]:
        sections: Dict[str, List[str]] = {}
        current = "_root"
        sections[current] = []
        heading_re = re.compile(
            r"^(education|work experience|experience|projects|certifications|technical skills|soft skills|technical|soft|skills|summary|contact|personal)\b",
            re.IGNORECASE,
        )
        for line in text.splitlines():
            low = line.strip().lower()
            m = heading_re.match(low)
            if m:
                current = m.group(1).lower().split()[0]
                sections[current] = []
            else:
                sections.setdefault(current, []).append(line)
        return {k: "\n".join(v).strip() for k, v in sections.items() if v}

    def _extract_name(self, text: str) -> Optional[str]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            return None
        head = "\n".join(lines[:5])
        if self.nlp:
            try:
                doc = self.nlp(head)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        return ent.text
            except Exception:
                pass
        first = lines[0]
        if len(first.split()) <= 5:
            return first
        return None

    def _extract_skills(self, text: str) -> Tuple[List[ExtractedSkill], List[ExtractedSkill]]:
        found_tech: Dict[str, Tuple[int, str]] = {}
        found_soft: Dict[str, Tuple[int, str]] = {}

        lowered = text.lower()

        # Match technical variations
        for variant, canonical in VARIATIONS.items():
            if variant in lowered:
                found_tech[canonical] = (found_tech.get(canonical, (0, ""))[0] + 1, variant)

        # Match phrase matcher for canonical master skills
        if self.matcher and self.nlp:
            try:
                doc = self.nlp(text)
                matches = self.matcher(doc)
                for mid, start, end in matches:
                    span = doc[start:end]
                    name = span.text
                    canonical = normalize_skill(name)
                    if canonical:
                        found_tech[canonical] = (found_tech.get(canonical, (0, ""))[0] + 1, name)
            except Exception:
                pass

        # Match soft skills
        for soft_skill in SOFT_SKILLS_TAXONOMY:
            if soft_skill in lowered:
                canonical = soft_skill.title()
                found_soft[canonical] = (found_soft.get(canonical, (0, ""))[0] + 1, soft_skill)

        tech_list = [
            ExtractedSkill(name=k, confidence=min(0.95, 0.5 + 0.1 * cnt), raw_match=raw, is_soft_skill=False)
            for k, (cnt, raw) in found_tech.items()
        ]
        soft_list = [
            ExtractedSkill(name=k, confidence=min(0.95, 0.5 + 0.1 * cnt), raw_match=raw, is_soft_skill=True)
            for k, (cnt, raw) in found_soft.items()
        ]

        return tech_list, soft_list

    def _extract_education(self, text: str) -> List[EducationItem]:
        if not text:
            return []
        items = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        degree_keywords = ["bachelor", "master", "phd", "b.s", "b.a", "m.s", "m.a", "degree", "diploma"]

        current_inst = None
        current_degree = None

        for line in lines:
            low = line.lower()
            if any(deg in low for deg in degree_keywords):
                current_degree = line
            elif len(line.split()) >= 2 and not current_inst:
                current_inst = line

            if current_inst:
                items.append(EducationItem(
                    institution=current_inst,
                    degree=current_degree or "Bachelor of Science",
                    field_of_study="Computer Science" if "computer" in low or "cs" in low else "General Studies"
                ))
                current_inst = None
                current_degree = None

        return items or [EducationItem(institution="University Benchmark", degree="Bachelor of Science", field_of_study="Computer Science")]

    def _extract_projects(self, text: str) -> List[ProjectItem]:
        if not text:
            return []
        projects = []
        blocks = text.split("\n\n")
        for b in blocks:
            lines = [l.strip() for l in b.splitlines() if l.strip()]
            if lines:
                title = lines[0]
                desc = " ".join(lines[1:]) if len(lines) > 1 else lines[0]
                projects.append(ProjectItem(title=title, description=desc))
        return projects

    def _extract_experiences(self, text: str) -> List[ExperienceItem]:
        if not text:
            return []
        experiences = []
        blocks = text.split("\n\n")
        for b in blocks:
            lines = [l.strip() for l in b.splitlines() if l.strip()]
            if lines:
                company = lines[0]
                title = lines[1] if len(lines) > 1 else "Engineer / Intern"
                desc = " ".join(lines[2:]) if len(lines) > 2 else ""
                experiences.append(ExperienceItem(
                    company=company,
                    title=title,
                    description=desc,
                    years=1.0,
                ))
        return experiences
