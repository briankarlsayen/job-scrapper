import sqlite3
import pandas as pd
import os 
from glob import glob

DB_FILE = "jobs.db"

def create_schema(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    with open("schema.sql", "r") as f:
        schema = f.read()

    cur.executescript(schema)
    conn.commit()
    conn.close()

def migrate(file: str):
    if not os.path.exists(DB_FILE):
        create_schema(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

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

def merge_databases():
    # This is for merging multiple databases
    # Rename the db file ex. a.db, b.db
    DB_FOLDER = "db_folder"
    INDEX_DB = "index.db"
    os.makedirs(DB_FOLDER, exist_ok=True)

    if not os.path.exists(f"{DB_FOLDER}/{INDEX_DB}"):
        create_schema(f"{DB_FOLDER}/{INDEX_DB}")

    index_conn = sqlite3.connect(f"{DB_FOLDER}/{INDEX_DB}")
    index_cur = index_conn.cursor()
    db_files = glob(os.path.join(DB_FOLDER, "*.db"))
    
    for db_file in db_files:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT title, company, location, skills, scraped_date, url FROM jobs")
        rows = cur.fetchall()
        for row in rows:
            index_cur.execute("""
            INSERT OR IGNORE INTO jobs
            (title, company, location, skills, scraped_date, url)
            VALUES (?, ?, ?, ?, ?, ?)
            """, row)
        conn.close()

    index_conn.commit()
    index_conn.close()

    print("Merge complete.")

def db_dummy_data_generate(db_path: str): # for testing merge_databases
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    jobs_data = [
    ("Backend Developer", "Gemini", "Remote", "Python, Django", "2026-05-16", "https://job6.com"),
    # ("Frontend Developer", "Meta", "USA", "React, JS", "2026-05-16", "https://job2.com"),
    # ("Data Engineer", "Amazon", "Remote", "SQL, Python", "2026-05-16", "https://job3.com"),
    ]
    for data in jobs_data:
        cur.execute("""
        INSERT OR IGNORE INTO jobs
        (title, company, location, skills, scraped_date, url)
        VALUES (?, ?, ?, ?, ?, ?)
        """, data)

    conn.commit()
    conn.close()


# migrate(file="datas/2025_09_24/jobs.csv")

# order: create_schema > migrate_all
# create_schema()
# migrate_all()

# db_dummy_data_generate("db_folder/b.db")
# merge_databases()