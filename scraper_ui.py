# scraper_ui.py

import streamlit as st
import os
import json
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    run_classification_and_enrichment
)

# Streamlit app setup
st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")
st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Session states for dynamic UI
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False

# Input form
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", placeholder="e.g. zerowastestore")
    insta_username = st.text_input("Your Instagram Username")
    insta_password = st.text_input("Your Instagram Password", type="password")
    if st.session_state.show_2fa:
        insta_2fa = st.text_input("2FA Code (required)")
    else:
        insta_2fa = ""
    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)
    run = st.form_submit_button("🚀 Start Scanning")

# Run logic
if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields: handle, username, and password.")
    else:
        with st.spinner("🔐 Verifying Instagram login..."):
            login_result = check_login_only(insta_username, insta_password)

        if login_result == "2FA_REQUIRED":
            st.session_state.show_2fa = True
            st.warning("🔐 2FA is required. Please re-enter your credentials and 2FA code.")
            st.stop()

        elif login_result == "LOGIN_FAILED":
            st.error("❌ Login failed. Please check your credentials.")
            st.stop()

        elif login_result == "LOGIN_SUCCESS" or (st.session_state.show_2fa and insta_2fa):
            with st.spinner("🔍 Scraping followers and enriching data..."):
                try:
                    # Step 1: Scrape followers
                    scrape_followers_of_account(
                        target_username=insta_handle,
                        max_users=max_users,
                        login_user=insta_username,
                        login_pass=insta_password,
                        twofa_code=insta_2fa.strip() if insta_2fa else None
                    )

                    # Step 2: Classify + Enrich
                    run_classification_and_enrichment()

                    # Step 3: Show success
                    if not os.path.exists("./data/instagram_leads_enriched.json"):
                        st.error("❌ Something went wrong. No output file generated.")
                    else:
                        st.success("✅ All done! Your leads have been enriched.")
                        st.info("➡️ Now click the **'dashboard'** tab on the left to view results.")

                except Exception as e:
                    st.error("💥 Unexpected Error:")
                    st.code(str(e), language="text")
