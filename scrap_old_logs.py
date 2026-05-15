from pathlib import Path
from datetime import datetime, timedelta
import shutil

def delete_expired_logs(log_dir: str, format: str, days: int = 14):
    log_path = Path(log_dir)
    cutoff_date = datetime.now().date() - timedelta(days=days)

    for item in log_path.iterdir():
        try:
            date_str = item.stem if item.is_file() else item.name
            file_date = datetime.strptime(date_str, format).date()
            if file_date < cutoff_date:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        except ValueError:
            continue

def scrap_old_logs():
    delete_expired_logs('logs/linkedin', "%Y_%m_%d", 14) # text logs
    delete_expired_logs('screenshots', "%Y%m%d_%H%M%S", 14) # ss
    delete_expired_logs('datas', "%Y_%m_%d", 30) # files
    delete_expired_logs('logs/main', "%Y_%m_%d", 30) # text main logs
