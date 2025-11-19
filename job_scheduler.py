#!/usr/bin/env python3
import fcntl
import os
from datetime import datetime, time
import sys
import subprocess
from utils.utils import log

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_DIR = BASE_DIR
JOB = "main.py"

LOCK_FILE = "/tmp/daily_job.lock"
FLAG_FILE = os.path.join(FLAG_DIR, f".daily_job_{datetime.now().strftime('%Y-%m-%d')}")
LOG_FILE = os.path.join(BASE_DIR, "logger.log")
now = datetime.now()

def acquire_lock():
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(0)  # Someone else is running
    return lock_fd


def detect_trigger_source():
    # Reboot cron job: using a flag passed in cron
    if "--reboot" in sys.argv:
        return "REBOOT"

    # Scheduled cron job (2pm)
    if "CRON" in os.getenv("PATH", "") or not os.isatty(0):
        return "CRON"

    # Otherwise, manual execution
    return "MANUAL"

def job_already_ran_today():
    return os.path.exists(FLAG_FILE)


def mark_job_done():
    with open(FLAG_FILE, "w") as f:
        f.write("done\n")


def run_job():
    subprocess.run(["python", JOB, "job_checker"])


def main():
    trigger = detect_trigger_source()
    log(f"Script triggered by: {trigger}", LOG_FILE)

    if trigger == "REBOOT" and now < time(14,0):
        return

    lock_fd = acquire_lock()

    if job_already_ran_today():
        sys.exit(0)

    run_job()
    mark_job_done()


if __name__ == "__main__":
    main()
