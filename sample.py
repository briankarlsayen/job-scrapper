import os
from utils import logger

logger()

folder_path = "dummy"
os.makedirs(folder_path, exist_ok=True)

count = 0

with os.scandir(folder_path) as entries:
    for entry in entries:
        if entry.is_file():
            file_name = entry.name.split(".")[0]
            if int(file_name):
                count = int(file_name) if int(file_name) > count else count


# create file
open(f"{folder_path}/{count + 1}.txt", "w").close()