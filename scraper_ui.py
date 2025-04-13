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

# --- Session states ---
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False
if "insta_2fa" not in st.session_state:
    st.session_state.insta_2fa = ""
if "last_run_success" not in st.session_state:
    st.session_state.last_run_success = False

# --- Inputs ---
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", value=st.session_state.get("last_handle", ""))
    insta_username = st.text_input("Your Instagram Username", value=st.session_state.get("last_user", ""))
    insta_password = st.text_input("Your Instagram Password", type="password")
    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)

    if st.session_state.show_2fa:
        st.session_state.insta_2fa = st.text_input("🔐 2FA Code", value=st.session_state.insta_2fa, type="password")

    run = st.form_submit_button("🚀 Start Scanning")

# --- Logic ---
if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("Please fill in all required fields.")
    else:
        st.session_state.last_handle = insta_handle
        st.session_state.last_user = insta_username

        if not st.session_state.show_2fa:
            with st.spinner("🔐 Checking login..."):
                result = check_login_only(insta_username, insta_password)

            if result == "2FA_REQUIRED":
                st.session_state.show_2fa = True
                st.warning("🔐 2FA is required. Please enter the code above and click again.")
                st.stop()
            elif result == "LOGIN_FAILED":
                st.error("❌ Login failed. Please check your credentials.")
                st.stop()
            else:
                st.session_state.show_2fa = False

        # If 2FA already shown or passed
        try:
            with st.spinner("📥 Scraping followers..."):
                scrape_followers_of_account(
                    insta_handle,
                    max_users,
                    insta_username,
                    insta_password,
                    st.session_state.insta_2fa
                )

            with st.spinner("🤖 Running classification and enrichment..."):
                run_classification_and_enrichment()

            st.success("✅ Done! Leads enriched.")
            st.info("➡️ Visit the 'dashboard' tab to explore and download leads.")
            st.session_state.show_2fa = False
            st.session_state.insta_2fa = ""

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
