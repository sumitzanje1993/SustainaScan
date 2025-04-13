import streamlit as st
import os
import sys
import json
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    classify_leads,
    enrich_leads_with_contacts
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

# Step 1: Login verification
if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields.")
    else:
        st.info("🔐 Verifying credentials...")
        login_result = check_login_only(insta_username, insta_password)
        if login_result == "2FA_REQUIRED":
            st.session_state.show_2fa = True
            st.warning("2FA is required. Please enter the code.")
            st.stop()
        elif login_result == "LOGIN_FAILED":
            st.error("❌ Login failed.")
            st.stop()
        else:
            st.session_state.ready_to_scrape = True

# Step 2: Scraping + classification
if st.session_state.ready_to_scrape and st.session_state.show_2fa:
    with st.spinner("🔍 Scraping followers and enriching data..."):
        try:
            output_file = scrape_followers_of_account(
                target_username=insta_handle,
                max_users=max_users,
                login_user=insta_username,
                login_pass=insta_password,
                twofa_code=insta_2fa
            )
            if not os.path.exists(output_file):
                st.error("Scraping failed or returned no data.")
                st.stop()

            classify_leads()
            enrich_leads_with_contacts()
            st.success("✅ All done! Now click the **dashboard** tab to view your leads.")

        except Exception as e:
            st.error(f"Unexpected error: {e}")
