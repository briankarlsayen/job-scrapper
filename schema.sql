CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    location TEXT,
    skills TEXT,
    scraped_date TEXT,
    url TEXT UNIQUE
);