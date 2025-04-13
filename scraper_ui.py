# scraper_ui.py

import streamlit as st
import os
import sys
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    run_classification_and_enrichment,
)

# Set correct Python interpreter
VENV_PYTHON = sys.executable

# Page config
st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")

st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Session states
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False

# Form UI
with st.form("scraper_form"):
    insta_handle = st.text_input("Target Instagram Handle", placeholder="e.g. zerowastestore")
    insta_username = st.text_input("Your Instagram Username")
    insta_password = st.text_input("Your Instagram Password", type="password")

    if st.session_state.show_2fa:
        insta_2fa = st.text_input("Enter 2FA Code sent by Instagram")
    else:
        insta_2fa = ""

    max_users = st.slider("Max Followers to Scrape", 5, 100, 30)
    run_button = st.form_submit_button("🚀 Start Scanning")

# Logic
if run_button:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill all required fields.")
    else:
        with st.spinner("🔐 Checking Instagram login..."):
            login_check = check_login_only(insta_username, insta_password)

        if login_check == "2FA_REQUIRED":
            st.session_state.show_2fa = True
            st.warning("📲 2FA Required! Please enter your code and submit again.")
        elif login_check == "LOGIN_FAILED":
            st.error("❌ Login failed. Please verify your credentials.")
        elif login_check == "LOGIN_SUCCESS" or (st.session_state.show_2fa and insta_2fa.strip()):
            try:
                with st.spinner("🔍 Scraping & enriching leads..."):
                    scrape_followers_of_account(
                        target_username=insta_handle,
                        max_users=max_users,
                        login_user=insta_username,
                        login_pass=insta_password,
                        twofa_code=insta_2fa.strip() if insta_2fa else None
                    )
                    run_classification_and_enrichment()

                st.success("✅ Done! Your leads are enriched.")
                st.info("📊 Now switch to the **Dashboard** tab on the left to view results.")

            except Exception as e:
                st.error(f"❌ Scraping failed: {e}")
        else:
            st.error("❌ Unknown error occurred during login.")
