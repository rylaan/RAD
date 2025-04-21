import os
import subprocess
import mysql.connector
from datetime import datetime

# === CONFIG ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_LIST_FILE = os.path.join(SCRIPT_DIR, "student_emails.txt")
BASE_DIR = "/var/www/student_projects"
DEFAULT_PASSWORD = "password"
GROUP = "www-data"

# MySQL credentials
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace with your actual MySQL password
    'host': 'localhost',
    'database': 'student_users',
    'unix_socket': '/opt/bitnami/mariadb/tmp/mysql.sock'
}

def create_user(username):
    username = username.strip()

    if not username or len(username) < 4:
        print(f"Skipping invalid username: {username}")
        return

    try:
        # Check if the user already exists
        result = subprocess.run(['id', username], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            print(f"User {username} already exists. Skipping.")
            return

        # Create the Linux user
        subprocess.run(['sudo', 'useradd', '-m', '-d', f'{BASE_DIR}/{username}', '-s', '/bin/bash', username])
        subprocess.run(['sudo', 'chpasswd'], input=f"{username}:{DEFAULT_PASSWORD}".encode())

        # Set up directory permissions
        subprocess.run(['sudo', 'mkdir', '-p', f'{BASE_DIR}/{username}'])
        subprocess.run(['sudo', 'chown', f'{username}:{GROUP}', f'{BASE_DIR}/{username}'])
        subprocess.run(['sudo', 'chmod', '755', f'{BASE_DIR}/{username}'])

        print(f"✅ Created user: {username}")

        # Log the user to the database
        log_user_to_database(username, f"{BASE_DIR}/{username}", DEFAULT_PASSWORD)

    except Exception as e:
        print(f"❌ Error creating user {username}: {e}")

def log_user_to_database(username, home_dir, password):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, home_directory, default_password)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE created_at = CURRENT_TIMESTAMP
        """, (username, home_dir, password))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"📝 Logged {username} to database.")
    except Exception as e:
        print(f"❌ Error logging user to database: {e}")

def main():
    if not os.path.exists(USER_LIST_FILE):
        print(f"❌ Error: '{USER_LIST_FILE}' not found.")
        return

    with open(USER_LIST_FILE, 'r') as file:
        contents = file.read()

        # Support both comma-separated and newline-separated formats
        if ',' in contents:
            usernames = contents.split(',')
        else:
            usernames = contents.splitlines()

    for username in usernames:
        create_user(username.strip())

if __name__ == "__main__":
    main()
