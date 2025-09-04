from typing import List
import spacy
from spacy.matcher import PhraseMatcher
import json

def save_to_textfile(filename: str, content: str, mode: str = "w") -> None:
    """
    Save text content to a file.

    :param filename: Name or path of the text file (e.g., "jobs.txt" or "./data/jobs.txt").
    :param content: The string content you want to save.
    :param mode: File mode - "w" = overwrite, "a" = append.
    """
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
        
    skills = [skill for category in skills_dict.values() for skill in category]
    nlp = spacy.load("en_core_web_sm")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    patterns = [nlp.make_doc(skill) for skill in skills]
    matcher.add("SKILL", patterns)
    doc = nlp(content)
    matches = matcher(doc)
    extracted_skills = [doc[start:end].text for _, start, end in matches]
    

    return set(extracted_skills)

def validate_job_title(title: str) -> bool:
    invalid_keywords = ["devops",  "servicenow", "qa", "quality assurance", "data", "solution", "shopify",  "salesforce", "japanese", "microsoft", "cloud", "automation", 
                   "SAP", "CRM", "game producer", "azure integration", "SEO specialist", "google ads", "web designer", "campaign executive",
                   "quality engineer", "infastructure", "system admin", "coordinator", "oracle", "administrator", "unity", "graphic designer", 
                   "security consultant", "marketing", "wordpress", "writer",
                   "ruby","java", ".net", "c#", "springboot", "laravel", "php",]
    if not title:
        return False
    for item in invalid_keywords:
        if item.lower() in title.lower():  # case-insensitive check
            return False
    return True


with open("job_nice.txt", "r") as f:
    content = f.read()
print('skills', skill_extraction(content))