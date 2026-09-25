import re
import io
from typing import Dict, Any, List
import pypdf
from backend.universities_data import CAREER_FIELDS

# Common tech & soft skills dictionary
SKILLS_DICTIONARY = [
    # Languages
    "python", "javascript", "typescript", "c++", "c#", "c", "java", "golang", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "html", "css", "sql",
    # Frameworks & Libraries
    "react", "react.js", "next.js", "vue", "angular", "node.js", "express", "django",
    "flask", "fastapi", "spring boot", "laravel", "tailwind", "bootstrap", "flutter",
    # AI / ML / Data
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "opencv", "matplotlib", "seaborn", "keras",
    "huggingface", "llm", "generative ai", "langchain", "tableau", "power bi", "spark", "hadoop",
    # Cloud & DevOps & Infra
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git", "github", "linux",
    "bash", "terraform", "ansible", "nginx", "jenkins", "graphql", "rest api", "microservices",
    # Databases & Caches
    "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch", "cassandra", "firebase",
    # Core & Engineering
    "data structures", "algorithms", "dsa", "oop", "system design", "operating systems",
    "dbms", "computer networks", "embedded systems", "iot", "arduino", "matlab"
]

ACTION_VERBS = [
    "developed", "designed", "implemented", "architected", "built", "engineered",
    "optimized", "deployed", "spearheaded", "accelerated", "reduced", "increased",
    "achieved", "created", "published", "led", "managed", "integrated"
]

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            return "\n".join(text)
        except Exception as e:
            print("Error reading PDF:", e)
            return ""

    @staticmethod
    def parse_resume(text: str, target_field_id: str = "ai_ml") -> Dict[str, Any]:
        cleaned_text = text.lower()

        # 1. Detect CGPA
        cgpa = 8.0
        # Check patterns like "8.6 cgpa", "cgpa: 8.6", "gpa 3.8/4", "8.4 / 10", "84%"
        cgpa_match = re.search(r'(?:cgpa|gpa|pointer|grade)[:\s]*([0-9]\.[0-9]{1,2})', cleaned_text)
        if not cgpa_match:
            cgpa_match = re.search(r'([0-9]\.[0-9]{1,2})\s*(?:/10|/4\.0|cgpa|gpa)', cleaned_text)
        if not cgpa_match:
            pct_match = re.search(r'([0-9]{2}(?:\.[0-9]{1,2})?)\s*%', cleaned_text)
            if pct_match:
                pct = float(pct_match.group(1))
                cgpa = round(min(10.0, max(4.0, pct / 9.5)), 2)
        else:
            val = float(cgpa_match.group(1))
            if val <= 4.0:
                cgpa = round(min(10.0, val * 2.5), 2)
            else:
                cgpa = round(min(10.0, val), 2)

        # 2. Detect Degree
        degree = "B.Tech"
        if "m.tech" in cleaned_text or "master of technology" in cleaned_text:
            degree = "M.Tech"
        elif "mca" in cleaned_text or "master of computer" in cleaned_text:
            degree = "MCA"
        elif "mba" in cleaned_text or "master of business" in cleaned_text:
            degree = "MBA"
        elif "bca" in cleaned_text or "bachelor of computer applications" in cleaned_text:
            degree = "BCA"
        elif "b.sc" in cleaned_text or "bachelor of science" in cleaned_text:
            degree = "B.Sc"
        elif "bba" in cleaned_text:
            degree = "BBA"
        elif "b.tech" in cleaned_text or "bachelor of engineering" in cleaned_text or "b.e" in cleaned_text:
            degree = "B.Tech"

        # 3. Detect Skills
        detected_skills = []
        for skill in SKILLS_DICTIONARY:
            # Word boundary regex check
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, cleaned_text):
                detected_skills.append(skill.title())

        num_skills = max(len(detected_skills), 3)

        # 4. Detect Projects
        # Look for project sections or headings
        project_count = 3
        project_sections = re.findall(r'(?:project|developed|built|github\.com\/)[^\n]+', cleaned_text)
        if project_sections:
            project_count = min(15, max(2, len(set(project_sections)) // 2))

        # 5. Detect Internships
        internships_count = 1
        intern_matches = re.findall(r'\b(?:intern|internship|trainee|apprentice|work experience)\b', cleaned_text)
        if intern_matches:
            internships_count = min(6, max(1, len(intern_matches) // 2))
        else:
            internships_count = 0

        # 6. Detect Certifications
        cert_matches = re.findall(r'\b(?:certified|certification|credential|coursera|udemy|aws certified|google cloud certified|hackerrank|leetcode)\b', cleaned_text)
        certifications_count = min(10, max(0, len(cert_matches)))

        # 7. Detect Hackathons
        hackathon_participated = 1
        hackathon_won = 0
        if "hackathon" in cleaned_text or "hack" in cleaned_text:
            hackathon_participated = 2
            if re.search(r'\b(?:winner|1st|first place|runner up|podium|top 3|finalist|champion)\b', cleaned_text):
                hackathon_won = 1
                hackathon_participated = 3

        # 8. Communication and Vocabulary Assessment
        words = re.findall(r'\w+', cleaned_text)
        unique_words = len(set(words))
        word_count = len(words)
        vocab_richness = (unique_words / max(word_count, 1)) if word_count > 0 else 0.5
        communication_score = round(min(100.0, max(45.0, 50.0 + vocab_richness * 60.0)), 1)

        # 9. Compute ATS & Resume Strength Score (0-100)
        ats_score = 40.0
        # Action verbs
        verbs_found = sum(1 for verb in ACTION_VERBS if verb in cleaned_text)
        ats_score += min(18.0, verbs_found * 2.0)
        # Quantifiable metrics (% or numbers)
        metrics_found = len(re.findall(r'\b\d+(?:%|\+|x|\s*k|\s*lpa)\b', cleaned_text))
        ats_score += min(15.0, metrics_found * 2.5)
        # Skills density
        ats_score += min(15.0, len(detected_skills) * 1.2)
        # Experience / Project richness
        if internships_count > 0:
            ats_score += 8.0
        if project_count >= 3:
            ats_score += 7.0
        ats_score = round(min(98.0, max(30.0, ats_score)), 1)

        # 10. Field Relevance Match (Against Target Career Track)
        target_field = CAREER_FIELDS.get(target_field_id, CAREER_FIELDS["ai_ml"])
        target_skills = target_field["key_skills"]
        
        matched_target_skills = []
        for skill in target_skills:
            if skill in cleaned_text:
                matched_target_skills.append(skill.title())

        field_match_ratio = len(matched_target_skills) / max(len(target_skills) * 0.55, 1.0)
        skill_relevance_score = round(min(1.0, max(0.25, field_match_ratio * 0.75 + (ats_score / 100.0) * 0.25)), 2)
        field_match_percentage = round(skill_relevance_score * 100, 1)

        missing_target_skills = [s.title() for s in target_skills if s.title() not in matched_target_skills][:4]

        return {
            "degree_program": degree,
            "cgpa": cgpa,
            "num_skills": num_skills,
            "detected_skills": detected_skills[:16],
            "projects_count": project_count,
            "internships_count": internships_count,
            "certifications_count": certifications_count,
            "hackathons_participated": hackathon_participated,
            "hackathons_won": hackathon_won,
            "communication_score": communication_score,
            "resume_score": ats_score,
            "skill_relevance_score": skill_relevance_score,
            "field_match_percentage": field_match_percentage,
            "target_field_name": target_field["name"],
            "matched_target_skills": matched_target_skills,
            "missing_target_skills": missing_target_skills,
            "backlogs": 0
        }
