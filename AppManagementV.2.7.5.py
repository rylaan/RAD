import time  # Retrieves the current time, waits during code execution, and measures efficiency.
import psutil  # Used to retrieve information about running processes and system utilization.
import smtplib  # Defines the SMTP client that can be used to send an email.
import subprocess  # Allows the running of external commands and interacting with them.
from email.mime.text import MIMEText  # Used to create text-based email messages.

# Configuration
APP_NAME = "your_application_name"  # Replace with the actual application name
START_COMMAND = "your_application_command"  # Command to start the application
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_RECEIVER = "recipient_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"  # Use environment variables for security
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CHECK_INTERVAL = 3600  # 1 hour in seconds

def is_application_running(app_name):
    """Check if the application is running by its name."""
    for process in psutil.process_iter():
        try:
            if process.name == app_name:  # In Python 2, use `process.name`
                return True
        except psutil.NoSuchProcess:
            pass  # Process may have ended, ignore error
    return False

def restart_application():
    """Restart the application."""
    try:
        subprocess.Popen(START_COMMAND, shell=True)
        print "Application {} restarted successfully.".format(APP_NAME)  # FIXED print statement
    except Exception as e:
        print "Failed to restart application: {}".format(str(e))  # FIXED print statement

def send_email(subject, body):
    """Send an email notification."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        print "Alert email sent."  # FIXED print statement
    except Exception as e:
        print "Failed to send email: {}".format(str(e))  # FIXED print statement

def main():
    """Main function to monitor and restart the application if needed."""
    while True:
        if not is_application_running(APP_NAME):
            print "{} is not running! Restarting...".format(APP_NAME)  # FIXED print statement
            send_email("Alert: {} is Down".format(APP_NAME),
                       "{} was not running and has been restarted.".format(APP_NAME))
            restart_application()
        else:
            print "Application {} is running normally.".format(APP_NAME)  # FIXED print statement

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
