
import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Hotel Maintenance Agent", layout="wide")
st.title("🏨 Hotel Maintenance - Bulk Job Manager")

# Load existing jobs if present
def load_jobs():
    try:
        return pd.read_csv("bulk_jobs.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Room", "Job", "Status"])

# Save jobs to CSV
def save_jobs(df):
    df.to_csv("bulk_jobs.csv", index=False)

jobs_df = load_jobs()

# Paste job input section
st.subheader("📋 Paste Jobs from Knowcross or Other System")
with st.form("paste_form"):
    pasted_text = st.text_area("Paste job list here (Format: Room | Job description)", height=200)
    submit = st.form_submit_button("Submit Jobs")

    if submit and pasted_text:
        new_entries = []
        lines = pasted_text.strip().splitlines()
        for line in lines:
            if '|' in line:
                parts = [p.strip() for p in line.split('|', 1)]
                if len(parts) == 2:
                    new_entries.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Room": parts[0],
                        "Job": parts[1],
                        "Status": "Open"
                    })

        if new_entries:
            new_df = pd.DataFrame(new_entries)
            jobs_df = pd.concat([jobs_df, new_df], ignore_index=True)
            save_jobs(jobs_df)
            st.success(f"✅ {len(new_entries)} job(s) added successfully!")

# Show filter and dashboard
st.subheader("📊 Maintenance Dashboard")
if not jobs_df.empty:
    room_filter = st.selectbox("Filter by Room", options=["All"] + sorted(jobs_df['Room'].unique()))
    if room_filter != "All":
        filtered_df = jobs_df[jobs_df['Room'] == room_filter]
    else:
        filtered_df = jobs_df

    st.dataframe(filtered_df, use_container_width=True)

    # Close jobs section
    st.subheader("✅ Close Completed Jobs")
    open_jobs = jobs_df[jobs_df['Status'] != 'Closed']
    for idx, row in open_jobs.iterrows():
        if st.checkbox(f"{row['Room']} - {row['Job']}", key=f"close_{idx}"):
            jobs_df.at[idx, 'Status'] = 'Closed'
            save_jobs(jobs_df)
            st.success(f"Job closed: {row['Room']} - {row['Job']}")

    # Job count summary
    st.markdown("---")
    st.subheader("🔢 Job Summary by Room")
    summary = jobs_df[jobs_df['Status'] != 'Closed'].groupby("Room").size().reset_index(name="Job Count")
    st.bar_chart(summary.set_index("Room"))
else:
    st.info("No jobs found. Paste job data to get started.")
