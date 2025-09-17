
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time, random
from datetime import datetime, date
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import save_to_textfile, skill_extraction, validate_job_title
from selenium.common.exceptions import NoSuchElementException
from constant import PREFERRED_KEYWORDS, REQ_KEYWORDS, BULLET_CHARS
from selenium.webdriver.chrome.service import Service

print('start')
# Configure Selenium (headless Chrome)
# brave_path = "/snap/bin/brave"

options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
# options.binary_location = brave_path
# service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(options=options)
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

MAX_SCROLLS = 5

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
        elif sibling.string:
            raw_text = sibling.get_text(strip=True)
            if raw_text and any(raw_text.startswith(b) for b in BULLET_CHARS):
                cleaned = raw_text.lstrip("".join(BULLET_CHARS)).replace("\xa0", " ")
                cleaned = " ".join(cleaned.split())  # normalize spaces
                if cleaned:
                    results.add(cleaned)

    return list(results)


def safe_find_element(parent, by: By, value: str):
    try:
        return parent.find_element(by, value)
    except NoSuchElementException:
        return None

while True:
    BASE_URL = f"https://www.linkedin.com/jobs/search?keywords=Software%20Engineer&location=Philippines&geoId=103121230&f_TPR=r86400&f_WT=3%2C2&position=1"
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 30)
    
    time.sleep(10)

    close_button = ""
    try:
        overlay = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal__overlay"))
        )
        # Now search inside the overlay for the close button
        close_button = overlay.find_element(By.XPATH, "//button[contains(@class, 'modal__dismiss')]")
        driver.execute_script("arguments[0].click();", close_button)
        print("Login modal closed ✅")
    except Exception as e:
        # driver.execute_script("arguments[0].click();", close_button)
        print("No modal or not clickable:", e)
        # break

    driver.refresh()


    # if not job_cards:
    #     break

    scroll_load_limit = 10
    scroll_load = scroll_load_limit


    while True:
        # Scroll to bottom of results list
        found_end = False        
        loader_timeout = False

        try:
            footer = driver.find_element(By.CLASS_NAME, "see-more-jobs__viewed-all")
            if footer.is_displayed():
                print("Reached end of job list!")
                break
        except:
            # footer not yet visible, continue scrolling
            pass

        for _ in range(10):
            print('haha')
            for _ in range(30):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(random.uniform(0.5, 1.5))
            time.sleep(2)
            # loader_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".loader.loader--show")))
            # wait.until(EC.invisibility_of_element(loader_element))
            loader_element = safe_find_element(driver, By.CSS_SELECTOR, ".loader.loader--show")

            footer = driver.find_element(By.CLASS_NAME, "see-more-jobs__viewed-all")
            if footer.is_displayed():
                found_end = True
                break
            
            # end_list = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.see-more-jobs__viewed-all")))
            # end_list = safe_find_element(driver, By.CSS_SELECTOR, ".see-more-jobs__viewed-all")

            # if end_list:
            #     print('found end!')
            #     found_end = True
            #     break
            if not loader_element:
                print('no loading icon')
                pass
            elif loader_element.is_displayed():
                print('loading icon found')
                found_end = True
                scroll_load -= 1
                break


                
        # try:
        #     # Wait for loader to show up
        #     loader = safe_find_element(driver, By.CSS_SELECTOR, ".loader.loader--show")
        #     # Wait until loader disappears (new jobs loaded)
        #     wait.until(EC.invisibility_of_element(loader))
        # except Exception:
        #     # No loader means no more jobs
        #     print('No more jobs to load')
        #     break
        time.sleep(5)

        if not found_end or scroll_load <= 0:
            print('done process jobs')
            break


    job_cards = []
    try:
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.jobs-search__results-list li")))
    except:
        print('No jobs scraped')
        break
    items = 0

    print('Unfiltered jobs: ', len(job_cards))
    requirement_datas = []

    for job in job_cards:
        time.sleep(.5)
        # if items >= 5: # limit to first 5
        #     break

        title_tag = safe_find_element(job, By.CSS_SELECTOR, "h3.base-search-card__title")
        title_text = title_tag.text.strip() if title_tag else None
        # if not validate_job_title(title_text):
        #     print('Not valid job :', title_text)
        #     continue

        link_tag = safe_find_element(job, By.CSS_SELECTOR, "a.base-card__full-link")
        job_link = link_tag.get_attribute("href") if link_tag else None
        raw_link = job_link.split("?position")[0] if job_link else None
        company_tag = safe_find_element(job, By.CSS_SELECTOR, "h4.base-search-card__subtitle")
        company_text = company_tag.text.strip() if company_tag else None
        location_tag = safe_find_element(job, By.CSS_SELECTOR, "span.job-search-card__location")
        location_text = location_tag.text.strip() if location_tag else None
        date_tag = safe_find_element(job, By.CSS_SELECTOR, "time.job-search-card__listdate--new")
        date_text = date_tag.text.strip() if date_tag else None

        if raw_link in seen_links:
            print('dups')
            duplicates +=1
            continue  # Skip duplicate
        seen_links.add(raw_link)

        # job.click()
        items += 1 

        # current_url = driver.current_url
        # if "/jobs/view/" in current_url:
        #     driver.back()  # go back to previous results page
        #     time.sleep(2)  # wait to reload results page
        #     break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        # job_description = soup.select_one("div.show-more-less-html__markup")
        # if not job_description:
        #     continue

        jobs.append({
            "title": title_text if title_text else "N/A",
            "company": company_text if company_text else "N/A",
            "location": location_text if location_text else "N/A",
            "date_posted": date_text if date_text else "N/A",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_link": raw_link if raw_link else "N/A",
        })
    break
    page += 1

    # scroll down

    if duplicates >= 5:
        break

    if page >= PAGE_LIMIT:
        break

driver.quit()

def create_job_folder(folder_name: str, file_name: str, text_content: str, csv_content: list):
    text_file_name = f"{file_name}.txt"
    csv_file_name = f"{file_name}.csv"
    folder_path =  os.path.join("datas", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    text_file_path = os.path.join(folder_path, text_file_name)
    csv_file_path = os.path.join(folder_path, csv_file_name)

    # create text file
    # save_to_textfile(text_file_path, text_content)
    # create csv file
    df = pd.DataFrame(csv_content)
    df.to_csv(csv_file_path, sep=';', index=False)

create_job_folder(folder_name=formatted_date, file_name="test-linkedin", text_content="\n".join(job_requirement_list), csv_content=jobs)
print(f"Scraped {len(jobs)} jobs from Linkedin.")