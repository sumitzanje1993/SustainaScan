# lead_classifier.py

import json
import os
import openai

# ✅ Load OpenAI key from secrets if running via Streamlit, else fallback to .env
if os.getenv("STREAMLIT_RUN") == "1":
    try:
        import streamlit as st
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


# File paths
INPUT_FILE = "./data/instagram_raw_leads.json"
OUTPUT_FILE = "./data/instagram_leads_scored.json"

def classify_leads():
    if not os.path.exists(INPUT_FILE):
        print("[!] Raw leads file not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        leads = json.load(f)

    scored_leads = []

    for lead in leads:
        username = lead.get("username", "unknown_user")
        bio = lead.get("bio", "")
        followers = lead.get("followers", 0)

        prompt = f"""
You are a smart assistant for a sustainable brand.
Based on the Instagram bio and follower count, classify this user and assign a lead score (1-10).

Bio: {bio}
Followers: {followers}

Return ONLY a valid JSON like this:
{{
  "lead_type": "Influencer / Eco-Buyer / Business / Other",
  "lead_score": 1-10
}}
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            result_text = response.choices[0].message.content.strip()
            parsed = json.loads(result_text)

            lead["lead_type"] = parsed.get("lead_type", "Other")
            lead["lead_score"] = int(parsed.get("lead_score", 5))

        except Exception as e:
            print(f"[!] Error scoring @{username}: {e}")
            lead["lead_type"] = "Unknown"
            lead["lead_score"] = 1

        scored_leads.append(lead)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scored_leads, f, indent=2)

    print(f"[✓] Saved {len(scored_leads)} scored leads to {OUTPUT_FILE}")


if __name__ == "__main__":
    classify_leads()
