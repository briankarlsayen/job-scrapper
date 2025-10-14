
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time, random
from datetime import datetime, date
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from utils import save_to_textfile, skill_extraction, validate_job_title
from selenium.common.exceptions import NoSuchElementException
from constant import BULLET_CHARS, SEPARATOR
from selenium.webdriver.chrome.service import Service
import sys

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                      "AppleWebKit/537.36 (KHTML, like Gecko) "
#                      "Chrome/115.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = Service("/usr/bin/chromedriver") # chromedriver path
driver = webdriver.Chrome(service=service, options=options)
driver.set_window_size(1920, 1080)

jobs = []
seen_links = set()
separator = SEPARATOR

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
job_requirement_list = []

def extract_section(container):
    if not container:
        return []
    results = set()

    elements = container.find_all(string=True)
    for el in elements:
        raw_text = el.get_text(strip=True)
        if raw_text and any(raw_text.startswith(b) for b in BULLET_CHARS):
            cleaned = raw_text.lstrip("".join(BULLET_CHARS)).replace("\xa0", " ")
            cleaned = " ".join(cleaned.split())  # normalize spaces
            if cleaned:
                results.add(cleaned)
    
    uls = container.find_all("ul")
    for ul in uls:
        lis = ul.find_all("li")
        for li in lis:
            text = li.get_text(" ", strip=True)
            if text:
                results.add(text)

    return list(results)

def safe_find_element(parent, by: By, value: str):
    try:
        return parent.find_element(by, value)
    except NoSuchElementException:
        return None
    
def is_loading_shown(driver) -> bool:
    loader_element = safe_find_element(driver, By.CSS_SELECTOR, ".loader.loader--show")
    if not loader_element:
        return False
    if loader_element.is_displayed():
        return True
    return False

def is_viewed_all_shown(driver) -> bool:
    viewed_all_element = safe_find_element(driver, By.CLASS_NAME, "see-more-jobs__viewed-all")
    if not viewed_all_element:
        return False
    if viewed_all_element.is_displayed():
        return True
    return False


def process_job_scrape(driver, reload=False):
    retry = False
    BASE_URL = f"https://www.linkedin.com/jobs/search?keywords=Software%20Engineer&location=Philippines&geoId=103121230&f_TPR=r86400&f_WT=3%2C2&position=1"

    try:
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 30)
    except TimeoutException as e:
        if reload == False:
            # driver.refresh()
            process_job_scrape(driver, reload=True)
        message = str(e).split("\n")[0]
        print(f"TimeoutException: {message}", file=sys.stderr)
        return

    except WebDriverException as e:
        message = str(e).split("\n")[0]
        print(f"WebDriverException: {message}", file=sys.stderr)
        return

    except Exception as e:
        message = str(e).split("\n")[0]
        print(f"UnexpectedError: {message}", file=sys.stderr)
        return

    # driver.get(BASE_URL)
    # wait = WebDriverWait(driver, 30)
    duplicates = 0 

    # close login modal
    def close_modal(driver) -> bool:
        retry = 3
        retry_failed = False
        while True:
            try:
                modal_container = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.top-level-modal-container"))
                )

                overlay = safe_find_element(modal_container, By.CSS_SELECTOR, "div.modal__overlay")
                if not overlay:
                    break

                close_button = overlay.find_element(By.XPATH, "//button[contains(@class, 'modal__dismiss')]")
                driver.execute_script("arguments[0].click();", close_button)

                if retry <=0:
                    retry_failed = True
                    break
                retry -= 1
                time.sleep(3)
            except Exception as e:
                print("No modal or not clickable:", e)
        if retry_failed:
            print('Retries Failed')
            return False
        else:
            print('Successfully closed modal')
            return True

    time.sleep(5)
    is_modal_closed = close_modal(driver)
    if not is_modal_closed:
        return
    time.sleep(1)

    # handle scroll lazy loading
    def load_all_jobs():
        found_end = False        
        loading_shown = False
        loading_retry = 3
        success = False

        while True:
            if is_viewed_all_shown(driver):
                success = True
                break

            if loading_shown:
                if loading_retry <= 0:
                    found_end = True
                    break
                elif is_loading_shown(driver):
                    loading_retry -= 1
                else:
                    loading_retry = 3
                    loading_shown = False
                time.sleep(2)

            for _ in range(10):
                if found_end or loading_shown:
                    break
                for _ in range(30):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(random.uniform(0.5, 1.5))
                    if is_viewed_all_shown(driver):
                        found_end = True
                        break
                    elif is_loading_shown(driver):
                        loading_shown = True
                        time.sleep(5) # wait for loading to stop
                        break

                    loading_shown = False
                    loading_retry = 3
                time.sleep(2)

            if found_end:
                break
        
        return success
    success = load_all_jobs() 
    if not success:
        print('Processing partial jobs')

    job_cards = []
    try:
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.jobs-search__results-list li")))
    except:
        print('No jobs scraped')
        return
    if not job_cards:
        return

    items = 0

    print('Unfiltered jobs: ', len(job_cards))

    for job in job_cards:
        time.sleep(1)
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
            duplicates +=1
            continue  # Skip duplicate
        seen_links.add(raw_link)

        job.click()
        items += 1 
        time.sleep(8)
        
        # if items > 5: # TODO test
        #     break

        current_url = driver.current_url
        if "/jobs/view/" in current_url:
            driver.back()  # go back to previous results page
            time.sleep(2)  # wait to reload results page
            retry = True
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")        
        job_description = soup.select_one("div.show-more-less-html__markup")
        
        if not job_description:
            continue

        requirement_list = extract_section(job_description)
        extraction_list = [title_text] + requirement_list
        required_skills = skill_extraction("\n".join(extraction_list))

        job_requirement_list.extend(["Title: " + title_text if title_text else "N/A", 
                                     "Company: " + company_text if company_text else "N/A", 
                                     "Link: " + raw_link if raw_link else "N/A", 
                                     "Requirements:"])
        job_requirement_list.extend(requirement_list)
        # <---------- SKILLS section
        job_requirement_list.extend(['Skills:'])
        if len(required_skills):
            job_requirement_list.extend([",".join(required_skills)]) 
        # -------------------------->
        job_requirement_list.append(separator)

        jobs.append({
            "title": title_text if title_text else "N/A",
            "company": company_text if company_text else "N/A",
            "location": location_text if location_text else "N/A",
            "required_skills": ",".join(required_skills) if len(required_skills) else "N/A",
            "date_posted": date_text if date_text else "N/A",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_link": raw_link if raw_link else "N/A",
        })
    return retry
    
retry = True
is_error = False
while retry:
    try:
        retry = process_job_scrape(driver, reload=False)
    except Exception as e:
        is_error = True
        
if is_error:
    driver.quit()
    sys.exit(2)

driver.quit()

if not job_requirement_list or not jobs:
    sys.exit(1)

def create_job_folder(folder_name: str, file_name: str, text_content: str, csv_content: list):
    text_file_name = f"{file_name}.txt"
    csv_file_name = f"{file_name}.csv"
    folder_path =  os.path.join("datas", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Force permission (rwxrwxr-x = 775)
    os.chmod(folder_path, 0o775)

    text_file_path = os.path.join(folder_path, text_file_name)
    csv_file_path = os.path.join(folder_path, csv_file_name)

    # create text file
    save_to_textfile(text_file_path, text_content)
    # create csv file
    df = pd.DataFrame(csv_content)
    df.to_csv(csv_file_path, sep=';', index=False)

create_job_folder(folder_name=formatted_date, file_name="linkedin", text_content="\n".join(job_requirement_list), csv_content=jobs)
print(f"Scraped {len(jobs)} jobs from Linkedin.")


