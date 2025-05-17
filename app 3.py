
import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

st.set_page_config(page_title="Hotel Maintenance Agent", layout="wide")

st.title("🏨 Hotel Maintenance Dashboard")

def extract_jobs_from_text(pasted_text):
    lines = pasted_text.strip().split('\n')
    job_entries = []

    for line in lines:
        match = re.search(r'(Room|Rm)?\s*(\d{3})\D+(.*)', line, re.IGNORECASE)
        if match:
            room = match.group(2)
            description = match.group(3).strip(" -:|")
            job_entries.append({
                "Room": room,
                "Job Description": description,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    return pd.DataFrame(job_entries)

# Section 1: Paste jobs
st.subheader("📋 Paste Jobs from Knowcross or Other App")
pasted_text = st.text_area("Paste multiple job entries here", height=200,
                           placeholder="Example:\nRoom 302 - Door lock not working\n105: AC not cooling\nRm 407 Toilet blocked")

if st.button("➕ Add Jobs to Dashboard"):
    if pasted_text.strip():
        new_jobs = extract_jobs_from_text(pasted_text)
        if not new_jobs.empty:
            try:
                existing_jobs = pd.read_csv("jobs.csv")
                combined = pd.concat([existing_jobs, new_jobs], ignore_index=True)
            except FileNotFoundError:
                combined = new_jobs

            combined.to_csv("jobs.csv", index=False)
            st.success(f"{len(new_jobs)} job(s) added!")
        else:
            st.warning("No valid job entries detected.")
    else:
        st.warning("Please paste job entries before clicking add.")

# Section 2: Dashboard
st.subheader("📊 Job Dashboard")
try:
    jobs = pd.read_csv("jobs.csv")
    jobs["Room"] = jobs["Room"].astype(str)
    rooms = sorted(jobs["Room"].unique())

    selected_rooms = st.multiselect("Filter by room number", rooms, default=rooms)
    filtered_jobs = jobs[jobs["Room"].isin(selected_rooms)]
    st.dataframe(filtered_jobs.reset_index(drop=True), use_container_width=True)

except FileNotFoundError:
    st.info("No jobs yet. Paste and submit jobs to populate dashboard.")
