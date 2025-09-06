from typing import List
import spacy
from spacy.matcher import PhraseMatcher
import json
import re

def add_space_around_slash(text: str) -> str:
    return text.replace("/", " / ")

def insert_spaces_with_skills(text: str, skills: List[str]) -> str:
    fixed = text
    for skill in sorted(skills, key=len, reverse=True):  # longest first
        if len(skill) < 5:  # skip very short skills
            continue
        pattern = re.compile(re.escape(skill), re.IGNORECASE)
        fixed = pattern.sub(f" {skill} ", fixed)
    return " ".join(fixed.split())  # normalize spaces

def save_to_textfile(filename: str, content: str, mode: str = "w") -> None:
    try:
        with open(filename, mode, encoding="utf-8") as f:
            f.write(content + "\n")
        print(f"✅ Saved content to {filename}")
    except Exception as e:
        print(f"❌ Error saving file {filename}: {e}")

def skill_extraction(content: str) -> List[str]:
    # Load skills from JSON
    with open("skills.json", "r") as f:
        skills_dict = json.load(f)
    with open("normalize_skills.json", "r") as f:
        normalize_skills_dict = json.load(f)
        
    skills = [skill for category in skills_dict.values() for skill in category]

    cleaned_content = add_space_around_slash(content)
    cleaned_content = insert_spaces_with_skills(cleaned_content, skills)

    nlp = spacy.load("en_core_web_sm")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    patterns = [nlp.make_doc(skill) for skill in skills]
    matcher.add("SKILL", patterns)
    doc = nlp(cleaned_content)
    matches = matcher(doc)
    extracted_skills = [doc[start:end].text for _, start, end in matches]

    def normalize_array(values, mapping):
        # Build reverse lookup dict: synonym -> canonical
        reverse_map = {}
        for canonical, synonyms in mapping.items():
            reverse_map[canonical.lower()] = canonical  # include canonical itself
            for s in synonyms:
                reverse_map[s.lower()] = canonical       # point synonyms to canonical
        return [reverse_map.get(v.lower(), v) for v in values]

    return list(set(normalize_array(extracted_skills, normalize_skills_dict)))


def validate_job_title(title: str) -> bool:
    invalid_keywords = ["devops",  "servicenow", "qa", "quality assurance", "data", "solution", "shopify",  "salesforce", "japanese", "microsoft", "cloud", "automation", 
                   "SAP", "CRM", "game producer", "azure integration", "SEO specialist", "google ads", "web designer", "campaign executive",
                   "quality engineer", "infastructure", "system admin", "coordinator", "oracle", "administrator", "unity", "graphic designer", 
                   "security consultant", "marketing", "wordpress", "writer",
                #    "ruby","java", ".net", "c#", "springboot", "laravel", "php",
                   ]
    if not title:
        return False
    for item in invalid_keywords:
        if item.lower() in title.lower():  # case-insensitive check
            return False
    return True


with open("job_nice_2025_09_04.txt", "r") as f:
    content = f.read()
print('skills', skill_extraction(content))