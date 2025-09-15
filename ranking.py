import pandas as pd
import json

def load_normalizer(json_path):
    with open(json_path, "r") as f:
        normalize_map = json.load(f)
    lookup = {}
    for canonical, variations in normalize_map.items():
        for v in variations:
            lookup[v.lower()] = canonical
    return lookup

def load_skill_categories(json_path):
    with open(json_path, "r") as f:
        categories = json.load(f)

    skill_to_category = {}
    for category, skills in categories.items():
        for skill in skills:
            skill_to_category[skill.lower()] = category  # lowercase for matching
    return skill_to_category

def load_skill_weights(json_path):
    with open(json_path, "r") as f:
        categories = json.load(f)
    
    return categories

def normalize_skill(skill, lookup):
    return lookup.get(skill.lower().strip(), skill.strip()).lower()

def weighted_score(matched, input_skills, skill_to_category, skill_weights):
    # # Sum actual matched weights
    # matched_weight = 0
    # for skill in matched:
    #     category = skill_to_category.get(skill.lower(), "Other Tools")
    #     matched_weight += skill_weights.get(category, 0)

    # # Calculate max possible weight from all input skills
    # max_weight = 0
    # for skill in input_skills:
    #     category = skill_to_category.get(skill.lower(), "Other Tools")
    #     max_weight += skill_weights.get(category, 0)

    # # Normalize to 0–1 scale
    # if max_weight == 0:
    #     return 0.0
    # return round(matched_weight / max_weight, 3)

    matched_weight = sum(
        skill_weights.get(skill_to_category.get(skill.lower(), "Other Tools"), 0)
        for skill in matched
    )

    max_weight = sum(
        skill_weights.get(skill_to_category.get(skill.lower(), "Other Tools"), 0)
        for skill in input_skills
    )

    if max_weight == 0:
        return 0.0
    return round(matched_weight / max_weight, 3)



def rank_jobs_by_skills(df, input_skills) -> list:
    lookup = load_normalizer('normalize_skills.json')
    skill_to_category = load_skill_categories('skills.json')
    skill_weights = load_skill_weights('skill_weight.json')

    # df = pd.read_csv(csv_path, delimiter=";")
    input_set = set([normalize_skill(s, lookup) for s in input_skills])
    ranked_jobs = []
    
    for _, row in df.iterrows():
        skills_raw = row.get("required_skills", "")
        if not isinstance(skills_raw, str) or not skills_raw.strip():
            continue
        job_skills = [
            s.strip().lower() for s in skills_raw.split(",") if s.strip()
        ]
        job_skills_set = set(job_skills)

        # Calculate overlap
        matched = job_skills_set & input_set
        if not matched:
            continue  # skip if no match
        matched_text = ",".join(matched)
        job_skills_text = ",".join(job_skills)

        score = weighted_score(matched, job_skills, skill_to_category, skill_weights)

        ranked_jobs.append({
            "title": row.get("title", "N/A"),
            "company": row.get("company", "N/A"),
            "required_skills": job_skills_text,
            "matched_skills": matched_text,
            "score": score,
            "location": row.get("company", "N/A"),
            "date_posted": row.get("date_posted", "N/A"),
            "scraped_at": row.get("scraped_at", "N/A"),
            "job_link": row.get("job_link", ""),
        })
    # Sort by score descending
    ranked_jobs.sort(key=lambda x: x["score"], reverse=True)
    return ranked_jobs

# data_path = "./datas/2025_09_13/jobs.csv"
# input_skills = ['python', 'Javascript', 'Typescript', 'nosql', 'sql', 'express', 'nodejs', 'reactjs', 'django', 'vuejs', 'mongodb', 'postgresql', 'mysql', 'next.js', 'html', 'css', 'aws', 'azure', 's3', 'zustand', 'redux', 'git', 'gitlab', 'vercel', 'jira','ci/cd', 'rest api', 'docker', 'linux', 'windows', 'mui', 'tailwindcss', 'jest', 'github']
# df = pd.read_csv(data_path, delimiter=";")

# ranked_skills = rank_jobs_by_skills(df=df, input_skills=input_skills)
# # create a csv file
# df = pd.DataFrame(ranked_skills)
# df.to_csv("./datas/ranked_jobs.csv", sep=';', index=False)
