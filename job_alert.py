import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import re

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

HEADERS = {"User-Agent": "Mozilla/5.0"}

EXCLUDE_KEYWORDS = [
    "senior", "lead", "architect", "manager", "principal"
]

TECH_KEYWORDS = [
    "java", "react", "node", "mern", "javascript",
    "mongodb", "mysql", "express", "rest", "typescript"
]

PRIORITY_KEYWORDS = [
    "fresher", "graduate", "trainee", "get", "campus", "mentorship"
]

# --------------------------------------------------
# EMAIL
# --------------------------------------------------
def send_email(body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "Daily Fresher Software Job Alerts (India)"

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# --------------------------------------------------
# FILTERING
# --------------------------------------------------
def is_valid_job(title, description):
    text = (title + description).lower()

    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False

    if not any(word in text for word in TECH_KEYWORDS):
        return False

    return True

# --------------------------------------------------
# LINKEDIN SCRAPER (PUBLIC SEARCH PAGES)
# --------------------------------------------------
def fetch_linkedin_jobs():
    jobs = []
    url = (
        "https://www.linkedin.com/jobs/search/"
        "?keywords=Software%20Engineer%20Fresher"
        "&location=India&f_E=2"
    )

    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    for job in soup.select("div.base-card"):
        title = job.select_one("h3").get_text(strip=True)
        company = job.select_one("h4").get_text(strip=True)
        location = job.select_one(".job-search-card__location").get_text(strip=True)
        link = job.a["href"]

        if is_valid_job(title, title):
            jobs.append({
                "company": company,
                "title": title,
                "location": location,
                "skills": "Java / MERN / Full Stack",
                "link": link,
                "date": "Recent"
            })

    return jobs

# --------------------------------------------------
# WELLFOUND SCRAPER
# --------------------------------------------------
def fetch_wellfound_jobs():
    jobs = []
    url = "https://wellfound.com/jobs"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    for job in soup.select("div.styles_jobListing__"):
        title = job.get_text(" ", strip=True)
        if is_valid_job(title, title):
            jobs.append({
                "company": "Startup (Wellfound)",
                "title": title,
                "location": "India / Remote",
                "skills": "Java / MERN / Full Stack",
                "link": url,
                "date": "Recent"
            })

    return jobs

# --------------------------------------------------
# NAUKRI RSS
# --------------------------------------------------
def fetch_naukri_jobs():
    jobs = []
    feed_url = (
        "https://www.naukri.com/software-engineer-fresher-jobs-in-india-rss"
    )
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        summary = entry.summary

        if is_valid_job(title, summary):
            jobs.append({
                "company": "Various (Naukri)",
                "title": title,
                "location": "India",
                "skills": "Java / MERN / Full Stack",
                "link": link,
                "date": entry.get("published", "Recent")
            })

    return jobs

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    all_jobs = []
    all_jobs.extend(fetch_linkedin_jobs())
    all_jobs.extend(fetch_wellfound_jobs())
    all_jobs.extend(fetch_naukri_jobs())

    # Deduplicate by title + company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job["company"], job["title"])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    if not unique_jobs:
        send_email("No new fresher-level jobs found today.")
        return

    body = ""
    for job in unique_jobs[:20]:
        body += f"""
Company: {job['company']}
Role: {job['title']}
Location: {job['location']}
Skills: {job['skills']}
Date Posted: {job['date']}
Apply Here: {job['link']}
------------------------------------------
"""

    send_email(body)

if __name__ == "__main__":
    main()
