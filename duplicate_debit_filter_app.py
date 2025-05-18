
import streamlit as st
import pandas as pd
import re
from io import StringIO
from collections import defaultdict

st.set_page_config(page_title="Duplicate Debit Filter", layout="wide")
st.title("💳 Duplicate Debit Amount Filter")

st.markdown("Upload or paste your bank statement text. This app will extract **debit entries**, detect **duplicate amounts**, and group them.")

def extract_entries(text):
    lines = text.strip().split("\n")
    entries = []
    for line in lines:
        line = line.strip()
        # Match lines with a debit amount, e.g., -$316.70 or -316.70
        match = re.search(r"(?P<amount>\-\$?\d{1,5}[.,]?\d{0,2})", line)
        if match:
            amount_raw = match.group("amount")
            # Clean and normalize amount
            amount = float(amount_raw.replace("$", "").replace(",", ""))
            # Try to extract some form of merchant/institute name
            desc_match = re.search(r"Transfer to|POS|Direct Debit|DEPT OF|Transfer To|CommBank|NetBank|Importers|EMI|RED.*?\s+(.*?)(\s+\$|\-|$)", line, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else line[:50]
            entries.append({
                "Line": line,
                "Amount": amount,
                "Institute": description
            })
    return entries

st.subheader("📋 Input Text")
input_text = st.text_area("Paste bank transaction entries here:", height=300)

if st.button("🔍 Find Duplicates"):
    if not input_text.strip():
        st.warning("Please paste some data first.")
    else:
        entries = extract_entries(input_text)
        if not entries:
            st.error("No valid debit entries found.")
        else:
            df = pd.DataFrame(entries)
            dup_df = df[df.duplicated(["Amount"], keep=False)].sort_values("Amount")
            st.subheader("📌 All Debit Entries")
            st.dataframe(df)

            st.subheader("❗ Duplicate Debit Amounts")
            if not dup_df.empty:
                st.dataframe(dup_df)
                csv = dup_df.to_csv(index=False).encode("utf-8")
                st.download_button("💾 Download Duplicates as CSV", csv, "duplicate_debits.csv", "text/csv")
            else:
                st.success("No duplicate debit amounts found.")
