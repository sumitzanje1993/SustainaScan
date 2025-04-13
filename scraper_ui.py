# scraper_ui.py

import streamlit as st
import subprocess
import os
import sys
import time

# Use the Python interpreter from the current venv
VENV_PYTHON = sys.executable

st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")

st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Input form
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", placeholder="e.g. zerowastestore")
    insta_username = st.text_input("Your Instagram Username")
    insta_password = st.text_input("Your Instagram Password", type="password")
    insta_2fa = st.text_input("2FA Code (if prompted by Instagram)")
    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)
    run = st.form_submit_button("🚀 Start Scanning")

# Button logic
if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields: handle, username, and password.")
    else:
        # Clear old files
        for f in [
            "./data/instagram_raw_leads.json",
            "./data/instagram_leads_scored.json",
            "./data/instagram_leads_enriched.json"
        ]:
            if os.path.exists(f):
                os.remove(f)

        st.info(f"⏳ Starting scrape for @{insta_handle}... This may take 10–60 seconds depending on followers.")
        progress = st.progress(0, text="Initializing...")

        try:
            # Build command
            args = [
                VENV_PYTHON,
                "instagram_scraper.py",
                insta_handle,
                str(max_users),
                insta_username,
                insta_password
            ]
            if insta_2fa.strip():
                args.append(insta_2fa.strip())

            # Simulated progress (visual feedback)
            for pct in range(0, 60, 10):
                time.sleep(0.5)
                progress.progress(pct, text=f"Scanning... {pct}% complete")

            # Run scraper
            progress.progress(70, text="Scraping followers...")
            result = subprocess.run(args, capture_output=True, text=True)

            # Finish up
            progress.progress(90, text="Enriching leads...")

            if "SCRAPE_DONE" not in result.stdout or not os.path.exists("./data/instagram_raw_leads.json"):
                progress.empty()
                st.error("❌ Scraping failed. Please check credentials, 2FA code, or public access.")
            else:
                subprocess.run([VENV_PYTHON, "lead_classifier.py"])
                subprocess.run([VENV_PYTHON, "contact_extractor.py"])

                progress.progress(100, text="✅ Completed.")
                progress.empty()
                st.success("✅ All done! Your leads have been enriched.")
                st.info("➡️ Now click the **'dashboard'** tab on the left to view results.")

        except Exception as e:
            progress.empty()
            st.markdown("### 💥 Unhandled Exception")
            st.code(str(e), language="text")
