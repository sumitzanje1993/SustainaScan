# scraper_ui.py

import streamlit as st
import os
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    run_classification_and_enrichment
)

st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")
st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Session state init
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False
if "ready_to_scrape" not in st.session_state:
    st.session_state.ready_to_scrape = False

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

if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields.")
    else:
        st.info("🔐 Verifying credentials...")
        result = check_login_only(insta_username, insta_password)
        if result == "2FA_REQUIRED":
            st.session_state.show_2fa = True
            st.warning("🔐 2FA is required. Please enter the code.")
            st.stop()
        elif result == "LOGIN_FAILED":
            st.error("❌ Login failed.")
            st.stop()
        else:
            st.session_state.ready_to_scrape = True

# Scrape + Enrich
if st.session_state.ready_to_scrape:
    with st.spinner("🔍 Scraping and enriching leads..."):
        try:
            file = scrape_followers_of_account(
                insta_handle, max_users, insta_username, insta_password, insta_2fa if insta_2fa else None
            )
            if os.path.exists(file):
                run_classification_and_enrichment()
                st.success("✅ All done! Now click the **dashboard** tab to view your leads.")
            else:
                st.error("Scraping failed.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
