
import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

st.set_page_config(page_title="Hotel Maintenance Agent", layout="wide")

# Google Sheet replacement: use a CSV file (for deployment, link to Google Sheet or Firebase)
DATA_FILE = "maintenance_log.csv"

# Load or initialize data
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["ID", "Date", "Room", "Issue", "Urgency", "Status"])
    df.to_csv(DATA_FILE, index=False)

st.title("🏨 Hotel Maintenance AI Agent")

# New issue form
st.subheader("Report a New Issue")
with st.form("new_issue_form"):
    room = st.text_input("Room Number or Area", placeholder="e.g. 102 or Kitchen")
    issue = st.text_area("Describe the issue")
    urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])
    submitted = st.form_submit_button("Submit Issue")

    if submitted and room and issue:
        new_issue = {
            "ID": str(uuid.uuid4())[:8],
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Room": room,
            "Issue": issue,
            "Urgency": urgency,
            "Status": "Pending",
        }
        df = pd.concat([pd.DataFrame([new_issue]), df], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Issue submitted successfully.")

# Issue dashboard
st.subheader("🛠 Current Maintenance Issues")
status_filter = st.selectbox("Filter by status", ["All", "Pending", "In Progress", "Done"])

filtered_df = df if status_filter == "All" else df[df["Status"] == status_filter]
edited_df = st.data_editor(filtered_df, num_rows="dynamic", key="editor")

# Update data if any edits were made
if not edited_df.equals(filtered_df):
    df.update(edited_df)
    df.to_csv(DATA_FILE, index=False)
    st.success("Updates saved.")

# Analytics
st.subheader("📊 Maintenance Analytics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Issues", len(df))
col2.metric("Pending", len(df[df["Status"] == "Pending"]))
col3.metric("Done", len(df[df["Status"] == "Done"]))

urgency_chart = df["Urgency"].value_counts().rename_axis("Urgency").reset_index(name="Count")
st.bar_chart(urgency_chart.set_index("Urgency"))
