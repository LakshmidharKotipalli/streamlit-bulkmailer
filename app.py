import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Optional Access Password (set this to something secret)
ACCESS_PASSWORD = "bulkmailer123"

st.set_page_config(page_title="🔐 Bulk Mailer", layout="centered")
st.title("🔐 Secure Bulk Mailer for Trusted Users")

# 🔑 Require an access password
access = st.text_input("Enter access password to use the app", type="password")
if access != ACCESS_PASSWORD:
    st.warning("Please enter the correct access password to continue.")
    st.stop()

st.markdown("""
Upload a file with `email` and `name` columns. Use `$name` in subject or body to customize.
""")

with st.form("mail_form"):
    email = st.text_input("Your Email")
    password = st.text_input("App/SMTP Password", type="password")
    subject = st.text_input("Subject (use $name for personalization)")
    body = st.text_area("Email Body (use $name)", height=150)
    file = st.file_uploader("Upload .csv/.xlsx/.json file", type=["csv", "xlsx", "json"])
    send = st.form_submit_button("Send Emails")

if send:
    if not email or not password or not subject or not body or not file:
        st.error("Please complete all fields and upload a file.")
    else:
        try:
            # Read uploaded file
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            elif file.name.endswith(".json"):
                df = pd.read_json(file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            if "email" not in df.columns or "name" not in df.columns:
                st.error("File must contain 'email' and 'name' columns.")
                st.stop()

            # Detect SMTP server
            domain = email.split("@")[1]
            smtp_server = "smtp.gmail.com" if domain == "gmail.com" else f"mail.{domain}"
            smtp_port = 587

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email, password)

            success = 0
            failure = 0

            with st.spinner("Sending emails..."):
                for _, row in df.iterrows():
                    recipient = str(row["email"]).strip()
                    name_raw = row["name"]
                    name = str(name_raw).strip() if pd.notna(name_raw) else "there"

                    subject_filled = subject.replace("$name", name)
                    body_filled = body.replace("$name", name)

                    msg = MIMEMultipart()
                    msg["From"] = email
                    msg["To"] = recipient
                    msg["Subject"] = subject_filled
                    msg.attach(MIMEText(body_filled, "plain"))

                    try:
                        server.sendmail(email, recipient, msg.as_string())
                        success += 1
                    except Exception:
                        failure += 1

            server.quit()
            st.success(f"✅ Sent: {success}, ❌ Failed: {failure}")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
