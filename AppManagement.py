# The overall idea for the following code is to monitor an application.
# Every 1 hour the application is checked to make sure there are no issues.
# If the application is down it will be restarted.
# Once restarted an email will be sent that informs the user the application status.

import time #retreives the current time, waiting during code execution, and measures code efficiency.
import psutil #used to retrieve information about running processes and system utilization.
import smtplib #defines the SMTP client that can be used to send an email.
import subprocess#allows the running of external commands and interacting with them.
from email.mime.text import MIMEText # used to create text-based email messages.

# Configuration
APP_NAME = "your_application_name"  # Replace with the actual application name
START_COMMAND = "your_application_command"  # Command to start the application
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_RECEIVER = "recipient_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"  # Use environment variables for security
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CHECK_INTERVAL = 3600 #1 hr in seconds


def is_application_running(app_name):
    """Check if the application is running by its name."""
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == app_name:
            return True
    return False


def restart_application():
    """Restart the application."""
    try:
        subprocess.Popen(START_COMMAND, shell=True)
        print(f"Application {APP_NAME} restarted successfully.")
    except Exception as e:
        print(f"Failed to restart application: {e}")


def send_email(subject, body):
    """Send an email notification."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    """Main function to monitor and restart the application if needed."""
    while True:
        if not is_application_running(APP_NAME):
            print(f"{APP_NAME} is not running! Restarting...")
            send_email(f"Alert: {APP_NAME} is Down", f"{APP_NAME} was not running and has been restarted.")
            restart_application()
        else:
            print(f"Application {APP_NAME} is running normally.")

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()