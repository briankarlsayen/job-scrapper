import re
from utils.utils import skill_extraction
from datetime import date

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")

def update_file_with_skills(filepath: str, output_path: str):

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Split posts by separator
    posts = text.split("================================================================")
    updated_posts = []

    for post in posts:
        post = re.sub(r"\nSkills:.*?(?=\n=+|$)", "", post, flags=re.DOTALL)
        if "Requirements:" in post:
            # Extract requirements block
            req_match = re.search(r"Requirements:\s*(.*)", post, flags=re.DOTALL)
            if req_match:
                requirements_text = req_match.group(1).strip()
                skills_found = skill_extraction(requirements_text)
                # print('skills_found: ', skills_found)

                if skills_found:
                    skills_section = "Skills:\n" + ",".join(skills_found) + "\n"
                    post = post.strip() + "\n" + skills_section
        updated_posts.append(post.strip())
        

    # Join back with separator
    updated_text = "\n================================================================\n".join(updated_posts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_text)

    # print(f"Updated file written to {output_path}")


# Example usage

input_path = f"./text/sample_job_1.txt"
output_path = f"./text/sample_job_1_updated.txt"

text_file_path = f"./text/job_req_{formatted_date}.txt"
update_text_file_path =  f"./text/jobs_with_skills_{formatted_date}.txt"
update_file_with_skills(input_path, output_path)