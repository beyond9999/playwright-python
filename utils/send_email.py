import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import zipfile

# Set the email sender and recipient addresses and 01_login credentials
sender_email = "sender@example.com"
receiver_email = "receiver@example.com"
sender_password = "password"

# Set the SMTP server and port number
smtp_server = "smtp.example.com"
smtp_port = 587

# Set the path to the Allure report directory
report_dir = "/path/to/allure/report"

# Zip the Allure report directory
zipfile_name = "allure_report.zip"
zipfile_path = os.path.join(report_dir, zipfile_name)
zipfile.ZipFile(zipfile_path, mode="w").write(report_dir)

# Create a message object and set its attributes
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "Allure Test Report"
msg.attach(MIMEText("Please find the attached Allure test report."))

# Add the zipped Allure report to the message object
with open(zipfile_path, "rb") as f:
    attachment = MIMEApplication(f.read(), _subtype="zip")
    attachment.add_header("Content-Disposition", "attachment", filename=zipfile_name)
    msg.attach(attachment)

# Send the email using SMTP
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)

# Remove the zipped Allure report
os.remove(zipfile_path)