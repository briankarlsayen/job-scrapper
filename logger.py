import sys
from datetime import datetime
from pathlib import Path

LAST_RUN = "last_run.txt"
today = datetime.now().strftime("%Y-%m-%d")
now = datetime.now()

def logger_script():
    log_file = Path(__file__).parent / "logger.log"

    def log(message):
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    
    source = sys.argv[1] if len(sys.argv) > 1 else "manual"
    log(f"Script triggered by: {source}")

    with open(LAST_RUN, "w") as f:
        f.write(today)