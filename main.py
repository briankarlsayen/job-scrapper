import os
from datetime import date
import pandas as pd
import subprocess
import time
from ranking import rank_jobs_by_skills
from migration import migrate
from utils.utils import logger, log_json, safe_remove
import sys
from pathlib import Path
from scrap_old_logs import scrap_old_logs
from config import INPUT_SKILLS

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
log_file_path=Path(__file__).resolve().parent
log_main_file_path = "logs/main"
os.makedirs(log_main_file_path, exist_ok=True)
ss_folder_path = "screenshots"
os.makedirs(ss_folder_path, exist_ok=True)
folder_path = f"datas/{formatted_date}"
os.makedirs(folder_path, exist_ok=True)
os.chmod(folder_path, 0o775)
jobs_csv_file_path = f"{folder_path}/jobs.csv"
if os.path.exists(jobs_csv_file_path): # BLOCK THIS ON --- TESTING ---
    log_json(log_dir='main', level='error', message="Jobs csv already exist!")
    sys.exit(1)

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
        log_json(log_dir='main', level='info', message=f"Running {script} | attempt {attempt}/3")
        try:
            result = subprocess.run(
                ["python", script],
                check=True,
                capture_output=True,
                text=True
            )
            log_json(log_dir='main', level='info', message=f"Successfully run script: {script}")
            success = True
            success_scripts.append(script)
            break  # exit retry loop if success
        except subprocess.CalledProcessError as e:
            log_json(log_dir='main', level='warning', message=f"Failed attempt {attempt} for {script}, Error: ${e.stderr.strip()}")
            if e.stderr:
                error_message = e.stderr.strip()
            time.sleep(1)  # optional delay before retry
    if not success:
        log_json(log_dir='main', level='error', message=f"Scraping Failed: {script}, {error_message}")
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
            if len(item) < 1:
                log_json(log_dir='main', level='error', message=f"No listing scraped on {source}")
                continue
            log_json(log_dir='main', level="info", message=f"Source: {source} | Listings: {len(item)}")
    return files

log_json(log_dir='main', level='info', message='Merging scraped data')
dfs = merge_csv_files()
df = pd.concat(dfs, ignore_index=True)
df.to_csv(f"{folder_path}/jobs.csv",  sep=';', index=False) # CREATE jobs.csv file
log_json(log_dir='main', level='info', message=f"Successfully scraped {len(df)} listings")

# CREATE ranked_jobs.csv file
ranked_skill = rank_jobs_by_skills(df=df, input_skills=INPUT_SKILLS)
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

# INSERT todays job data to db | BLOCK THIS ON --- TESTING ---
try: 
    migrate(file=f"{folder_path}/jobs.csv")
except:
    log_json(log_dir='main', level='error', message=f"Unable to save to database")

# DELETE files | BLOCK THIS ON --- TESTING ---
def safe_remove(file_path: str | None):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

if os.path.exists(jobs_csv_file_path):
    safe_remove(scraper['jobstreet']['csv'])
    safe_remove(scraper['jobstreet']['txt'])
    safe_remove(scraper['linkedin']['csv'])
    safe_remove(scraper['linkedin']['txt'])

scrap_old_logs()