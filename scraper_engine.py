# scraper_engine.py

import json
import os
import instaloader
from lead_classifier import classify_leads
from contact_extractor import enrich_contacts

OUTPUT_FILE = "./data/instagram_raw_leads.json"

def scrape_followers(target_handle, max_users, username, password, twofa_code=None):
    L = instaloader.Instaloader()

    try:
        if twofa_code:
            L.login(username, password)
            L.two_factor_login(twofa_code)
        else:
            L.login(username, password)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        return {"error": "2FA_REQUIRED"}
    except Exception as e:
        return {"error": f"LOGIN_FAILED: {e}"}

    try:
        profile = instaloader.Profile.from_username(L.context, target_handle)
    except Exception as e:
        return {"error": f"PROFILE_FETCH_FAILED: {e}"}

    leads = []
    try:
        for i, follower in enumerate(profile.get_followers()):
            if i >= max_users:
                break
            leads.append({
                "username": follower.username,
                "full_name": follower.full_name,
                "bio": follower.biography,
                "followers": follower.followers,
                "external_url": follower.external_url,
                "profile_url": f"https://instagram.com/{follower.username}",
                "lead_source": f"https://instagram.com/{target_handle}"
            })
    except Exception as e:
        return {"error": f"SCRAPE_LOOP_FAILED: {e}"}

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    return {"success": True, "lead_count": len(leads)}

def run_classification_and_enrichment():
    try:
        classify_leads()
        enrich_contacts()
        return {"success": True}
    except Exception as e:
        return {"error": f"ENRICH_FAILED: {e}"}
