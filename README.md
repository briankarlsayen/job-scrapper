# Job Scraper

### Functionalities

- scrape jobs from job boards daily(linkedin, jobstreet)
- show the jobs that I can apply to

TODOS
[x] further filter by checking the job post requirements
--- [x] pass the requirements and nice to the nlp filter
--- [x] create a csv file, add requirements, requirement score(12/14), failed requirement(seo,java,php), nice to haves, nth score, failed nth, status(passed or failed)
[x] create a file containing all requirements, have it separated but maintain it in one txt file
[x] expand skills.json (ex. react, reactjs, react.js)
[x] update filter by job title, remove language filter
[x] get skills for job_req file, manually validate the accuracy, (process_text_file)
--- [x] if accurate enough <=90%, then proceed, else retry
[x] apply skill_extration to linkedin-updated
[x] save formatw
--- [x] create a folder based on date
--- [x] inside folder create text and csv files
[x] update saved excel file to have required skill
[x] create same skill extractor for jobstreet
[x] fix extracted skill - PHP, Java
[x] include bullet char job requirements
[x] add job title to the skill extractor
[x] job rating
--- [x] create classification by skills
--- [x] weight skill differently, Programming Languages > JavaScript Libraries, etc
--- [x] create text file that shows the inputed skills for the ranked_jobs file
[x] make error handler for main when scraper failed, run it 3x
[x] add this to ranking to main file
[x] fix the ranked_jobs file, still include the unmatched jobs, watch for changes in scores
[x] when jobs.csv exist delete duplicate csv and txt files
[x] lk scroll loading
--- [x] fix unreliable modal clicker, if not clicked stop operation
--- [x] apply to main file
[x] get all ul,li, and strings with bullet points for requirements
[ ] automatic running: by my pc or raspi
--- [x] run headless
--- [x] test run on 2pm next day
--- [ ] if cron time today has passed, run in at once (check anacron)
[x] save to data database
--- [x] setup db schema
--- [x] import csv data to db
--- [x] save new data to db
[x] cron job
--- [x] create cron job
--- [x] handle missed job
--- [x] create log when job triggered
[ ] raspi transfer
--- [x] run script, fix dependencies
--- [x] run as cronjob
--- [x] handle missed jobs
[ ] data analysis
[ ] logs
--- [ ] create logs on unsuccessful run
--- [ ] create on start/end run

TIPS:

- to get skills I need data from others: ask skills from others, get skills from resume, etc

BUGS
[ ] C not listed when C, C++ exist
[ ] Git not listed when Git/Github
[x] test linkedin not equal number scraped, test for duplicate titles, lk not logged has duplicate jobs(sites problem issue)
[x] handle if scraper failed, do not create a csv
[ ] no db schema once installed, create a schema first before running main.py, create jobs.db > migrate schema > run main.py

ENCHANCEMENT
[ ] add log for end scraping
[ ] create a test file, for improvement checking
[ ] employment type(full time, contract, part time)
[ ] salary(if range then max/min)
[ ] work arrangement(remote, onsite, hybrid)

## INSTALL PACKAGES

- using requirements.txt

```
pip install -r requirements.txt
```

- or manually, with spacy matching

```
pip install pandas selenium sqlite3 spacy bs4
```

```
python -m spacy download en_core_web_sm
```

## INSTALL CHROMEDRIVER

- note: update "/usr/bin/chromedriver" to match chromedriver path

```
sudo apt update
sudo apt install chromium-browser chromium-chromedriver -y
```

## RUN SCRIPT

```
python main.py
```
