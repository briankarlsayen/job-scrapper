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
now = datetime.now().time()
today = datetime.now().strftime("%Y-%m-%d")

LAST_RUN = "last_run.txt"

# TODO clean up
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

# def job_already_ran_today():
#     if os.path.exists(LAST_RUN):
#         with open(LAST_RUN, "r") as f:
#             last_run_date = f.read().strip()
#     return last_run_date == today


#     return os.path.exists(FLAG_FILE)

def should_run_today(last_run_file: str) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")

    # Create file if it does not exist
    if not os.path.exists(last_run_file):
        with open(last_run_file, "w") as f:
            f.write("")         # mark as never run
        return True             # first time running

    # Read last run date
    with open(last_run_file, "r") as f:
        last_run = f.read().strip()

    # If script already ran today → skip
    if last_run == today:
        return False

    # Otherwise → allowed to run
    return True


def mark_job_done():

    with open(LAST_RUN, "w") as f:
        f.write(today)

    # with open(FLAG_FILE, "w") as f:
    #     f.write("done\n")


def run_job():
    subprocess.run(["python", JOB])


def main():
    trigger = detect_trigger_source()
    log(f"Script triggered by: {trigger}", LOG_FILE)

    if trigger == "REBOOT" and now < time(14,0):
        return

    lock_fd = acquire_lock()

    if not should_run_today(LAST_RUN):
        print('done')
        sys.exit(0)

    print('run')
    run_job()
    mark_job_done()


if __name__ == "__main__":
    main()
