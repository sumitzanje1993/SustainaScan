# llm_processing/contact_extractor.py

import json
import re
import requests
from bs4 import BeautifulSoup
import os

INPUT_FILE = "./data/instagram_leads_scored.json"
OUTPUT_FILE = "./data/instagram_leads_enriched.json"

EMAIL_REGEX = r'[\w\.-]+@[\w\.-]+\.\w+'
PHONE_REGEX = r'\+?\d[\d -]{8,}\d'
WHATSAPP_REGEX = r'(wa\.me/\d+|api\.whatsapp\.com/send\?phone=\d+)'

def extract_contacts_from_text(text):
    email = re.findall(EMAIL_REGEX, text)
    phone = re.findall(PHONE_REGEX, text)
    whatsapp = re.findall(WHATSAPP_REGEX, text)
    return {
        "email": email[0] if email else None,
        "phone": phone[0] if phone else None,
        "whatsapp": f"https://{whatsapp[0]}" if whatsapp else None
    }

def extract_from_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return extract_contacts_from_text(resp.text)
    except Exception:
        pass
    return {}

def enrich_leads_with_contacts():
    if not os.path.exists(INPUT_FILE):
        print("[!] Scored leads file not found.")
        return

    with open(INPUT_FILE, "r") as f:
        leads = json.load(f)

    enriched = []
    for lead in leads:
        bio = lead.get("bio", "")
        ext_url = lead.get("external_url")

        contacts = extract_contacts_from_text(bio)

        if ext_url:
            website_contacts = extract_from_website(ext_url)
            for k in ['email', 'phone', 'whatsapp']:
                if not contacts.get(k) and website_contacts.get(k):
                    contacts[k] = website_contacts[k]

        lead.update(contacts)
        enriched.append(lead)

        print(f"[+] @{lead['username']} | Email: {contacts['email']} | Phone: {contacts['phone']} | WhatsApp: {contacts['whatsapp']}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"\n[✓] Saved enriched leads to {OUTPUT_FILE}")

if __name__ == "__main__":
    enrich_leads_with_contacts()
