import os
from datetime import date
import pandas as pd

folder_path = "datas"
today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
csv_files = [f"./datas/jobstreet_jobs_{formatted_date}.csv", f"./datas/linkedin_jobs_{formatted_date}.csv"]

is_exist = True
for file in csv_files:
    if not os.path.exists(file):
        is_exist = False

if not is_exist:
    # run scraping
    print('start job scrape')
    os.system("python3 jobstreet.py")
    os.system("python3 linkedin.py")
    print('done job scrape')
    pass


# read data from todays csv
dfs = []
for file in csv_files:
    item = pd.read_csv(file, delimiter=";")
    dfs.append(item)

# df1 = pd.read_csv(csv_files[0], delimiter=";")
# df2 = pd.read_csv(csv_files[1], delimiter=";")

df = pd.concat(dfs, ignore_index=True)

# filter the jobs by title
remove_keywords = ["devops",  "servicenow", "qa", "quality assurance", "data", "solution", "shopify",  "salesforce", "japanese", "microsoft", "cloud", "automation", 
                   "SAP", "CRM", "game producer", "azure integration", "SEO specialist", "google ads", "web designer", "campaign executive",
                   "quality engineer", "infastructure", "system admin", "coordinator", "oracle", "administrator", "unity", "graphic designer", 
                   "security consultant", "marketing", "wordpress", "writer",
                   "ruby","java", ".net", "c#", "springboot", "laravel", "php",]
filtered_df = df[~df["title"].str.contains("|".join(remove_keywords), case=False, na=False)]

# create a csv jobs_today.csv
filtered_df.to_csv("jobs_today.csv",  sep=';', index=False)