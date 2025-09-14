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
[ ] job rating
--- [x] create classification by skills
--- [ ] weight skill differently, Programming Languages > JavaScript Libraries, etc
[ ] add this to ranking to main file
[ ] make error handler for main when scraper failed, run it 3x
[ ] automatic running: by my pc or raspi
[ ] linkedin scroll down to load new jobs

TIPS:

- to get skills I need data from others: ask skills from others, get skills from resume, etc

BUGS
[ ] C not listed when C, C++ exist
[ ] Git not listed when Git/Github
[ ] linkedin access scroll bottom to full content
