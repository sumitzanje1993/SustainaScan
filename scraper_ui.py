# scraper_ui.py

import streamlit as st
import os
import json
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    run_classification_and_enrichment
)

# Page config
st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")
st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Initialize session state variables
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False
if "insta_username" not in st.session_state:
    st.session_state.insta_username = ""
if "insta_password" not in st.session_state:
    st.session_state.insta_password = ""
if "insta_handle" not in st.session_state:
    st.session_state.insta_handle = ""
if "max_users" not in st.session_state:
    st.session_state.max_users = 30

# Input Form
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", value=st.session_state.insta_handle)
    insta_username = st.text_input("Your Instagram Username", value=st.session_state.insta_username)
    insta_password = st.text_input("Your Instagram Password", type="password", value=st.session_state.insta_password)
    if st.session_state.show_2fa:
        insta_2fa = st.text_input("2FA Code (required)")
    else:
        insta_2fa = ""
    max_users = st.slider("Max Followers to Scrape", 10, 100, value=st.session_state.max_users)
    run = st.form_submit_button("🚀 Start Scanning")

# Save state
if run:
    st.session_state.insta_handle = insta_handle
    st.session_state.insta_username = insta_username
    st.session_state.insta_password = insta_password
    st.session_state.max_users = max_users

    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields: handle, username, and password.")
    else:
        with st.spinner("🔐 Checking Instagram login..."):
            result = check_login_only(insta_username, insta_password)

        if result == "2FA_REQUIRED" and not insta_2fa:
            st.session_state.show_2fa = True
            st.warning("🔐 2FA is required. Please enter the 2FA code and resubmit.")
            st.stop()

        elif result == "LOGIN_FAILED":
            st.error("❌ Login failed. Please check your credentials.")

        else:
            with st.spinner("🔍 Scraping + Classifying + Enriching..."):
                try:
                    output_file = scrape_followers_of_account(
                        insta_handle, max_users, insta_username, insta_password, insta_2fa or None
                    )
                    if not os.path.exists(output_file):
                        st.error("❌ Scraping failed. File not found.")
                        st.stop()

                    run_classification_and_enrichment()

                    st.success("✅ Done! Dashboard is ready.")
                    st.info("➡️ Click on the 'dashboard' tab to view enriched leads.")

                except Exception as e:
                    st.error(f"💥 Failed: {e}")
