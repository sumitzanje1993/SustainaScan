# pages/dashboard.py

import streamlit as st
import pandas as pd
import json
import os
import openai
from PIL import Image
from dotenv import load_dotenv

# Load OpenAI key
load_dotenv(dotenv_path="./config/secrets.env")
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="SustainaScan | Dashboard", layout="wide")

# Background color (dark theme with light text readability)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Logo
logo_path = "./data/Greeco_logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=180)

st.title("📊 SustainaScan | Lead Dashboard")
st.markdown("Filter, view, and connect with your eco-minded audience below.")

# Data paths
DATA_FILE = "./data/instagram_leads_enriched.json"
CONTACTED_FILE = "./data/contacted_status.json"

# Ensure file exists
if not os.path.exists(DATA_FILE):
    st.warning("⚠️ No leads found. Please run a scrape first.")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    leads = json.load(f)

# Load or initialize contacted status
if os.path.exists(CONTACTED_FILE):
    with open(CONTACTED_FILE, "r", encoding="utf-8") as f:
        contacted_status = json.load(f)
else:
    contacted_status = {}

# Convert to DataFrame
df = pd.DataFrame(leads)

# Sidebar filters
st.sidebar.header("🎯 Filter Leads")
lead_types = st.sidebar.multiselect("Lead Type", options=df["lead_type"].unique(), default=df["lead_type"].unique())
min_score, max_score = st.sidebar.slider("Lead Score", 1, 10, (5, 10))
location = st.sidebar.text_input("Location contains", "")

filtered_df = df[
    (df["lead_type"].isin(lead_types)) &
    (df["lead_score"].between(min_score, max_score)) &
    (df["location"].str.contains(location, case=False, na=False))
]

st.success(f"✅ Found {len(filtered_df)} leads")

# GPT message generator
def generate_message(username, lead_type, score):
    prompt = f"""
You are a friendly marketer for an eco-business called Greeco Sustainable Living.
Write a short, personal outreach message for Instagram DM or WhatsApp.

Lead username: {username}
Lead type: {lead_type}
Relevance score: {score}

The tone should be:
- Warm and approachable
- Not salesy
- Friendly and authentic

Return only the message.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Error generating message: {e})"

# Display each lead
updated_status = contacted_status.copy()

for _, row in filtered_df.iterrows():
    username = row['username']
    contacted = contacted_status.get(username, False)

    with st.expander(f"@{username} | Score: {row['lead_score']} | Type: {row['lead_type']}"):
        st.write(f"**Bio:** {row['bio']}")
        st.write(f"**Followers:** {row['followers']}")
        st.write(f"**Location:** {row['location']}")

        msg = generate_message(username, row['lead_type'], row['lead_score'])
        st.text_area("✉️ Suggested Message", msg, height=100, key=f"msg_{username}")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if row.get("whatsapp"):
                st.markdown(f"[📲 Open WhatsApp]({row['whatsapp']})", unsafe_allow_html=True)
            elif row.get("email"):
                st.markdown(f"[📧 Send Email](mailto:{row['email']})", unsafe_allow_html=True)
            else:
                st.markdown("⚠️ No contact method available.")

        with col2:
            st.code(msg, language="text")

        with col3:
            status = st.checkbox("✅ Mark as Contacted", value=contacted, key=f"check_{username}")
            updated_status[username] = status

# Save updated contacted status
with open(CONTACTED_FILE, "w", encoding="utf-8") as f:
    json.dump(updated_status, f, indent=2)

# Export CSV
filtered_df["message"] = filtered_df.apply(
    lambda row: generate_message(row["username"], row["lead_type"], row["lead_score"]), axis=1
)
filtered_df["contacted"] = filtered_df["username"].map(updated_status)

csv = filtered_df[[
    "username", "full_name", "lead_type", "lead_score", "location",
    "email", "phone", "whatsapp", "profile_url", "message", "contacted"
]].to_csv(index=False)

st.download_button(
    label="📥 Download All Leads + Messages as CSV",
    data=csv,
    file_name='sustaina_leads_with_messages.csv',
    mime='text/csv',
)
