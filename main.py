import os
from datetime import date
import pandas as pd
import subprocess
import time
from ranking import rank_jobs_by_skills
from migration import migrate
from utils.utils import logger
import sys
from pathlib import Path

# run logger script
log_file_path=Path(__file__).resolve().parent

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")

# get/create the directory
ss_folder_path = "screenshots"
os.makedirs(ss_folder_path, exist_ok=True)
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
success_scripts = []
for script in to_process_exist_list:
    success = False
    error_message = "Retries Failed"
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
            success_scripts.append(script)
            break  # exit retry loop if success
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed attempt {attempt} for {script}")
            print('error :', e.stderr.strip())
            if e.stderr:
                error_message = e.stderr.strip()
            time.sleep(1)  # optional delay before retry
    if not success:
        print(f"⚠️ Skipping {script} after 3 failed attempts")
        logger(log_message=f"Scraping Failed: {script}, {error_message}", file_path=log_file_path)
    
if not success_scripts:
    sys.exit(1)

logger(log_message="Scraping Success", file_path=log_file_path)

# READ data from created csv's
def merge_csv_files():
    files = []
    folder = Path(folder_path)
    exclude = {"jobs.csv", "ranked_jobs.csv"}
    for f in folder.glob("*.csv"):
        if f.name not in exclude:
            source = os.path.splitext(os.path.basename(f))[0]
            item = pd.read_csv(f, delimiter=";")
            item['source'] = source
            files.append(item)
    return files

dfs = merge_csv_files()
df = pd.concat(dfs, ignore_index=True)
df.to_csv(f"{folder_path}/jobs.csv",  sep=';', index=False) # CREATE jobs.csv file
print('jobs: ', len(df))

# CREATE ranked_jobs.csv file
input_skills = ['python', 'Javascript', 'Typescript', 'nosql', 'sql', 'express', 'nodejs', 'reactjs', 'django', 'vuejs', 'mongodb', 'postgresql', 'mysql', 'next.js', 'html', 'css', 'aws', 'azure', 's3', 'zustand', 'redux', 'git', 'gitlab', 'vercel', 'jira','ci/cd', 'rest api', 'docker', 'linux', 'windows', 'mui', 'tailwindcss', 'jest', 'github']
ranked_skill = rank_jobs_by_skills(df=df, input_skills=input_skills)
updated_df = pd.DataFrame(ranked_skill)
updated_df.to_csv(f"{folder_path}/ranked_jobs.csv", sep=';', index=False)

# CREATE jobs.txt
def merge_txt_files(output_file: str):
    folder = Path(folder_path)
    exclude = {"jobs.txt"}
    txt_files = [f for f in folder.glob("*.txt") if f.name not in exclude]

    with open(output_file, "w", encoding="utf-8") as out:
        for file in txt_files:
            with open(file, "r", encoding="utf-8") as f:
                out.write(f.read())
merge_txt_files(output_file=f"{folder_path}/jobs.txt")

# INSERT todays job data to db
try: 
    migrate(file=f"{folder_path}/jobs.csv")
except:
    print('Unable to save to database')

# DELETE files
def safe_remove(file_path: str | None):
    """Remove file if it exists and path is valid."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

if os.path.exists(jobs_csv_file_path):
    safe_remove(scraper['jobstreet']['csv'])
    safe_remove(scraper['jobstreet']['txt'])
    safe_remove(scraper['linkedin']['csv'])
    safe_remove(scraper['linkedin']['txt'])