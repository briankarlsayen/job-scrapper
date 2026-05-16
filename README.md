# Job Scraper

### Functionalities

- scrape jobs from job boards daily(linkedin, jobstreet)
- show the jobs that I can apply to

### Install packages

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

### Install chromedriver

- note: update "/usr/bin/chromedriver" to match chromedriver path

```
sudo apt update
sudo apt install chromium-browser chromium-chromedriver -y
```

### Run script

```
python main.py
```

### Using python env

1. On terminal activate python env

```
source /[env folder name]/bin/activate
```

2. On VSCode click: alt + shift + p then search `Python: Select Interpreter` then find the env folder the click on the python3 file ex.( /[env folder/bin/python3])
3. Click the play button to run the application

### Using cron

- using cron, run every 1400

```
0 14 * * * /bin/bash -c "cd /[main folder path]/ && source [python env folder path]/bin/activate && python job_scheduler.py"
```

- handle missed jobs, run after 60 sec on startup

```
@reboot /bin/bash -c "sleep 60 && cd /[main folder path]/ && source [python env folder path]/bin/activate && python job_scheduler.py --reboot"

```

### Testing

- when testing check the comments that has --- TESTING ---

### TODOS

```
TIPS:

- to get skills I need data from others: ask skills from others, get skills from resume, etc

BUGS
[ ] C not listed when C, C++ exist
[ ] Git not listed when Git/Github

ENCHANCEMENT

[ ] raspi transfer
--- [x] run script, fix dependencies
--- [ ] run as cronjob
--- [ ] handle missed jobs
[ ] data analysis, research on how to make sense of data(need to scrape longer first ---> 01-2026 task )
[x] improve logs
--- [x] delete old logs --- <14days
--- [x] delete old data --- <30days
--- [x] delete screenshots --- <14days
--- [x] convert to json, add types (INFO, WARNING, ERROR)
--- [x] create logs/main, store logs on the main.py
[x] handle errors
--- [x] setup a system on sending errors (email, sms)
[ ] create a test file, for improvement checking
[ ] employment type(full time, contract, part time)
[ ] salary(if range then max/min)
[ ] work arrangement(remote, onsite, hybrid)
```
