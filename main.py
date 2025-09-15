import os
from datetime import date
import pandas as pd
import sys
import subprocess
import time
from typing import List 
from constant import SEPARATOR
from ranking import rank_jobs_by_skills

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")

# get/create the directory
folder_path = f"datas/{formatted_date}"
os.makedirs(folder_path, exist_ok=True)

csv_files = [f"{folder_path}/jobstreet.csv", f"{folder_path}/linkedin.csv"]

scraper = {}
scraper['linkedin'] = {
    'file': 'linkedin.py',
    'csv': f"{folder_path}/linkedin.csv"
}
scraper['jobstreet'] = {
    'file': 'jobstreet.py',
    'csv':f"{folder_path}/jobstreet.csv"
}
to_process_exist_list = []
for key, data in scraper.items():
    if not os.path.exists(data.get("csv")):
        to_process_exist_list.append(data.get('file'))

for script in to_process_exist_list:
    success = False
    for attempt in range(1, 4):  # try 3 times max
        print(f"\n➡️ Running {script}, attempt {attempt}/3")
        try:
            result = subprocess.run(
                ["python", script],
                check=True,   # raises CalledProcessError if script fails
                capture_output=True,
                text=True
            )
            print(f"✅ Success: {script}")
            print(result.stdout)
            success = True
            break  # exit retry loop if success
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed attempt {attempt} for {script}")
            print(e.stderr)
            time.sleep(1)  # optional delay before retry
    if not success:
        print(f"⚠️ Skipping {script} after 3 failed attempts")


# read data from todays csv
dfs = []
for key, data in scraper.items():
    item = pd.read_csv(data.get('csv'), delimiter=";")
    dfs.append(item)

# OLD jobs
df = pd.concat(dfs, ignore_index=True)
df.to_csv(f"{folder_path}/jobs.csv",  sep=';', index=False)
print('jobs: ', len(df))


# UPDATED jobs
input_skills = ['python', 'Javascript', 'Typescript', 'nosql', 'sql', 'express', 'nodejs', 'reactjs', 'django', 'vuejs', 'mongodb', 'postgresql', 'mysql', 'next.js', 'html', 'css', 'aws', 'azure', 's3', 'zustand', 'redux', 'git', 'gitlab', 'vercel', 'jira','ci/cd', 'rest api', 'docker', 'linux', 'windows', 'mui', 'tailwindcss', 'jest', 'github']
ranked_skill = rank_jobs_by_skills(df=df, input_skills=input_skills)
updated_df = pd.DataFrame(ranked_skill)
updated_df.to_csv(f"{folder_path}/ranked_jobs.csv", sep=';', index=False)


def merge_txt_files(files: List[str], output_file: str):
    with open(output_file, "w", encoding="utf-8") as out:
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                out.write(f.read())

files_to_merge = [f"{folder_path}/jobstreet.txt", f"{folder_path}/linkedin.txt"]
merge_txt_files(files_to_merge, f"{folder_path}/jobs.txt")