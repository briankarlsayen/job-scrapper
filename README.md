# Job Scraper

### Functionalities

- scrape jobs from job boards daily(linkedin, jobstreet)
- show the jobs that I can apply to

TODOS
[ ] further filter by checking the job post requirements
--- [ ] pass the requirements and nice to the nlp filter
--- [ ] create a csv file, add requirements, requirement score(12/14), failed requirement(seo,java,php), nice to haves, nth score, failed nth, status(passed or failed)

BUG
[ ] linkedin access scroll bottom to full content

importants: [requirement, preferred experience, preferred qualification, for this role you will need, qualification, what we ask of you, ]

- strong/p
- has ul's

others: [nice to have,]

TODO --------------> i need data!

[x] create a file containing all requirements, have it separated but maintain it in one txt file
[x] expand skills.json (ex. react, reactjs, react.js)
[x] update filter by job title, remove language filter
[x] get skills for job_req file, manually validate the accuracy, (process_text_file)
--- [x] if accurate enough <=90%, then proceed, else retry
[x] apply skill_extration to linkedin-updated
[x] save format
--- [x] create a folder based on date
--- [x] inside folder create text and csv files
[x] update saved excel file to have required skill
[x] create same skill extractor for jobstreet
[x] fix extracted skill - PHP, Java
[ ] include bullet char job requirements
[ ] add job title to the skill extractor
[ ] add job rating, classification: by job title, skills
[ ] automatic running: by my pc or raspi
TIPS:

- to get skills I need data from others: ask skills from others, get skills from resume, etc
