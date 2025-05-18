
import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.set_page_config(page_title="Consumer Materials Generator", layout="wide")
st.title("🔧 Hotel Consumer Material Calculator")

# Define job-to-material rules
MATERIAL_RULES = {
    "shower silicon": {"material": "Grey Silicon", "rate": 2},
    "bathtub silicon": {"material": "White Silicon", "rate": 3},
    "silicon": {"material": "Blade", "rate": 2},
    "safe battery": {"material": "AA Battery", "quantity": 4},
    "tv remote": {"material": "AA Battery", "quantity": 2},
    "door battery": {"material": ["AA Battery", "6V Alkaline Battery"], "quantity": [4, 1]},
    "flusher": {"material": "Flusher Valve", "quantity": 1},
    "reading light": {"material": "Switch", "quantity": 1},
    "light": {"material": "Globe", "quantity": 1},
    "replace": {"material": "Check/Identify", "quantity": 1},
    "missing": {"material": "Check/Identify", "quantity": 1}
}

def extract_jobs(text):
    jobs = []
    lines = text.strip().split("\n")
    for line in lines:
        match = re.search(r"(Room|Rm)?\s*(\d{3})\D+(.*)", line, re.IGNORECASE)
        if match:
            room = match.group(2)
            desc = match.group(3).strip(" -:|")
            jobs.append({"Room": room, "Job": desc})
    return jobs

def calculate_materials(jobs):
    counts = defaultdict(int)
    for job in jobs:
        desc = job["Job"].lower()
        for keyword, rule in MATERIAL_RULES.items():
            if keyword in desc:
                counts[keyword] += 1

    materials_needed = defaultdict(int)
    for keyword, count in counts.items():
        rule = MATERIAL_RULES[keyword]
        if "rate" in rule:
            materials_needed[rule["material"]] += count // rule["rate"]
        elif isinstance(rule["material"], list):
            for i in range(len(rule["material"])):
                materials_needed[rule["material"][i]] += count * rule["quantity"][i]
        else:
            materials_needed[rule["material"]] += count * rule["quantity"]

    return dict(materials_needed)

# Input area
st.subheader("📋 Paste Knowcross Job List")
text_input = st.text_area("Paste job entries copied from Knowcross below:", height=250)

if st.button("🧾 Generate Materials List"):
    if not text_input.strip():
        st.warning("Please paste job entries first.")
    else:
        jobs = extract_jobs(text_input)
        if not jobs:
            st.error("No valid job entries found.")
        else:
            st.success(f"✅ {len(jobs)} job(s) processed.")
            job_df = pd.DataFrame(jobs)
            st.subheader("📝 Extracted Jobs")
            st.dataframe(job_df)

            materials = calculate_materials(jobs)
            if materials:
                st.subheader("📦 Consumer Materials Needed")
                mat_df = pd.DataFrame([{"Material": k, "Quantity": v} for k, v in materials.items()])
                st.table(mat_df)
            else:
                st.info("No materials matched the current job list.")
