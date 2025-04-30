# === IMPORTS ===
import os
import subprocess
import mysql.connector
from datetime import datetime

# === CONFIGURATION ===
# Define paths and default values
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Path to the script's directory
USER_LIST_FILE = os.path.join(SCRIPT_DIR, "student_emails.txt")  # File containing student usernames/emails
BASE_DIR = "/var/www/student_projects"  # Base directory for student project folders
DEFAULT_PASSWORD = "password"  # Default Linux login password for students
MYSQL_USER_PASSWORD = "password"  # Default password for each student's MySQL user
GROUP = "www-data"  # Group ownership for web access

# MySQL database connection configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace this with actual secure password
    'host': 'localhost',
    'database': 'student_users',
    'unix_socket': '/opt/bitnami/mariadb/tmp/mysql.sock'
}

# === FUNCTION: Create system and database accounts for each student ===
def create_user(username):
    username = username.strip()

    # Skip invalid or too-short usernames
    if not username or len(username) < 4:
        print(f"Skipping invalid username: {username}")
        return

    try:
        # Check if the user already exists on the system
        result = subprocess.run(['id', username], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            print(f"User {username} already exists. Skipping.")
            return

        # Create a new Linux user with a home directory
        subprocess.run(['sudo', 'useradd', '-m', '-d', f'{BASE_DIR}/{username}', '-s', '/bin/bash', username])
        subprocess.run(['sudo', 'chpasswd'], input=f"{username}:{DEFAULT_PASSWORD}".encode())

        # Create the user's project directory and assign proper permissions
        subprocess.run(['sudo', 'mkdir', '-p', f'{BASE_DIR}/{username}'])
        subprocess.run(['sudo', 'chown', f'{username}:{GROUP}', f'{BASE_DIR}/{username}'])
        subprocess.run(['sudo', 'chmod', '755', f'{BASE_DIR}/{username}'])

        print(f"Created user: {username}")

        # Record the user in the MySQL users database
        log_user_to_database(username, f"{BASE_DIR}/{username}", DEFAULT_PASSWORD)

        # Create a personal MySQL database for the student
        create_student_database(username)

        # Create a MySQL user account and give access to their database
        create_student_mysql_user(username)

    except Exception as e:
        print(f"Error creating user {username}: {e}")

# === FUNCTION: Log the student’s profile to a central MySQL table ===
def log_user_to_database(username, home_dir, password):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert or update user information
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

# === FUNCTION: Create a personal MySQL database for the student ===
def create_student_database(username):
    db_name = f"student_{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create the database if it doesn’t already exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Created database: {db_name}")
    except Exception as e:
        print(f"Error creating database for {username}: {e}")

# === FUNCTION: Create a MySQL user and grant them access to their database ===
def create_student_mysql_user(username):
    db_name = f"student_{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create MySQL user and assign full privileges to their database
        cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{MYSQL_USER_PASSWORD}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'localhost';")
        cursor.execute("FLUSH PRIVILEGES;")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"MySQL user '{username}' created and granted access to '{db_name}'.")

    except Exception as e:
        print(f"Error creating MySQL user for {username}: {e}")

# === MAIN EXECUTION BLOCK ===
def main():
    # Check if the student list file exists
    if not os.path.exists(USER_LIST_FILE):
        print(f"Error: '{USER_LIST_FILE}' not found.")
        return

    with open(USER_LIST_FILE, 'r') as file:
        contents = file.read()

        # Support both comma-separated and newline-separated username lists
        if ',' in contents:
            usernames = contents.split(',')
        else:
            usernames = contents.splitlines()

    # Process each username one by one
    for username in usernames:
        create_user(username.strip())

# === ENTRY POINT ===
if __name__ == "__main__":
    main()
