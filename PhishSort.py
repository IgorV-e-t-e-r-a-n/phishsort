import os
import shutil
import tkinter as tk
from tkinter import filedialog
from dnslib import DNSRecord, QTYPE

# SPF Checking Function
def check_spf(domain):
    try:
        q = DNSRecord.question(domain, QTYPE.TXT)
        a = q.send("8.8.8.8", 53, tcp=False)
        response = DNSRecord.parse(a)
        for rr in response.rr:
            if "v=spf1" in rr.rdata.toZone():
                return rr.rdata.toZone()
    except Exception as e:
        print(f"Error checking SPF for {domain}: {e}")
    return None

# Categorization Function
def categorize_email(email_headers):
    sender_domain = email_headers.get("From", "").split("@")[1] if "From" in email_headers else ""
    spf_record = check_spf(sender_domain)
    
    if spf_record is None:
        return "Monitoring"
    elif "-all" in spf_record:
        return "Reject"
    elif "~all" in spf_record:
        return "Quarantine"
    else:
        return "Monitoring"

# GUI to Select Folder
def select_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select Folder with Email Headers")

# Process Emails
def process_emails(folder):
    categories = {"Monitoring": [], "Quarantine": [], "Reject": []}
    
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):  # Assuming email headers are stored as .txt
            file_path = os.path.join(folder, filename)
            with open(file_path, "r") as f:
                headers = {line.split(": ")[0]: line.split(": ")[1].strip() for line in f if ": " in line}
                category = categorize_email(headers)
                categories[category].append(file_path)
    
    # Move Emails into Respective Folders
    for category, files in categories.items():
        category_folder = os.path.join(folder, category)
        os.makedirs(category_folder, exist_ok=True)
        for file in files:
            shutil.move(file, os.path.join(category_folder, os.path.basename(file)))
    
    print("Sorting Complete.")

# Run Program
email_folder = select_folder()
if email_folder:
    process_emails(email_folder)
