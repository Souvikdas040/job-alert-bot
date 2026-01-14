import requests, feedparser, os, smtplib
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

HEADERS = {"User-Agent": "Mozilla/5.0"}

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# -----------------------------------
# FILTER CONFIG
# -----------------------------------
EXCLUDE = ["senior", "lead", "manager", "architect", "principal"]
TECH = ["java", "react", "node", "mern", "javascript", "mongodb", "mysql"]

# -----------------------------------
# EMAIL
# -----------------------------------
def send_email(html):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "🚀 Daily Fresher Software Job Alerts"

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(EMAIL_SENDER, EMAIL_PASSWORD)
        s.send_message(msg)

# -----------------------------------
# TELEGRAM
# -----------------------------------
def send_telegram(jobs):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return

    msg = "<b>🚀 Fresher Job Alerts</b>\n\n"
    for j in jobs[:5]:
        msg += f"<b>{j['title']}</b>\n{j['company']}\n<a href='{j['link']}'>Apply</a>\n\n"

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": msg, "parse_mode": "HTML"}
    )

# -----------------------------------
# FILTER LOGIC
# -----------------------------------
def valid_job(title, text):
    data = (title + text).lower()
    if any(x in data for x in EXCLUDE):
        return False
    return any(x in data for x in TECH)

def classify(title):
    t = title.lower()
    return "intern" if any(x in t for x in ["intern", "trainee", "graduate", "get"]) else "full"

# -----------------------------------
# SCRAPERS
# -----------------------------------
def linkedin_jobs():
    jobs = []
    url = "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer%20Fresher&location=India&f_E=2"
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")

    for j in soup.select("div.base-card"):
        title = j.select_one("h3").text.strip()
        company = j.select_one("h4").text.strip()
        link = j.a["href"]
        if valid_job(title, title):
            jobs.append({
                "company": company,
                "title": title,
                "location": "India",
                "skills": "Java, MERN",
                "link": link
            })
    return jobs

def wellfound_jobs():
    jobs = []
    soup = BeautifulSoup(requests.get("https://wellfound.com/jobs", headers=HEADERS).text, "html.parser")
    for j in soup.select("a[href*='/jobs/']"):
        title = j.text.strip()
        if valid_job(title, title):
            jobs.append({
                "company": "Startup (Wellfound)",
                "title": title,
                "location": "Remote / India",
                "skills": "Java, MERN",
                "link": "https://wellfound.com" + j["href"]
            })
    return jobs

def naukri_jobs():
    jobs = []
    feed = feedparser.parse("https://www.naukri.com/software-engineer-fresher-jobs-in-india-rss")
    for e in feed.entries:
        if valid_job(e.title, e.summary):
            jobs.append({
                "company": "Various (Naukri)",
                "title": e.title,
                "location": "India",
                "skills": "Java, MERN",
                "link": e.link
            })
    return jobs

# -----------------------------------
# HTML TEMPLATE
# -----------------------------------
def html_email(full, intern):
    def card(j):
        return f"""
        <div style="border:1px solid #ddd;padding:15px;border-radius:8px;margin-bottom:12px">
          <h3>{j['title']}</h3>
          <p><b>{j['company']}</b> | {j['location']}</p>
          <p>{j['skills']}</p>
          <a href="{j['link']}" style="background:#2563eb;color:#fff;padding:8px 12px;border-radius:5px;text-decoration:none">Apply</a>
        </div>
        """

    html = "<h2>🚀 Daily Fresher Job Alerts</h2>"
    if full:
        html += "<h3>💼 Full-Time Roles</h3>" + "".join(card(j) for j in full)
    if intern:
        html += "<h3>🎓 Internships / Trainee</h3>" + "".join(card(j) for j in intern)
    return html

# -----------------------------------
# MAIN
# -----------------------------------
def main():
    jobs = linkedin_jobs() + wellfound_jobs() + naukri_jobs()

    seen, unique = set(), []
    for j in jobs:
        key = (j["company"], j["title"])
        if key not in seen:
            seen.add(key)
            unique.append(j)

    full, intern = [], []
    for j in unique:
        (intern if classify(j["title"]) == "intern" else full).append(j)

    send_email(html_email(full, intern))
    send_telegram(unique)

if __name__ == "__main__":
    main()
