#!/usr/bin/env python3
import fcntl
import os
from datetime import datetime, time
import sys
import subprocess
from utils.utils import log, log_json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_DIR = BASE_DIR
JOB = "main.py"

LOCK_FILE = "/tmp/daily_job.lock"
LOG_FILE = os.path.join(BASE_DIR, "logger.log")
now = datetime.now().time()
today = datetime.now().strftime("%Y-%m-%d")

LAST_RUN = "last_run.txt"

def acquire_lock():
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(0)  # Someone else is running
    return lock_fd


def detect_trigger_source():
    if "--reboot" in sys.argv:
        return "REBOOT"

    if "CRON" in os.getenv("PATH", "") or not os.isatty(0):
        return "CRON"

    return "MANUAL"

def should_run_today(last_run_file: str) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(last_run_file):
        with open(last_run_file, "w") as f:
            f.write("")         # mark as never run
        return True             # first time running

    with open(last_run_file, "r") as f:
        last_run = f.read().strip()
    if last_run == today:
        return False

    return True

def mark_job_done():
    with open(LAST_RUN, "w") as f:
        f.write(today)

def run_job():
    subprocess.run(["python", JOB])

def clear_log_file(file_path: str):
    with open(file_path, "w"):
        pass

def main():
    trigger = detect_trigger_source()
    clear_log_file(LOG_FILE)
    log_json(log_dir='main', level='info', message=f"Script triggered by: {trigger}")
    log(f"Script triggered by: {trigger}", LOG_FILE)

    if trigger == "REBOOT" and now < time(14,0):
        log_json(log_dir='main', level='info', message=f"Script stopped, it's not time yet")
        return

    acquire_lock()

    if not should_run_today(LAST_RUN): # BLOCK THIS ON TESTING
        log_json(log_dir='main', level='info', message=f"Script already executed for today")
        log(f"Script already executed for today", LOG_FILE)
        sys.exit(0)

    run_job()
    mark_job_done()

if __name__ == "__main__":
    main()
