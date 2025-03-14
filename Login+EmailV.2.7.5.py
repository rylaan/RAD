import os
import subprocess
import sys
import smtplib
import pwd
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def check_root():
    """Ensure the script is run as root."""
    if os.geteuid() != 0:
        print "Script must be run as root."
        sys.exit(1)


def get_filenames():
    """Retrieve input filenames from command-line arguments."""
    if len(sys.argv) < 3:
        print "Usage: sudo python script.py <username.csv> <credentials.txt>"
        sys.exit(1)
    return sys.argv[1], sys.argv[2]


def read_usernames(filename):
    """Read the list of usernames from a CSV file."""
    try:
        with open(filename, "r") as f:
            return f.read().strip().split(",")  # More efficient reading
    except IOError:
        print "Error: File '{}' not found.".format(filename)
        sys.exit(1)


def read_credentials(filename):
    """Read email credentials from a file."""
    try:
        with open(filename, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            if len(lines) < 2:
                print "Error: '{}' must contain at least two lines (email and password).".format(filename)
                sys.exit(1)
            return lines[0], lines[1]
    except IOError:
        print "Error: File '{}' not found.".format(filename)
        sys.exit(1)


def user_exists(username):
    """Check if a user already exists on the system."""
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def run_command(cmd):
    """Execute a shell command safely."""
    try:
        subprocess.check_call(cmd, shell=True)
        print "Command '{}' executed successfully.".format(cmd)
    except subprocess.CalledProcessError as e:
        print "Command '{}' failed with error: {}".format(cmd, str(e))
        sys.exit(1)


def send_email(sender_email, sender_password, receiver_email, subject, body):
    """Send an email notification with credentials."""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print "Email sent successfully to {}.".format(receiver_email)
    except smtplib.SMTPException as e:
        print "Error sending email to {}: {}".format(receiver_email, str(e))


def create_or_update_user(username, sender_email, sender_password, default_password):
    """Create or update a user account and send login credentials via email."""
    home_dir = "/home/{}".format(username)
    recipient_email = "{}@aurora.edu".format(username)

    if user_exists(username):
        print "Updating existing user: {}".format(username)
        commands = [
            "mkdir -p {}/public_html".format(home_dir),
            "chown {}:{} {}/public_html".format(username, username, home_dir),
            "cp /home/dlash/public_html/helloworld1.html {}/public_html/helloworld.html".format(home_dir),
            "chmod 644 {}/public_html/helloworld.html".format(home_dir),
            "chown {}:{} {}/public_html/helloworld.html".format(username, username, home_dir)
        ]
    else:
        print "Creating new user: {}".format(username)
        commands = [
            "useradd -m -s /bin/bash {}".format(username),
            "echo '{}:{}' | chpasswd".format(username, default_password),
            "mkdir -p {}/public_html".format(home_dir),
            "chmod 755 {}/public_html".format(home_dir),
            "chmod 755 {}".format(home_dir),
            "chown {}:{} {}".format(username, username, home_dir),
            "chown {}:{} {}/public_html".format(username, username, home_dir),
            "cp /home/dlash/public_html/helloworld1.html {}/public_html/helloworld.html".format(home_dir),
            "chmod 644 {}/public_html/helloworld.html".format(home_dir),
            "chown {}:{} {}/public_html/helloworld.html".format(username, username, home_dir)
        ]

    for cmd in commands:
        run_command(cmd)

    email_subject = "Account Created"
    email_body = """
    Hello, {}!

    Here is your log-in info:
    Username: {}
    Password: {}

    Remember to change your temporary password.

    Aurora University IT Team
    """.format(username, username, default_password)

    send_email(sender_email, sender_password, recipient_email, email_subject, email_body)


def main():
    """Main function to process user creation and notifications."""
    check_root()
    input_file, credentials_file = get_filenames()
    usernames = read_usernames(input_file)
    sender_email, sender_password = read_credentials(credentials_file)

    # Get password securely
    default_password = os.environ.get("DEFAULT_PASSWORD", None)
    if not default_password:
        default_password = getpass.getpass("Enter default password: ")

    for username in usernames:
        if username.strip():
            create_or_update_user(username.strip(), sender_email, sender_password, default_password)

    print "Script execution complete."


if __name__ == "__main__":
    main()
