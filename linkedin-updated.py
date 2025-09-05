
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
from utils import save_to_textfile, skill_extraction, validate_job_title

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
separator = "================================================================"


today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
job_requirement_list = []

# def extract_section(soup, headers):
#     """
#     Extracts the <ul><li> list under the first matching header.

#     :param soup: BeautifulSoup object
#     :param headers: list of keywords/phrases to search (case-insensitive)
#     :return: list of strings (requirements), or empty list if not found
#     """
#     results = set()  # use set to avoid duplicates

#     header_tags = soup.find_all(
#         lambda tag: tag.name in ["h2", "h3", "h4", "p", "strong"]
#         and any(h.lower() in tag.get_text(strip=True).lower() for h in headers)
#     )

#     for header_tag in header_tags:
#         ul = header_tag.find_next("ul")
#         if ul:
#             for li in ul.find_all("li"):
#                 results.add(li.get_text(strip=True))  # set keeps only unique

#     return list(results)

# def extract_section(driver, headers):
#     header_tags = driver.find_elements(By.CSS_SELECTOR, "h2, h3, h4, p, strong")

#     for header in header_tags:
#         header_text = header.text.strip().lower()
#         print('header_text', header_text)
#         if any(h.lower() in header_text for h in headers):
#             try:
#                 # Find the next <ul> sibling under this header
#                 ul = header.find_element(By.XPATH, "following-sibling::ul[1]")
#                 li_elements = ul.find_elements(By.TAG_NAME, "li")
#                 return [li.text.strip() for li in li_elements if li.text.strip()]
#             except:
#                 continue  # no <ul> after this header, keep searching
#     return []

def extract_section(container, headers):
    if not container:
        return []

    results = set()

    header_tag = container.find(
        lambda tag: tag.name in ["h2", "h3", "h4", "p", "strong"]
        and any(h.lower() in tag.get_text(strip=True).lower() for h in headers)
    )

    if not header_tag:
        return []

    for sibling in header_tag.find_all_next():
        if sibling.name in ["button"]:
            break  # stop at next section header

        if sibling.name == "ul":
            for li in sibling.find_all("li"):
                text = li.get_text(strip=True)
                if text:  # skip empty
                    results.add(text)

    return list(results)


while True:
    BASE_URL = f"https://www.linkedin.com/jobs/search?keywords=Software%20Engineer&location=Philippines&geoId=103121230&f_TPR=r86400&f_WT=3%2C2&position=1"
    driver.get(BASE_URL)
    time.sleep(3) 
    wait = WebDriverWait(driver, 10)

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
        # driver.execute_script("arguments[0].click();", close_button)
        print("No modal or not clickable:", e)
        # break

    job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.jobs-search__results-list li")))

    if not job_cards:
        break

    items = 0

    print('Unfiltered jobs: ', len(job_cards))

    requirement_datas = []

    for job in job_cards:
        time.sleep(1)

        # if items >= 5: # limit to first 5
        #     break

        title_tag = job.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
        title_text = title_tag.text.strip()

        if not validate_job_title(title_text):
            continue

        print('Job Title: ', title_text)
        
        job.click()
        items += 1 

        time.sleep(8)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_description = soup.select_one("div.show-more-less-html__markup")

        requirement_headers = ["qualification", "require", 
                               "must have", "skills", "responsibilities",
                               "what you will bring to the team", "about you",
                               "what we’re looking for"
                               ]
        nice_to_have_headers = ["nice to have", "preferred", "bonus points"]
        headers = requirement_headers + nice_to_have_headers

        requirement_list = extract_section(job_description, headers)

        link_tag = job.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
        job_link = link_tag.get_attribute("href") if link_tag else ""
        raw_link = job_link.split("?position")[0] if job_link else ""

        required_skills = skill_extraction("\n".join(requirement_list))

        company_tag = job.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
        company_text = company_tag.text.strip()
        location_tag = job.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
        location_text = location_tag.text.strip()
        link_tag = job.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
        job_link = link_tag.get_attribute("href") if link_tag else ""
        raw_link = job_link.split("?position")[0] if job_link else ""

        if raw_link in seen_links:
            duplicates +=1
            continue  # Skip duplicate
        seen_links.add(raw_link)

        job_requirement_list.extend(["Title: " + title_text, "Company: " + company_text, "Link: " + raw_link, "Requirements:"])
        job_requirement_list.extend(requirement_list)
        job_requirement_list.append(separator)

        jobs.append({
            "title": title_text if title_tag else "",
            "company": company_text if company_tag else "",
            "location": location_text if location_tag else "",
            "date_posted": "",
            # "date_posted": date_text if date_tag else "",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_link": raw_link if raw_link else "",
            "required_skills": ",".join(required_skills) if len(required_skills) else "",
        })
    page += 1

    if duplicates >= 5:
        break

    if page >= PAGE_LIMIT:
        break

driver.quit()

save_to_textfile(f"job_req_{formatted_date}.txt", "\n".join(job_requirement_list))

# Save to CSV
folder_path = "datas"
os.makedirs(folder_path, exist_ok=True)
df = pd.DataFrame(jobs)
today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
file_path = os.path.join(folder_path, f"linkedin_jobs_{formatted_date}.csv")
df.to_csv(file_path, sep=';', index=False)
print(f"Scraped {len(jobs)} jobs from Linkedin.")
