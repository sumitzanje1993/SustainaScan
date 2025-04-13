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

# --- Initialize session state ---
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False
if "scrape_triggered" not in st.session_state:
    st.session_state.scrape_triggered = False

# --- Input Form ---
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", value=st.session_state.get("last_handle", ""))
    insta_username = st.text_input("Your Instagram Username", value=st.session_state.get("last_user", ""))
    insta_password = st.text_input("Your Instagram Password", type="password")
    
    if st.session_state.show_2fa:
        insta_2fa = st.text_input("🔐 2FA Code (check your phone)", type="password")
    else:
        insta_2fa = ""

    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)
    submit = st.form_submit_button("🚀 Start Scanning")

# --- Form Handling ---
if submit:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields.")
    else:
        st.session_state.last_handle = insta_handle
        st.session_state.last_user = insta_username

        if not st.session_state.show_2fa:
            with st.spinner("🔐 Checking login..."):
                login_result = check_login_only(insta_username, insta_password)
            
            if login_result == "2FA_REQUIRED":
                st.session_state.show_2fa = True
                st.warning("🔐 2FA is required. Please enter the 2FA code and resubmit.")
                st.stop()
            elif login_result == "LOGIN_FAILED":
                st.error("❌ Login failed. Please check your credentials.")
                st.stop()

        # If already validated or 2FA passed
        try:
            with st.spinner("📥 Scraping followers..."):
                raw_file = scrape_followers_of_account(
                    insta_handle, max_users, insta_username, insta_password, insta_2fa if insta_2fa else None
                )

            with st.spinner("🤖 Running AI classification + enrichment..."):
                run_classification_and_enrichment()

            st.success("✅ All done! Leads collected and enriched.")
            st.info("📊 Go to the **dashboard** tab to view leads and download messages.")

            # Reset state for future runs
            st.session_state.show_2fa = False

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
