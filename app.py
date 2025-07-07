import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="📬 Bulk Mailer", layout="centered")
st.title("📬 Bulk Mailer with Custom Names")

st.markdown("""
Upload a file with `email` and `name` columns. You can use `$name` in the subject or body to personalize your emails.
""")

with st.form("mail_form"):
    email = st.text_input("Your Email")
    password = st.text_input("App/SMTP Password", type="password")
    subject = st.text_input("Subject (you can use $name)")
    body = st.text_area("Email Body (you can use $name)", height=150)
    file = st.file_uploader("Upload file (.csv, .xlsx, .json)", type=["csv", "xlsx", "json"])
    send = st.form_submit_button("Send Emails")

if send:
    if not email or not password or not subject or not body or not file:
        st.error("Please fill all fields and upload a file.")
    else:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            elif file.name.endswith(".json"):
                df = pd.read_json(file)
            else:
                st.error("Unsupported file type")
                st.stop()

            if "email" not in df.columns or "name" not in df.columns:
                st.error("File must contain 'email' and 'name' columns")
                st.stop()

            domain = email.split("@")[1]
            smtp_server = "smtp.gmail.com" if domain == "gmail.com" else f"mail.{domain}"
            smtp_port = 587

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email, password)

            successes = 0
            failures = 0

            with st.spinner("Sending emails..."):
                for _, row in df.iterrows():
                    recipient = str(row["email"]).strip()
                    name_raw = row["name"]
                    name = str(name_raw).strip() if pd.notna(name_raw) else "there"

                    personalized_subject = subject.replace("$name", name)
                    personalized_body = body.replace("$name", name)

                    msg = MIMEMultipart()
                    msg["From"] = email
                    msg["To"] = recipient
                    msg["Subject"] = personalized_subject
                    msg.attach(MIMEText(personalized_body, "plain"))

                    try:
                        server.sendmail(email, recipient, msg.as_string())
                        successes += 1
                    except Exception as e:
                        failures += 1

            server.quit()
            st.success(f"✅ Emails sent: {successes}, ❌ Failed: {failures}")

        except Exception as e:
            st.error(f"Error: {str(e)}")
