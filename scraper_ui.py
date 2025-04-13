import streamlit as st
import os
from scraper_engine import (
    check_login_only,
    scrape_followers_of_account,
    run_classification_and_enrichment
)

# UI config
st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")
st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Session init
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False
if "ready_to_scrape" not in st.session_state:
    st.session_state.ready_to_scrape = False

# Form UI
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", placeholder="e.g. zerowastestore")
    insta_username = st.text_input("Your Instagram Username")
    insta_password = st.text_input("Your Instagram Password", type="password")

    # 2FA input only if needed
    if st.session_state.show_2fa:
        insta_2fa = st.text_input("Enter 2FA Code sent by Instagram")
    else:
        insta_2fa = ""

    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)
    submit = st.form_submit_button("🚀 Start Scan")

# Handle submit
if submit:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("Please fill in all required fields.")
    else:
        with st.spinner("🔐 Checking login..."):
            login_result = check_login_only(insta_username, insta_password)

        if login_result == "2FA_REQUIRED":
            st.session_state.show_2fa = True
            st.warning("2FA is required. Please enter the code sent by Instagram.")
            st.stop()

        elif login_result == "LOGIN_FAILED":
            st.error("Login failed. Please check your credentials.")
            st.stop()

        elif login_result == "LOGIN_SUCCESS" or (st.session_state.show_2fa and insta_2fa):
            with st.spinner("🔍 Scraping and processing leads..."):
                try:
                    scrape_followers_of_account(
                        target_username=insta_handle,
                        max_users=max_users,
                        login_user=insta_username,
                        login_pass=insta_password,
                        twofa_code=insta_2fa if st.session_state.show_2fa else None
                    )
                    run_classification_and_enrichment()
                    st.success("✅ All done! Leads are enriched and ready.")
                    st.info("➡️ Now click the **Dashboard** tab on the left to view results.")
                except Exception as e:
                    st.error(f"Scraping failed: {e}")
