import instaloader
import os
import json
import sys

# Output file path
OUTPUT_FILE = "./data/instagram_raw_leads.json"

def check_login_only(user: str, pwd: str):
    L = instaloader.Instaloader()
    try:
        L.login(user, pwd)
        print("LOGIN_SUCCESS")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("2FA_REQUIRED")
    except Exception as e:
        print(f"LOGIN_FAILED: {e}")

def scrape_followers_of_account(target_username: str, max_users: int, login_user: str, login_pass: str, twofa_code: str = None):
    print("[+] Scraping followers of @{}...".format(target_username))
    print("[+] Attempting login...")

    # Setup Instaloader
    L = instaloader.Instaloader()

    try:
        L.login(login_user, login_pass)
        print("[INFO] Login successful.")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("[!] 2FA required by Instagram.")
        if twofa_code:
            try:
                L.two_factor_login(twofa_code)
                print("[INFO] 2FA login successful.")
            except Exception as e:
                print("[!] 2FA failed:", str(e))
                return
        else:
            print("[!] 2FA code not provided. Exiting.")
            return
    except Exception as e:
        print("[!] Login failed:", str(e))
        return

    # Fetch profile
    try:
        profile = instaloader.Profile.from_username(L.context, target_username)
        print("[INFO] Profile found:", target_username)
    except instaloader.exceptions.ProfileNotExistsException:
        print("[!] Profile not found. Double check the Instagram handle.")
        return
    except Exception as e:
        print("[!] Unexpected error while fetching profile:", str(e))
        return

    leads = []
    count = 0

    try:
        print("[INFO] Fetching followers list...")
        followers = profile.get_followers()
        print("[INFO] Follower generator acquired.")
    except Exception as e:
        print("[!] Failed to access followers:", str(e))
        return

    for follower in followers:
        if count >= max_users:
            break
        try:
            print("[INFO] Scraping follower:", follower.username)
            lead = {
                "username": follower.username,
                "full_name": follower.full_name,
                "bio": follower.biography,
                "followers": follower.followers,
                "external_url": follower.external_url,
                "profile_url": f"https://instagram.com/{follower.username}",
                "lead_source": f"https://instagram.com/{target_username}"
            }
            leads.append(lead)
            count += 1
        except Exception as e:
            print("[!] Skipped follower due to error:", str(e))
            continue

    os.makedirs("data", exist_ok=True)
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)
        print(f"[INFO] Saved {len(leads)} leads to {OUTPUT_FILE}")
        print("SCRAPE_DONE")
    except Exception as e:
        print("[!] Error saving output file:", str(e))

# CLI entry point
if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--check-login":
        if len(sys.argv) != 4:
            print("Usage: python instagram_scraper.py --check-login <user> <pass>")
        else:
            check_login_only(sys.argv[2], sys.argv[3])
    elif len(sys.argv) < 5:
        print("Usage: python instagram_scraper.py <target_handle> <max_users> <login_user> <login_pass> [2fa_code]")
    else:
        target_handle = sys.argv[1]
        max_users = int(sys.argv[2])
        login_user = sys.argv[3]
        login_pass = sys.argv[4]
        twofa_code = sys.argv[5] if len(sys.argv) > 5 else None
        scrape_followers_of_account(target_handle, max_users, login_user, login_pass, twofa_code)
