from utils import save_to_textfile, skill_extraction, validate_job_title
from datetime import datetime, date
job_requirement_list = ['hahaha', 'hahaha', 'hahaha']

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")
save_to_textfile(f"./text/job_req_{formatted_date}.txt", "\n".join(job_requirement_list))
