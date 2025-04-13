# scraper_ui.py

import streamlit as st
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    run_classification_and_enrichment
)
import time

st.set_page_config(page_title="SustainaScan Scraper", layout="centered")

st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.write("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

with st.form(key="scrape_form"):
    target = st.text_input("Instagram Handle", help="The influencer or brand to scrape followers from")
    username = st.text_input("Your Instagram Username")
    password = st.text_input("Your Instagram Password", type="password")
    twofa_code = st.text_input("🔐 Instagram 2FA Code (if asked)", type="password", help="Only if 2FA is triggered")
    max_followers = st.slider("Max Followers to Scrape", min_value=10, max_value=100, value=30)
    submit = st.form_submit_button("🚀 Start Scanning")

if submit:
    if not all([target, username, password]):
        st.error("Please fill in all required fields.")
        st.stop()

    with st.spinner("🔐 Logging in..."):
        login_result = check_login_only(username, password)
        if login_result == "2FA_REQUIRED":
            if not twofa_code:
                st.warning("⚠️ 2FA is required. Please enter the code and resubmit.")
                st.stop()

    try:
        with st.spinner("📸 Scraping followers..."):
            scrape_followers_of_account(
                target_username=target,
                max_users=max_followers,
                login_user=username,
                login_pass=password,
                twofa_code=twofa_code or None
            )
        with st.spinner("🤖 Classifying and enriching leads..."):
            run_classification_and_enrichment()
        st.success("✅ All done! Head to the dashboard to view your leads.")
    except Exception as e:
        st.error(f"❌ {e}")
