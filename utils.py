from typing import List
import spacy
from spacy.matcher import PhraseMatcher
import json
import re
from pathlib import Path
import sys
from datetime import datetime, date
import os
import logging

def add_space_around_slash(text: str) -> str:
    pascal_case_space = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text) if re.match(r'^[a-z]', text) else text
    # pascal_case_space.replace("/", " / ")
    return re.sub(r"\s*/\s*", " / ", pascal_case_space)

def insert_spaces_with_skills(text: str, skills: List[str]) -> str:
    fixed = text
    for skill in sorted(skills, key=len, reverse=True):  # longest first
        if len(skill) < 6:  # skip very short skills
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

    special_skills = {"C", "C++", "C#", "Go", "S3",} 
    # Add patterns with token boundaries (skip 1–2 letter skills except special_skills)
    valid_skills = [s for s in skills if len(s) > 2 or s in special_skills]
    patterns = [nlp.make_doc(skill) for skill in valid_skills]
    matcher.add("SKILL", patterns)
    doc = nlp(cleaned_content)
    matches = matcher(doc)
    extracted_spans = [doc[start:end] for _, start, end in matches]
    extracted_texts = [span.text.strip() for span in extracted_spans]
    cleaned_skills = []

    def validate_php(text: str) -> bool:
        if "salary" in text or "bonus" in text:
            return True
        
        pattern = r'[\$€£]?\d+(?:,\d{3})*(?:\.\d+)?(?:[KMkm])?\b'
        for raw in re.findall(pattern, text):
            s = raw.strip()

            # remove leading currency symbol if present
            if s and s[0] in "$€£":
                s = s[1:]

            # detect K/M suffix
            suffix = ''
            if s and s[-1].upper() in ("K", "M"):
                suffix = s[-1].upper()
                s = s[:-1]

            # remove commas and parse number (allow decimals)
            s_clean = s.replace(",", "")
            try:
                num = float(s_clean)
            except ValueError:
                continue

            # apply multiplier for K / M
            if suffix == "K":
                num *= 1_000
            elif suffix == "M":
                num *= 1_000_000

            if num > 100:
                return True

        return False
    
    for i, text in enumerate(extracted_texts):
        span = extracted_spans[i]
        # 1. Skip "C" if it's part of Vitamin C, scalability, etc.
        if text == "C":
            sentence = span.sent.text.lower()
            if (span.start > 0 and doc[span.start-1].is_alpha) or (
                span.end < len(doc) and doc[span.end].is_alpha
            ):
                continue

        if text.lower() == "java":
            # If it's followed by "script", skip it
            if span.end < len(doc) and doc[span.end].text.lower().startswith("script"):
                continue
            else:
                cleaned_skills.append(text)  # ✅ safe to add
                continue

        # 2. Prevent substring duplicates (C inside C#, C inside C++)
        if any(text != other and text in other for other in extracted_texts):
            continue

        if text.upper() == "PHP":
            sentence = span.sent.text.lower()   # full sentence containing PHP
            if validate_php(sentence):
                continue  # skip if PHP is used in a salary/bonus context

        cleaned_skills.append(text)

    def normalize_array(values, mapping):
        # Build reverse lookup dict: synonym -> canonical
        reverse_map = {}
        for canonical, synonyms in mapping.items():
            reverse_map[canonical.lower()] = canonical  # include canonical itself
            for s in synonyms:
                reverse_map[s.lower()] = canonical       # point synonyms to canonical
        return [reverse_map.get(v.lower(), v) for v in values]
    
    lowercase_skills = [s.lower() for s in normalize_array(cleaned_skills, normalize_skills_dict)]

    return list(set(lowercase_skills))

def validate_job_title(title: str) -> bool:
    invalid_keywords = ["devops",  "servicenow", "qa", "quality assurance", "data", "solution", "shopify",  "salesforce", "japanese", "microsoft", "cloud", "automation", 
                   "SAP", "CRM", "game producer", "azure integration", "SEO specialist", "google ads", "web designer", "campaign executive",
                   "quality engineer", "infastructure", "system admin", "coordinator", "oracle", "administrator", "unity", "graphic designer", 
                   "security consultant", "marketing", "wordpress", "writer", "citrix"
                #    "ruby","java", ".net", "c#", "springboot", "laravel", "php",
                   ]
    if not title:
        return False
    for item in invalid_keywords:
        if item.lower() in title.lower():  # case-insensitive check
            return False
    return True

def log(message, file):
    with open(file, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def logger(log_message=""):
    log_file = Path(__file__).parent / "logger.log"
    
    source = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    if not log_message:
        log(f"Script triggered by: {source}", log_file)
    else:
        log(log_message, log_file)


def linkedin_log(message):
    today = date.today()
    formatted_date = today.strftime("%Y_%m_%d")
    folder_path = f"logs/linkedin"
    os.makedirs(folder_path, exist_ok=True)

    text_file_path = os.path.join(folder_path, f"{formatted_date}.log")

    logging.basicConfig(
        filename=text_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    logging.info(message)

def format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}hr"
