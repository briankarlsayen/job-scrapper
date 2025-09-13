import os
from datetime import date
import pandas as pd
import sys
from typing import List 
from constant import SEPARATOR

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
folder_path = f"./datas/{formatted_date}"
csv_files = [f"{folder_path}/jobstreet.csv", f"{folder_path}/linkedin.csv"]

is_exist = True
for file in csv_files:
    if not os.path.exists(file):
        is_exist = False

if not is_exist:
    # run scraping
    try:
        print('start job scrape')
        print('start jobstreet webscrape')
        os.system("python3 jobstreet.py")
        print('start linkedin webscrape')
        os.system("python3 linkedin.py")
        print('done job scrape')
    except Exception as e:
        print('Something went wrong!', e)
        sys.exit(1)
    pass


# read data from todays csv
dfs = []
for file in csv_files:
    item = pd.read_csv(file, delimiter=";")
    dfs.append(item)

df = pd.concat(dfs, ignore_index=True)

print('jobs: ', len(df))
df.to_csv(f"{folder_path}/jobs.csv",  sep=';', index=False)



def merge_txt_files(files: List[str], output_file: str):
    with open(output_file, "w", encoding="utf-8") as out:
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                out.write(f.read())

files_to_merge = [f"{folder_path}/jobstreet.txt", f"{folder_path}/linkedin.txt"]
merge_txt_files(files_to_merge, f"{folder_path}/jobs.txt")
print('text yeah')