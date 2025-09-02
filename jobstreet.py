from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, date
import os

print('start')
driver = webdriver.Chrome() # headless not working

jobs = []
PAGE_LIMIT = 10
page = 1

while True:
    BASE_URL = f"https://ph.jobstreet.com/web-developer-jobs?daterange=1&pos=1&salaryrange=70000-&salarytype=monthly&workarrangement=2%2C3&page={page}"
    driver.get(BASE_URL)
    time.sleep(3) 

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.find_all("article")

    if not job_cards:
        break

    for job in job_cards:
        title_tag = job.find("a", {"data-automation": "jobTitle"})
        company_tag = job.find("a", {"data-automation": "jobCompany"})
        location_tag = job.find("span", {"data-automation": "jobLocation"})
        date_tag = job.find("span", {"data-automation": "jobListingDate"})
        job_link = title_tag.get("href") if title_tag else ""

        jobs.append({
            "title": title_tag.get_text(strip=True) if title_tag else "",
            "company": company_tag.get_text(strip=True) if company_tag else "",
            "location": location_tag.get_text(strip=True) if location_tag else "",
            "date_posted": date_tag.get_text(strip=True) if date_tag else "",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_link": f"https://ph.jobstreet.com{job_link}" if job_link else "",
        })
    page += 1
    if page >= PAGE_LIMIT:
        break

driver.quit()

# Save to CSV
folder_path = "datas"
os.makedirs(folder_path, exist_ok=True)
df = pd.DataFrame(jobs)
today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
file_path = os.path.join(folder_path, f"jobstreet_jobs_{formatted_date}.csv")
df.to_csv(file_path, sep=';', index=False)
print(f"Scraped {len(jobs)} jobs from JobStreet.")
