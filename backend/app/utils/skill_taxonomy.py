from typing import Dict, List

# Master taxonomy canonical names
MASTER_SKILLS: List[str] = [
    "JavaScript",
    "TypeScript",
    "Python",
    "Java",
    "C++",
    "C",
    "C#",
    "PHP",
    "Go",
    "Rust",
    "Ruby",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Redis",
    "React",
    "Next.js",
    "Angular",
    "Vue.js",
    "Node.js",
    "Express.js",
    "Django",
    "Flask",
    "FastAPI",
    "Spring Boot",
    "HTML",
    "CSS",
    "Bootstrap",
    "Tailwind CSS",
    "Material-UI",
    "Vite",
    "REST APIs",
    "GraphQL",
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Linux",
    "CI/CD",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "BERT",
    "Scikit-Learn",
    "TensorFlow",
    "PyTorch",
    "Data Structures",
    "Algorithms",
    "Problem Solving",
]

# Variations mapping: maps common variations to canonical name
VARIATIONS: Dict[str, str] = {
    # JavaScript / TypeScript
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",

    # Core Languages
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c": "C",
    "c#": "C#",
    "csharp": "C#",
    "php": "PHP",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",

    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "bootstrap": "Bootstrap",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "material ui": "Material-UI",
    "material-ui": "Material-UI",
    "materialui": "Material-UI",
    "mui": "Material-UI",
    "vite": "Vite",

    # Backend
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",

    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "my sql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "mongo db": "MongoDB",
    "sqlite": "SQLite",
    "redis": "Redis",

    # DevOps & Tools
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "linux": "Linux",
    "cicd": "CI/CD",
    "ci/cd": "CI/CD",

    # AI & ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "bert": "BERT",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",

    # CS Fundamentals
    "data structures": "Data Structures",
    "dsa": "Data Structures",
    "algorithms": "Algorithms",
    "problem solving": "Problem Solving",
}


def normalize_skill(raw: str) -> str | None:
    if not raw:
        return None
    key = raw.strip().lower()
    key = key.replace("\n", " ").replace("\r", " ")
    for ch in [",", ";", "(", ")", "\"", "'"]:
        key = key.replace(ch, "")
    key = key.strip()

    if key in VARIATIONS:
        return VARIATIONS[key]
    for canonical in MASTER_SKILLS:
        if key == canonical.lower():
            return canonical
    for canonical in MASTER_SKILLS:
        if len(canonical) > 2 and canonical.lower() in key:
            return canonical
    return None
