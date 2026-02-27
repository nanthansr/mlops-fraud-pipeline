"""
AWS SAA-C03 Daily Study Log — Auto-entry creator
─────────────────────────────────────────────────
Run this each morning before your 6am study block.
It creates today's entry in your study log, pre-filled
with yesterday's "fuzzy on" section so you start with a recap.

Setup:
1. Put this script in your OneDrive synced folder
2. Set LOG_PATH below to your actual OneDrive path
3. Mac:     python3 study_log.py
   Windows: python study_log.py

Optional — run automatically at login:
   Mac:     Add to Login Items or use a launchd plist
   Windows: Add to Task Scheduler → trigger at logon
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# ── CONFIG — change this to your OneDrive path ──
# Mac example:    /Users/nanthan/OneDrive/Nanthan-Vault/aws-study-log.md
# Windows example: C:/Users/Nanthan/OneDrive/Nanthan-Vault/aws-study-log.md
LOG_PATH = Path.home() / "OneDrive" / "Nanthan-Vault" / "aws-study-log.md"

# Stephen Marek course sections — fill in as you go
# Format: "Section X — Topic"
COURSE_SECTIONS = [
    "Section 1 — AWS Fundamentals",
    "Section 2 — IAM & AWS CLI",
    "Section 3 — EC2 Fundamentals",
    "Section 4 — EC2 Instance Storage",
    "Section 5 — High Availability & Scalability (ELB & ASG)",
    "Section 6 — RDS, Aurora & ElastiCache",
    "Section 7 — Route 53",
    "Section 8 — Classic Solutions Architecture",
    "Section 9 — S3 Introduction",
    "Section 10 — S3 Advanced",
    "Section 11 — CloudFront & AWS Global Accelerator",
    "Section 12 — AWS Storage Extras",
    "Section 13 — Decoupling Applications (SQS, SNS, Kinesis)",
    "Section 14 — Containers on AWS (ECS, Fargate, ECR, EKS)",
    "Section 15 — Serverless Overview (Lambda)",
    "Section 16 — Serverless Architecture",
    "Section 17 — Databases in AWS",
    "Section 18 — Data & Analytics",
    "Section 19 — Machine Learning",
    "Section 20 — AWS Monitoring & Audit (CloudWatch, CloudTrail)",
    "Section 21 — IAM Advanced",
    "Section 22 — AWS Security & Encryption (KMS, SSM, Shield, WAF)",
    "Section 23 — Networking (VPC)",
    "Section 24 — Disaster Recovery & Migrations",
    "Section 25 — More Solutions Architecture",
    "Section 26 — Other Services",
    "Section 27 — WhizLabs Practice Exams",
]


def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %A")


def get_yesterday_str() -> str:
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def extract_yesterday_fuzzy(log_content: str) -> str:
    """Pull the 'Fuzzy on' line from yesterday's entry for today's recap."""
    yesterday = get_yesterday_str()
    pattern = rf"## {yesterday}.*?Fuzzy on:\s*(.+?)(?:\n|$)"
    match = re.search(pattern, log_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Nothing flagged from yesterday"


def entry_exists_today(log_content: str) -> bool:
    today_date = datetime.now().strftime("%Y-%m-%d")
    return f"## {today_date}" in log_content


def create_today_entry(fuzzy_yesterday: str) -> str:
    today = get_today_str()
    return f"""
## {today}

**Recap from yesterday**: {fuzzy_yesterday}

**Section covered**:
<!-- e.g. Section 14 — Containers on AWS (ECS, Fargate, ECR) -->

**Topics covered**:
<!-- What did you actually learn today? Be specific. -->
-
-
-

**Fuzzy on**:
<!-- What still doesn't click? This becomes tomorrow's recap. -->

**Tomorrow**:
<!-- Exact section + video number to pick up from -->

**Anki cards added**: <!-- How many new cards did you add? -->

---
"""


def main():
    # Ensure the log file and its parent directory exist
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not LOG_PATH.exists():
        header = """# AWS SAA-C03 Study Log — Nanthan Srikumar

> One entry per day. Three lines minimum: what you covered, what's fuzzy, where you're starting tomorrow.
> Fuzzy items become the next day's recap automatically.

---

"""
        LOG_PATH.write_text(header)
        print(f"✅ Created new log at {LOG_PATH}")

    content = LOG_PATH.read_text()

    if entry_exists_today(content):
        print(f"✅ Today's entry already exists in {LOG_PATH}")
        print("   Open the file and fill it in after your study session.")
        return

    # Get yesterday's fuzzy item for the recap
    fuzzy_yesterday = extract_yesterday_fuzzy(content)

    # Prepend today's entry after the header (so newest is at top)
    header_end = content.find("---\n") + 4
    new_content = content[:header_end] + create_today_entry(fuzzy_yesterday) + content[header_end:]
    LOG_PATH.write_text(new_content)

    print(f"""
✅ Today's study entry created in:
   {LOG_PATH}

📋 Yesterday you were fuzzy on:
   {fuzzy_yesterday}

⏰ Open the file, do your session, fill in what you covered.
   Takes 90 seconds after you close Udemy.
""")

    # Print upcoming sections reminder
    print("📚 Stephen Marek course sections (for reference):")
    for s in COURSE_SECTIONS[:5]:
        print(f"   {s}")
    print("   ...")


if __name__ == "__main__":
    main()
