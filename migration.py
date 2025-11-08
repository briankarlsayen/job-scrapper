import sqlite3
import pandas as pd
import os 

def create_schema(db_path: str):
    # Connect to SQLite DB (creates jobs.db if not exists)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Read schema from file
    with open("schema.sql", "r") as f:
        schema = f.read()

    # Execute schema
    cur.executescript(schema)

    conn.commit()
    conn.close()

def migrate(file: str):
    DB_FILE = "jobs.db"

    # check if db file exist, if not create file and create schema
    if not os.path.exists(DB_FILE):
        create_schema(DB_FILE)

    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Load CSV
    df = pd.read_csv(file, delimiter=";")

    for _, row in df.iterrows():
        title = row["title"].strip() if pd.notna(row["title"]) else None
        company = row["company"].strip() if pd.notna(row["company"]) else None
        location = row["location"].strip() if pd.notna(row["location"]) else None
        skills = row["required_skills"].strip().lower() if pd.notna(row["required_skills"]) else None
        scraped_date = None
        if pd.notna(row["scraped_at"]):
            scraped_date = str(row["scraped_at"]).strip()[:10]  

        url = row["job_link"].strip() if pd.notna(row["job_link"]) else None
        if url and url.count("https://ph.jobstreet.com") > 1:
            idx = url.rfind("https://ph.jobstreet.com")
            url = url[idx:]

        cur.execute("""
            INSERT OR IGNORE INTO jobs
            (title, company, location, skills, scraped_date, url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, company, location, skills, scraped_date, url))
    conn.commit()
    conn.close()
    print("✅ Migration complete: CSV data imported into jobs.db")

def migrate_all():
    folder_path = "datas"

    for dir in os.listdir(folder_path):
        dir_path = os.path.join(folder_path, dir)
        if os.path.isdir(dir_path):
            jobs_file = os.path.join(dir_path, "jobs.csv")
            linkedin_file = os.path.join(dir_path, "linkedin.csv")
            jobstreet_file = os.path.join(dir_path, "jobstreet.csv")
            if os.path.exists(jobs_file):
                print(f"'jobs.csv' found in: {dir_path}")
                migrate(jobs_file)
            else:
                if os.path.exists(linkedin_file):
                    print(f"'linkedin.csv' found in: {dir_path}")
                    migrate(linkedin_file)
                if os.path.exists(jobstreet_file):
                    print(f"'jobstreet.csv' found in: {dir_path}")
                    migrate(jobstreet_file)


# migrate(file="datas/2025_09_24/jobs.csv")

# order: create_schema > migrate_all
# create_schema()
# migrate_all()

