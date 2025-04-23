import os
import subprocess
import mysql.connector
from datetime import datetime

# === CONFIG ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_LIST_FILE = os.path.join(SCRIPT_DIR, "student_emails.txt")
BASE_DIR = "/var/www/student_projects"
DEFAULT_PASSWORD = "password"             # Linux login password (optional, if used)
MYSQL_USER_PASSWORD = "password"          # MySQL password for each student
GROUP = "www-data"

# MySQL credentials for root/admin access
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace with actual MySQL root password
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
        # Check if the user already exists on the Linux system
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

        print(f"Created user: {username}")

        # Log the user in the admin database
        log_user_to_database(username, f"{BASE_DIR}/{username}", DEFAULT_PASSWORD)

        # Create student's MySQL database and remote-access user
        create_student_database(username)
        create_student_mysql_user(username)

    except Exception as e:
        print(f"Error creating user {username}: {e}")

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

        print(f"Logged {username} to database.")
    except Exception as e:
        print(f"Error logging user to database: {e}")

def create_student_database(username):
    db_name = f"student_{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Created database: {db_name}")
    except Exception as e:
        print(f"Error creating database for {username}: {e}")

def create_student_mysql_user(username):
    db_name = f"student_{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create user for remote access
        cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{MYSQL_USER_PASSWORD}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"MySQL user '{username}'@'%' created and granted access to '{db_name}'.")
    except Exception as e:
        print(f"Error creating MySQL user for {username}: {e}")

def main():
    if not os.path.exists(USER_LIST_FILE):
        print(f"Error: '{USER_LIST_FILE}' not found.")
        return

    with open(USER_LIST_FILE, 'r') as file:
        contents = file.read()

        # Support comma or line-separated formats
        if ',' in contents:
            usernames = contents.split(',')
        else:
            usernames = contents.splitlines()

    for username in usernames:
        create_user(username.strip())

if __name__ == "__main__":
    main()
