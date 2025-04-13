# llm_processing/lead_classifier.py

import openai
import json
import os
from dotenv import load_dotenv

# Load OpenAI Key
load_dotenv(dotenv_path="./config/secrets.env")
openai.api_key = os.getenv("OPENAI_API_KEY")

INPUT_FILE = "./data/instagram_raw_leads.json"
OUTPUT_FILE = "./data/instagram_leads_scored.json"

def classify_leads():
    with open(INPUT_FILE, "r") as f:
        leads = json.load(f)

    enriched = []

    for lead in leads:
        prompt = f"""
You are a helpful marketing AI. Analyze this Instagram user and respond in JSON format.

Username: {lead['username']}
Bio: {lead['bio']}
Followers: {lead['followers']}
Full Name: {lead['full_name']}
External URL: {lead['external_url']}

Classify this person with:
- lead_type: Buyer / Influencer / Brand / Not Relevant
- lead_score: Number from 1 (low) to 10 (very relevant)
- location: If any city or place is mentioned in their bio
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            ai_response = json.loads(response.choices[0].message.content.strip())
            lead.update(ai_response)
            enriched.append(lead)

            print(f"[+] @{lead['username']} | Type: {ai_response['lead_type']} | Score: {ai_response['lead_score']}")

        except Exception as e:
            print(f"[!] Error processing {lead['username']}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"\n[✓] Saved enriched leads to {OUTPUT_FILE}")

if __name__ == "__main__":
    classify_leads()
