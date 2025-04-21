import os
import subprocess
import mysql.connector
from datetime import datetime

# === CONFIG ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DELETE_LIST_FILE = os.path.join(SCRIPT_DIR, "delete_students.txt")
LOG_FILE = os.path.join(SCRIPT_DIR, "deleted_students.log")
BASE_DIR = "/var/www/student_projects"
GROUP = "www-data"

# MySQL credentials
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace with your actual MySQL root password
    'host': 'localhost',
    'database': 'student_users',
    'unix_socket': '/opt/bitnami/mariadb/tmp/mysql.sock'
}

def log_deletion(username, success=True, error_msg=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "DELETED" if success else f"FAILED: {error_msg}"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{timestamp}] {username} - {status}\n")

def delete_user(username):
    username = username.strip()

    if not username or len(username) < 4:
        print(f"Skipping invalid username: {username}")
        return

    try:
        # Delete from MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()

        # Delete the user account and home directory
        subprocess.run(['sudo', 'userdel', '-r', username], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Delete their project folder (just in case it still exists)
        user_dir = os.path.join(BASE_DIR, username)
        if os.path.exists(user_dir):
            subprocess.run(['sudo', 'rm', '-rf', user_dir])

        print(f"✅ Deleted {username}")
        log_deletion(username)

    except Exception as e:
        print(f"❌ Error deleting {username}: {e}")
        log_deletion(username, success=False, error_msg=str(e))

def main():
    if not os.path.exists(DELETE_LIST_FILE):
        print(f"❌ Error: '{DELETE_LIST_FILE}' not found.")
        return

    with open(DELETE_LIST_FILE, 'r') as file:
        contents = file.read()

        # Support both comma-separated or newline-separated usernames
        if ',' in contents:
            usernames = contents.split(',')
        else:
            usernames = contents.splitlines()

    for username in usernames:
        delete_user(username.strip())

if __name__ == "__main__":
    main()
