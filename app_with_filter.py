
import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

st.set_page_config(page_title="Hotel Maintenance Dashboard", layout="wide")
st.title("🏨 Hotel Maintenance Agent")

CSV_FILE = "jobs.csv"

# Material mapping
MATERIALS_MAP = {
    "safe battery": {"item": "AA battery", "quantity": 4},
    "tv remote": {"item": "AA battery", "quantity": 2},
    "flusher": {"item": "Flusher valve", "quantity": 1},
    "reading light": {"item": "Switch", "quantity": 1},
    "light": {"item": "Globe", "quantity": 1},
}

def extract_jobs_from_text(text):
    lines = text.strip().split('\n')
    entries = []
    for line in lines:
        match = re.search(r'(Room|Rm)?\s*(\d{3})\D+(.*)', line, re.IGNORECASE)
        if match:
            room = match.group(2)
            desc = match.group(3).strip(" -:|")
            entries.append({
                "Room": room,
                "Job Description": desc,
                "Status": "Open",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    return pd.DataFrame(entries)

# Upload jobs section
st.subheader("📋 Paste Jobs from Knowcross")
user_input = st.text_area("Paste job list", height=200, placeholder="Paste Knowcross job list here...")

if st.button("➕ Add Jobs"):
    if user_input.strip():
        new_df = extract_jobs_from_text(user_input)
        if not new_df.empty:
            try:
                existing = pd.read_csv(CSV_FILE)
                combined = pd.concat([existing, new_df], ignore_index=True)
            except FileNotFoundError:
                combined = new_df
            combined.to_csv(CSV_FILE, index=False)
            st.success(f"Added {len(new_df)} new job(s).")
        else:
            st.warning("No valid job entries found.")
    else:
        st.warning("Please paste job entries.")

# Load data
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df["Room"] = df["Room"].astype(str)

    # Filter section
    st.subheader("🔍 Filter Jobs")
    room_filter = st.text_input("Filter by Room Number")
    job_filter = st.text_input("Filter by Job Type")

    if room_filter:
        df = df[df["Room"].str.contains(room_filter.strip(), case=False)]

    if job_filter:
        df = df[df["Job Description"].str.contains(job_filter.strip(), case=False)]

    st.subheader("📊 Dashboard")
    job_counts = df.groupby("Job Description")["Status"].count().rename("Total")
    closed_counts = df[df["Status"] == "Closed"].groupby("Job Description")["Status"].count().rename("Closed")
    dashboard = pd.concat([job_counts, closed_counts], axis=1).fillna(0).astype(int)
    st.dataframe(dashboard.reset_index(), use_container_width=True)

    st.subheader("📦 Consumer Materials Required")
    materials_needed = {}
    for _, row in df[df["Status"] == "Open"].iterrows():
        desc = row["Job Description"].lower()
        for keyword, mat in MATERIALS_MAP.items():
            if keyword in desc:
                key = mat["item"]
                materials_needed[key] = materials_needed.get(key, 0) + mat["quantity"]
                break

    if materials_needed:
        materials_df = pd.DataFrame([{"Item": k, "Quantity": v} for k, v in materials_needed.items()])
        st.table(materials_df)
    else:
        st.info("No matching consumer materials for open jobs.")

    st.subheader("🛠 Update Job Status")
    for i, row in df.iterrows():
        col1, col2 = st.columns([6, 2])
        with col1:
            st.markdown(f"**Room {row['Room']}** — {row['Job Description']} ({row['Status']})")
        with col2:
            if row["Status"] == "Open":
                if st.button("✅ Close", key=f"close_{i}"):
                    df.at[i, "Status"] = "Closed"
                    df.to_csv(CSV_FILE, index=False)
                    st.experimental_rerun()
else:
    st.info("Paste job entries above to start tracking.")
