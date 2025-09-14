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


def normalize_skill(skill, lookup):
    return lookup.get(skill.lower().strip(), skill.strip()).lower()

def rank_jobs_by_skills(csv_path, input_skills):
    lookup = load_normalizer('normalize_skills.json')
    df = pd.read_csv(csv_path, delimiter=";")
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
        score = round(len(matched) / len(job_skills), 3)
        ranked_jobs.append({
            "title": row.get("title", "Unknown"),
            "skills": job_skills,
            "matched_skills": list(matched),
            "score": score,
            "url": row.get("job_link", ""),
        })
    # Sort by score descending
    ranked_jobs.sort(key=lambda x: x["score"], reverse=True)
    return ranked_jobs


data_path = "./datas/2025_09_13/jobs.csv"
input_skills = ['python', 'Javascript', 'Typescript', 'nosql', 'sql', 'express', 'nodejs', 'reactjs', 'django', 'vuejs', 'mongodb', 'postgresql', 'mysql', 'next.js', 'html', 'css', 'aws', 'azure', 's3', 'zustand', 'redux', 'git', 'gitlab', 'vercel', 'jira','ci/cd', 'rest api', 'docker', 'linux', 'windows', 'mui', 'tailwindcss', 'jest', 'github']
ranked_skills = rank_jobs_by_skills(csv_path=data_path, input_skills=input_skills)

# create a csv file
df = pd.DataFrame(ranked_skills)
df.to_csv("./datas/ranked_jobs.csv", sep=';', index=False)
