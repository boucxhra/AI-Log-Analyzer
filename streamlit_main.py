import streamlit as st

from analyzer import analyze_logs, extract_ips, extract_usernames, extract_timestamps
from report import save_report

st.title("AI Log Analyzer")

uploaded_file = st.file_uploader("Upload a log file", type=["log", "txt"])
if uploaded_file:
    logs = uploaded_file.read().decode("utf-8")
    report = analyze_logs(logs)  # Now returns a dict

    if "error" in report:
        st.error(report["error"])
        st.text(report.get("raw", ""))
    else:
        st.subheader("AI Security Report")
        st.write(report["summary"])

        severity = report["severity_level"]
        score = report["severity_score"]

        # Show severity with colors
        if severity.lower() in ["high", "critical"]:
            st.error(f"Severity: {severity} (Score {score})")
        elif severity.lower() == "medium":
            st.warning(f"Severity: {severity} (Score {score})")
        else:
            st.success(f"Severity: {severity} (Score {score})")

        # Threat Types
        st.subheader("Threat Types")
        for threat in report["threat_types"]:
            st.write(f"- {threat}")

        # Suspicious IPs
        st.subheader("Suspicious IPs")
        st.table({"IP Address": report["suspicious_ips"]})

        # Indicators of Compromise
        st.subheader("Indicators of Compromise")
        for ioc in report["ioc"]:
            st.write(f"- {ioc}")

        # Recommended Actions
        st.subheader("Recommended Actions")
        for action in report["recommended_actions"]:
            st.write(f"- {action}")

        if st.button("Save Report"):
            path = save_report(report, prefix="report")
            st.success(f"Report saved to {path}")

# Extracted IPs
st.subheader("Extracted IPs from Logs")
ips = extract_ips(logs)
if ips:
    st.table({"IP Address": ips})
else:
    st.info("No IPs found in logs.")

# Extracted Usernames
st.subheader("Extracted Usernames from Logs")
users = extract_usernames(logs)
if users:
    for user in users:
        st.write(f"- {user}")
else:
    st.info("No usernames found in logs.")

# Extracted Timestamps
st.subheader("Extracted Timestamps from Logs")
timestamps = extract_timestamps(logs)
if timestamps:
    st.table({"Timestamp": timestamps})
else:
    st.info("No timestamps found in logs.")
