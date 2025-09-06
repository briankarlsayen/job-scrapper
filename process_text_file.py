import re
from utils import skill_extraction

def extract_requirements(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Find blocks that start with "Requirements:" and end before "====="
    matches = re.findall(r"Requirements:\s*(.*?)={5,}", text, flags=re.DOTALL)

    all_requirements = []
    for block in matches:
        # Split by line, remove empty ones
        items = [line.strip() for line in block.splitlines() if line.strip()]
        all_requirements.extend(items)

    return all_requirements

# Example usage
# requirements = extract_requirements("./process_job.txt")
# print(requirements)

def update_file_with_skills(filepath: str, output_path: str):

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Split posts by separator
    posts = text.split("================================================================")
    updated_posts = []

    for post in posts:
        if "Requirements:" in post:
            # Extract requirements block
            req_match = re.search(r"Requirements:\s*(.*)", post, flags=re.DOTALL)
            if req_match:
                requirements_text = req_match.group(1).strip()
                skills_found = skill_extraction(requirements_text)
                print('skills_found: ', skills_found)

                if skills_found:
                    skills_section = "Skills:\n" + ",".join(skills_found) + "\n"
                    # Insert skills section before trailing whitespace
                    post = post.strip() + "\n" + skills_section
        updated_posts.append(post.strip())
        

    # Join back with separator
    updated_text = "\n================================================================\n".join(updated_posts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_text)

    # print(f"Updated file written to {output_path}")


# Example usage
update_file_with_skills("process_job.txt", "jobs_with_skills.txt")