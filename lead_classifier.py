# scraper_engine.py

import json
import os
import instaloader
from lead_classifier import classify_leads
from contact_extractor import enrich_contacts

OUTPUT_FILE = "./data/instagram_raw_leads.json"

def check_login_only(user: str, pwd: str):
    L = instaloader.Instaloader()
    try:
        L.login(user, pwd)
        return "LOGIN_SUCCESS"
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        return "2FA_REQUIRED"
    except Exception:
        return "LOGIN_FAILED"

def scrape_followers_of_account(target_username, max_users, login_user, login_pass, twofa_code=None):
    L = instaloader.Instaloader()
    try:
        if twofa_code:
            L.login(login_user, login_pass)
            L.two_factor_login(twofa_code)
        else:
            L.login(login_user, login_pass)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        raise Exception("2FA_REQUIRED")
    except Exception as e:
        raise Exception(f"LOGIN_FAILED: {e}")

    try:
        profile = instaloader.Profile.from_username(L.context, target_username)
    except Exception as e:
        raise Exception(f"PROFILE_FETCH_FAILED: {e}")

    leads = []
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
            "lead_source": f"https://instagram.com/{target_username}"
        })

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    return OUTPUT_FILE

def run_classification_and_enrichment():
    classify_leads()
    enrich_contacts()
