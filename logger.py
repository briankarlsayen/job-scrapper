import sys
from datetime import datetime
from pathlib import Path
import os
from datetime import date

LAST_RUN = "last_run.txt"
today = datetime.now().strftime("%Y-%m-%d")
now = datetime.now()

def log(message, file):
    with open(file, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def logger_script():
    log_file = Path(__file__).parent / "logger.log"
    
    source = sys.argv[1] if len(sys.argv) > 1 else "manual"
    log(f"Script triggered by: {source}", log_file)

    with open(LAST_RUN, "w") as f:
        f.write(today)

def linkedin_log(message):
    today = date.today()
    formatted_date = today.strftime("%Y_%m_%d")
    folder_path = f"logs/linkedin"
    os.makedirs(folder_path, exist_ok=True)

    text_file_path = os.path.join(folder_path, f"{formatted_date}.log")

    log(message, text_file_path)