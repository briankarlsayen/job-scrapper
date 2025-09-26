import os
from datetime import date
import pandas as pd
import subprocess
import time
from typing import List 
from ranking import rank_jobs_by_skills
from migration import migrate
from utils import logger
import sys

# run logger script
logger()

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")

# get/create the directory
folder_path = f"datas/{formatted_date}"
os.makedirs(folder_path, exist_ok=True)

# Force permission (rwxrwxr-x = 775)
os.chmod(folder_path, 0o775)

jobs_csv_file_path = f"{folder_path}/jobs.csv"

if os.path.exists(jobs_csv_file_path):
    print('Jobs csv already exist!')
    sys.exit(1)

csv_files = [f"{folder_path}/jobstreet.csv", f"{folder_path}/linkedin.csv"]

scraper = {
    'linkedin': {
        'file': 'linkedin.py',
        'csv': f"{folder_path}/linkedin.csv",
        'txt':  f"{folder_path}/linkedin.txt"
    },
    'jobstreet': {
        'file': 'jobstreet.py',
        'csv':f"{folder_path}/jobstreet.csv",
        'txt':f"{folder_path}/jobstreet.txt"
    }
}

to_process_exist_list = []
for key, data in scraper.items():
    if not os.path.exists(data.get("csv")):
        to_process_exist_list.append(data.get('file'))

# RUN scrapers, retry 3 times once failed
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


# READ data from created csv's
dfs = []
for key, data in scraper.items():
    item = pd.read_csv(data.get('csv'), delimiter=";")
    item['source'] = key
    dfs.append(item)
df = pd.concat(dfs, ignore_index=True)
df.to_csv(f"{folder_path}/jobs.csv",  sep=';', index=False) # CREATE jobs.csv file
print('jobs: ', len(df))


# CREATE ranked_jobs.csv file
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

# INSERT todays job data to db
try: 
    migrate(file=f"{folder_path}/jobs.csv")
except:
    print('Unable to save to database')

# DELETE files
if os.path.exists(jobs_csv_file_path):
    os.remove(scraper['jobstreet']['csv'])
    os.remove(scraper['jobstreet']['txt'])
    os.remove(scraper['linkedin']['csv'])
    os.remove(scraper['linkedin']['txt'])