
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, date
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import save_to_textfile
print('start')
# Configure Selenium (headless Chrome)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome()
driver.set_window_size(1920, 1080)

jobs = []
page = 0
seen_links = set()
duplicates = 0
PAGE_LIMIT = 10
page_item_count = 25

def extract_section(soup, headers):
    """
    Extracts the <ul><li> list under the first matching header.

    :param soup: BeautifulSoup object
    :param headers: list of keywords/phrases to search (case-insensitive)
    :return: list of strings (requirements), or empty list if not found
    """
    # Look for any tag that contains one of the headers
    header_tag = soup.find(
        lambda tag: tag.name in ["h2", "h3", "h4", "p", "strong"]
        and any(h.lower() in tag.get_text(strip=True).lower() for h in headers)
    )

    if header_tag:
        ul = header_tag.find_next("ul")
        if ul:
            return [li.get_text(strip=True) for li in ul.find_all("li")]
    return []


while True:

    BASE_URL = f"https://www.linkedin.com/jobs/search?keywords=Software%20Engineer&location=Philippines&geoId=103121230&f_TPR=r86400&f_WT=3%2C2&position=1"
    # BASE_URL = f"https://www.linkedin.com/jobs/search/?f_TPR=r86400&f_WT=2%2C3&geoId=103121230&keywords=Web%20Developer&location=Philippines&start={page*page_item_count}"
    # BASE_URL = f"https://www.linkedin.com/jobs/search?keywords=Web%20Developer&location=Philippines&geoId=103121230&f_TPR=r86400&f_WT=2%2C3&position=1&pageNum={page}"
    print('BASE_URL', BASE_URL)

    driver.get(BASE_URL)
    time.sleep(3) 
    wait = WebDriverWait(driver, 10)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    close_button = ""

    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                'button[data-tracking-control-name="public_jobs_contextual-sign-in-modal_modal_dismiss"]'))
        )
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
        
        close_button.click()
        print("Login modal closed ✅")
    except Exception as e:
        driver.execute_script("arguments[0].click();", close_button)
        print("No modal or not clickable:", e)
        # break

    job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.jobs-search__results-list li")))

    if not job_cards:
        break


    print('job_card', job_cards[0])
    job_cards[0].click()
    job_description = soup.select_one("div.show-more-less-html__markup")

    requirement_headers = ["requirements", "qualifications", "must have", "skills required", "responsibilities"]
    nice_to_have_headers = ["nice to have", "preferred", "bonus points"]

    requirement_list = extract_section(job_description, requirement_headers)
    nice_to_have_list = extract_section(job_description, nice_to_have_headers)
    # text = job_description.get_text(separator="\n", strip=True)
    save_to_textfile("job_req.text", "\n".join(requirement_list))
    save_to_textfile("job_nice.text", "\n".join(nice_to_have_list))


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
