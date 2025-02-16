# This script must be run though a root domain
# The overall idea for this script is to create a login for new users
# while making sure duplicates arnt created
# once the user account is created it'll email the student/new user to their student email (aurora.edu)
# the content of the email will include the user credentials and instructions on how to sign-into the account


import os
import subprocess
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#making sure script runs as root
if os.geteuid() != 0:
    print("Script must be run as root.")
    sys.exit(1)

# reading filename from cmdl
if len(sys.argv) < 2:
    print("Usage: sudo python3 script.py <username.csv> <credentials.txt>")
    sys.exit(1)

input_file = sys.argv[1]
credentials_file = sys.argv[2]

#reading usernames from file
try:
    with open(input_file, "r") as f:
        usernames = f.readline().strip().split(",")
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)

# reading sender email and password from credentials file
try:
    with open(credentials_file, "r") as f:
        sender_email = f.readline().strip()
        sender_password = f.readline().strip()
except FileNotFoundError:
    print(f"Error: File '{credentials_file}' not found.")
    sys.exit(1)

#default password
default_password = "webclass1"

#error handling
def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Command '{cmd}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with exit code {e.stderr.decode().strip()}.")
        sys.exit(1)

# function to send email
def send_email (sender_email, sender_password, receiver_email, subject, body):
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

        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# iterating over the usernames
for username in usernames:
    username = username.strip()
    home_dir = f"/home/{username}"
    recipient_email = f"{username}@aurora.edu"


    #checking if user exits
    user_exists = subprocess.run(f"getent passwd {username}", shell=True, stdout=subprocess.PIPE).returncode == 0

    if user_exists:
        commands = [
            f"chown {username} {home_dir}/",
            f"mkdir -p {home_dir}/public_html",
            f"chown {username} {home_dir}/public_html",
            f"cp /home/dlash/public_html/helloworld1.html {home_dir}/public_html/helloworld.html",
            f"chmod 777 {home_dir}/public_html/helloworld.html",
            f"chown {username} {home_dir}/public_html/helloworld.html"
        ]
    #if user doesnt exist
    else:
        print(f"Creating... {home_dir}")
        commands = [
            f"adduser {username}",
            f"echo '{username}:{default_password}' | chpasswd",
            f"mkdir -p {home_dir}/public_html",
            f"chmod 755 {home_dir}/public_html",
            f"chmod 755 {home_dir}",
            f"chown {username} {home_dir}",
            f"chown {username} {home_dir}/public_html",
            f"cp /home/dlash/public_html/helloworld1.html {home_dir}/public_html/helloworld.html",
            f"chmod 777 {home_dir}/public_html/helloworld.html",
            f"chown {username} {home_dir}/public_html/helloworld.html"
        ]
    #     send email to notify users of account creation
    email_subject = "Account Created"
    email_body = f"Hello, {username}!,\n\nHere is your log-in info: \nUsername:{username}\nPassword:{default_password}\n\nRemember to change your temporary password, \nAurora University IT Team"
    send_email(sender_email, sender_password, recipient_email, email_subject, email_body)

    #executing the commands
    for cmd in commands:
        run_command(cmd)
print("Script execution complete.")