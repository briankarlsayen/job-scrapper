#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

# Path to your actual Python job
JOB = "main.py"

# File to record last run date
LAST_RUN = "last_run.txt"
# LAST_RUN = "/tmp/job_last_run"


today = datetime.now().strftime("%Y-%m-%d")
now = datetime.now()

# --- Check if already run today ---
if os.path.exists(LAST_RUN):
    with open(LAST_RUN, "r") as f:
        last_run_date = f.read().strip()
    if last_run_date == today:
        exit(0)

# --- If time is past 14:00 today, run the job ---
if now.hour > 14 or (now.hour == 14 and now.minute >= 0):
    subprocess.run(["python", JOB, "job_checker"])
    with open(LAST_RUN, "w") as f:
        f.write(today)
