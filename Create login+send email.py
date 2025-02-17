# The overall idea for this script is to create a login for new users while ensuring duplicates aren't created.
# Once the user account is created an email to the student/new user will be sent to their student email (aurora.edu).
# The content of the email will include the user credentials.

import os  # provides functions for interacting with the operating system.
import subprocess  # allows the running of external commands and interacting with them.
import sys  # provides access to system-specific parameters and functions.
import smtplib  # makes the simple mail transfer protocol (SMTP) library available.
from email.mime.multipart import MIMEMultipart  # used to create email messages that can contain multiple parts.
from email.mime.text import MIMEText  # used to create text-based email messages.


def check_root():
    """Ensure the script runs as root."""
    if os.geteuid() != 0:
        print("Script must be run as root.")
        sys.exit(1)


def get_filenames():
    """Retrieve input filenames from command-line arguments."""
    if len(sys.argv) < 3:
        print("Usage: sudo python3 script.py <username.csv> <credentials.txt>")
        sys.exit(1)
    return sys.argv[1], sys.argv[2]


def read_usernames(filename):
    """Read usernames from the CSV file."""
    try:
        with open(filename, "r") as f:
            return f.readline().strip().split(",")
# Within the file, the user information needs to be in the following format (user1,user2,user3,user4)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)


def read_credentials(filename):
    """Read email credentials from the text file."""
    try:
        with open(filename, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            # Within the file, the email and password need to be in the following format:
            # Line 1 - email@example.com
            # Line 2 - supersecretpassword
            if len(lines) < 2:
                print(f"Error: '{filename}' must contain at least two lines (email and password).")
                sys.exit(1)
            return lines[0], lines[1]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)


def run_command(cmd):
    """Execute a shell command with error handling."""
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"Command '{cmd}' executed successfully.")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else "Unknown error"
        print(f"Command '{cmd}' failed with error: {error_msg}.")
        sys.exit(1)


def send_email(sender_email, sender_password, receiver_email, subject, body):
    """Send an email to the newly created user."""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {receiver_email}.")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Check your email and password.")
    except smtplib.SMTPConnectError:
        print("Could not connect to SMTP server. Check network settings.")
    except Exception as e:
        print(f"Error sending email to {receiver_email}: {e}")


def create_or_update_user(username, sender_email, sender_password, default_password):
    """Create or update a user account and notify them via email."""
    home_dir = f"/home/{username}"
    recipient_email = f"{username}@aurora.edu"

    user_exists = subprocess.run(f"getent passwd {username}", shell=True, stdout=subprocess.DEVNULL).returncode == 0

    commands = []
    if user_exists:
        print(f"Updating existing user: {username}")
        commands = [
            f"mkdir -p {home_dir}/public_html",
            f"chown {username}:{username} {home_dir}/public_html",
            f"cp /home/dlash/public_html/helloworld1.html {home_dir}/public_html/helloworld.html",
            f"chmod 644 {home_dir}/public_html/helloworld.html",
            #644- user has permissions to read and write and everyone else has read-only permissions
            f"chown {username}:{username} {home_dir}/public_html/helloworld.html"
        ]
    else:
        print(f"Creating new user: {username}")
        commands = [
            f"useradd -m -s /bin/bash {username}",
            f"echo '{username}:{default_password}' | chpasswd",
            f"mkdir -p {home_dir}/public_html",
            f"chmod 755 {home_dir}/public_html",
            # 755 - owner has full read, write, execute; others can read and execute.
            f"chmod 755 {home_dir}",
            f"chown {username}:{username} {home_dir}",
            f"chown {username}:{username} {home_dir}/public_html",
            f"cp /home/dlash/public_html/helloworld1.html {home_dir}/public_html/helloworld.html",
            f"chmod 644 {home_dir}/public_html/helloworld.html",
            f"chown {username}:{username} {home_dir}/public_html/helloworld.html"
        ]

    for cmd in commands:
        run_command(cmd)

    email_subject = "Account Created"
    email_body = f"""
    Hello, {username}!,

    Here is your log-in info:
    Username: {username}
    Password: {default_password}

    Remember to change your temporary password.

    Aurora University IT Team
    """
    send_email(sender_email, sender_password, recipient_email, email_subject, email_body)


def main():
    check_root()
    input_file, credentials_file = get_filenames()
    usernames = read_usernames(input_file)
    sender_email, sender_password = read_credentials(credentials_file)
    default_password = "webclass1"

    for username in usernames:
        if username.strip():
            create_or_update_user(username.strip(), sender_email, sender_password, default_password)

    print("Script execution complete.")


if __name__ == "__main__":
    main()
