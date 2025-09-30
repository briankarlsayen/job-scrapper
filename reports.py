import sqlite3
from collections import Counter
from datetime import date

# filter by today, this week, this month, this year, all 
# filter by skill classification, Programming Languages | Web Development | Cloud & DevOps
def get_skills_stats(date_range="today"):
    

    # Connect to your database
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    # Fetch all skills from table
    if date_range == "today":
        today = date.today().isoformat()
        cursor.execute("SELECT skills FROM jobs WHERE DATE(scraped_date) = ?", (today,))
    elif date_range == "all":
        cursor.execute("SELECT skills FROM jobs")
    else:
        conn.close()
        raise ValueError("date_range must be 'today' or 'all'")
    rows = cursor.fetchall()

    # Count skills
    all_skills = []
    for row in rows:
        if row[0]:
            skills = [s.strip().lower() for s in row[0].split(",")]
            all_skills.extend(skills)

    conn.close()
    return Counter(all_skills).most_common()
    # return dict(Counter(all_skills))

print('skills', get_skills_stats(date_range="all"))