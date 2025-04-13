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

# --- Session state ---
if "last_handle" not in st.session_state:
    st.session_state.last_handle = ""
if "last_user" not in st.session_state:
    st.session_state.last_user = ""
if "show_warning" not in st.session_state:
    st.session_state.show_warning = False

# --- Input form ---
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", value=st.session_state.last_handle)
    insta_username = st.text_input("Your Instagram Username", value=st.session_state.last_user)
    insta_password = st.text_input("Your Instagram Password", type="password")
    insta_2fa = st.text_input("🔐 Instagram 2FA Code (if asked)", type="password")
    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)
    run = st.form_submit_button("🚀 Start Scanning")

# --- Logic ---
if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields.")
    else:
        st.session_state.last_handle = insta_handle
        st.session_state.last_user = insta_username

        try:
            with st.spinner("🔐 Checking login..."):
                result = check_login_only(insta_username, insta_password)

            if result == "2FA_REQUIRED" and not insta_2fa:
                st.session_state.show_warning = True
                st.warning("🔐 2FA required. Please enter the code above and click again.")
                st.stop()

            if result == "LOGIN_FAILED":
                st.error("❌ Login failed. Please check credentials.")
                st.stop()

            with st.spinner("📥 Scraping followers..."):
                scrape_followers_of_account(
                    insta_handle,
                    max_users,
                    insta_username,
                    insta_password,
                    insta_2fa
                )

            with st.spinner("🤖 Running classification and enrichment..."):
                run_classification_and_enrichment()

            st.success("✅ Scraping + enrichment complete.")
            st.info("➡️ Visit the **Dashboard** tab to explore and download your leads.")
            st.session_state.show_warning = False

        except Exception as e:
            st.error(f"❌ {str(e)}")
