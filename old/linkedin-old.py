
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, date
import os

print('start')
# Configure Selenium (headless Chrome)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

jobs = []
page = 1
seen_links = set()
duplicates = 0
PAGE_LIMIT = 10

while True:

    BASE_URL = "https://www.linkedin.com/jobs/search?keywords=Web%20Developer&location=Philippines&geoId=103121230&f_TPR=r86400&f_WT=2%2C3&position=1&pageNum=0"

    driver.get(BASE_URL)
    time.sleep(3) 

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("ul.jobs-search__results-list li")

    if not job_cards:
        break


    for job in job_cards:
        title_tag = job.find("h3", {"class": "base-search-card__title"})
        company_tag = job.find("h4", {"class": "base-search-card__subtitle"})
        location_tag = job.find("span", {"class": "job-search-card__location"})
        date_tag = job.find("time", {"class": "job-search-card__listdate--new"})
        link_tag = job.find("a", {"class": "base-card__full-link"})
        job_link = link_tag.get("href") if title_tag else ""
        raw_link=job_link.split("?position")[0]


        if raw_link in seen_links:
            duplicates +=1
            continue  # Skip duplicate
        seen_links.add(raw_link)

        jobs.append({
            "title": title_tag.get_text(strip=True) if title_tag else "",
            "company": company_tag.get_text(strip=True) if company_tag else "",
            "location": location_tag.get_text(strip=True) if location_tag else "",
            "date_posted": date_tag.get_text(strip=True) if date_tag else "",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_link": raw_link if raw_link else "",
        })
    page += 1

    if duplicates >= 5:
        break

    if page >= PAGE_LIMIT:
        break

driver.quit()

# Save to CSV
folder_path = "datas"
os.makedirs(folder_path, exist_ok=True)
df = pd.DataFrame(jobs)
today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
file_path = os.path.join(folder_path, f"linkedin_jobs_{formatted_date}.csv")
df.to_csv(file_path, sep=';', index=False)
print(f"Scraped {len(jobs)} jobs from Linkedin.")
