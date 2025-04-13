# scraper_ui.py

import streamlit as st
import os
import sys

# Internal engine imports
import scraper_engine

st.set_page_config(page_title="SustainaScan | Scraper", layout="centered")

st.title("🌿 SustainaScan: Smart Lead Finder for Greeco Sustainable Living")
st.markdown("Type the Instagram handle of an eco-friendly brand or influencer to scan their followers.")

# Initialize session state for UI control
if "show_2fa" not in st.session_state:
    st.session_state.show_2fa = False

# Scraper Form
with st.form("scraper_form"):
    insta_handle = st.text_input("Instagram Handle", placeholder="e.g. zerowastestore")
    insta_username = st.text_input("Your Instagram Username")
    insta_password = st.text_input("Your Instagram Password", type="password")
    insta_2fa = st.text_input("2FA Code (if applicable)") if st.session_state.show_2fa else ""
    max_users = st.slider("Max Followers to Scrape", 10, 100, 30)
    run = st.form_submit_button("🚀 Start Scanning")

# Handle form submission
if run:
    if not insta_handle or not insta_username or not insta_password:
        st.warning("⚠️ Please fill in all required fields.")
    else:
        with st.spinner("🔐 Verifying Instagram login..."):
            result = scraper_engine.check_login_only(insta_username, insta_password)

        if result == "2FA_REQUIRED":
            st.session_state.show_2fa = True
            st.warning("🔐 2FA is required. Please enter the 2FA code and resubmit.")
            st.stop()
        elif result == "LOGIN_FAILED":
            st.error("❌ Login failed. Please check your credentials.")
            st.stop()
        else:
            # Step 1: Scrape
            with st.spinner("📸 Scraping followers..."):
                try:
                    scraper_engine.scrape_followers_of_account(
                        target_username=insta_handle,
                        max_users=max_users,
                        login_user=insta_username,
                        login_pass=insta_password,
                        twofa_code=insta_2fa if insta_2fa.strip() else None
                    )
                    st.success("✅ Followers scraped.")
                except Exception as e:
                    st.error(f"❌ Scraping failed: {e}")
                    st.stop()

            # Step 2: Classify + Enrich
            with st.spinner("🧠 Classifying leads and extracting contact info..."):
                try:
                    scraper_engine.run_classification_and_enrichment()
                    st.success("✅ Leads classified and enriched.")
                    st.info("➡️ Click the **'dashboard'** tab to view your leads.")
                except Exception as e:
                    st.error(f"❌ Processing failed: {e}")
