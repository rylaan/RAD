import os
import subprocess
import sys
import pwd
import getpass
from datetime import datetime

def check_root():
    if os.geteuid() != 0:
        print("Script must be run as root.")
        sys.exit(1)

def get_filenames():
    if len(sys.argv) < 2:
        print("Usage: sudo python script.py <username.csv>")
        sys.exit(1)
    return sys.argv[1]

def read_usernames(filename):
    try:
        with open(filename, "r") as f:
            return f.read().strip().split(",")
    except IOError:
        print("Error: File '{}' not found.".format(filename))
        sys.exit(1)

def user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

def run_command(cmd):
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        return False
    return True

def create_or_update_user(username, default_password, log_file):
    home_dir = "/home/{}".format(username)
    timestamp = datetime.now().strftime("%m-%d-%y %I:%M%p").lower()

    def log(reason):
        with open(log_file, "a") as logf:
            logf.write("Failed {} on {}: {}\n".format(username, timestamp, reason))

    if user_exists(username):
        log("User already exists.")
        return

    commands = [
        ("useradd -m -s /bin/bash {}".format(username), "User creation failed"),
        ("echo '{}:{}' | chpasswd".format(username, default_password), "Setting password failed"),
        ("mkdir -p {}/public_html".format(home_dir), "Creating public_html failed"),
        ("chmod 755 {}/public_html".format(home_dir), "Setting permissions for public_html failed"),
        ("chmod 755 {}".format(home_dir), "Setting permissions for home directory failed"),
        ("chown {}:{} {}".format(username, username, home_dir), "Setting ownership of home directory failed"),
        ("chown {}:{} {}/public_html".format(username, username, home_dir), "Setting ownership of public_html failed"),
        ("cp /home/dlash/public_html/helloworld1.html {}/public_html/helloworld.html".format(home_dir), "Copying HTML file failed"),
        ("chmod 644 {}/public_html/helloworld.html".format(home_dir), "Setting permissions on HTML file failed"),
        ("chown {}:{} {}/public_html/helloworld.html".format(username, username, home_dir), "Setting ownership of HTML file failed")
    ]

    for cmd, err_msg in commands:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            log("{}: {}".format(err_msg, err.decode().strip()))
            return

    with open(log_file, "a") as logf:
        logf.write("Created {} on {} pass:{} user:{}\n".format(username, timestamp, default_password, username))

def main():
    check_root()
    input_file = get_filenames()
    usernames = read_usernames(input_file)

    default_password = os.environ.get("DEFAULT_PASSWORD", None)
    if not default_password:
        default_password = getpass.getpass("Enter default password: ")

    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    log_filepath = os.path.join(os.getcwd(), log_filename)

    for username in usernames:
        if username.strip():
            create_or_update_user(username.strip(), default_password, log_filepath)

    print("Script execution complete. Log saved to {}".format(log_filepath))

if __name__ == "__main__":
    main()
