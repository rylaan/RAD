import sys
import subprocess
import mysql.connector
import os
import datetime

# MySQL credentials for root/admin access
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace with actual MySQL root password
    'host': 'localhost',
    'database': 'student_users',
    'unix_socket': '/opt/bitnami/mariadb/tmp/mysql.sock'
}

def delete_old_logins():
    report_file = "old_users.txt"
    deleted_users_report = "deleted_users.txt"
    
    if not os.path.exists(report_file):
        print(f"Error: {report_file} does not exist.")
        sys.exit(1)
    
    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
        old_logins = [line.strip().split()[0] for line in lines[2:]]  # Skip header lines and extract usernames
        with open(deleted_users_report, 'w') as report:
            report.write("Deleted Users Report\n")
            report.write("====================\n")
            for username in old_logins:
                try:
                    # Get the modification date of the user's home directory
                    home_dir = f"/home/{username}"
                    if os.path.exists(home_dir):
                        modification_time = os.path.getmtime(home_dir)
                        modification_date = datetime.datetime.fromtimestamp(modification_time)
                        age = (datetime.datetime.now() - modification_date).days
                    else:
                        modification_date = "Unknown"
                        age = "Unknown"

                    # Delete the Linux user and their home directory
                    subprocess.run(['userdel', '-r', username], check=True)
                    print(f"Deleted user {username} (Last modified: {modification_date}, Account age: {age} days)")
                    report.write(f"Deleted user: {username} (Last modified: {modification_date}, Account age: {age} days)\n")

                    # Delete the user's MySQL database
                    delete_student_database(username)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to delete user {username}: {e}")
                    report.write(f"Failed to delete user: {username} - {e}\n")
    except Exception as e:
        print(f"Error reading report file: {e}")

def delete_student_database(username):
    db_name = f"student_{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Deleted database: {db_name}")
    except Exception as e:
        print(f"Error deleting database for {username}: {e}")

if __name__ == "__main__":
    delete_old_logins()
    print("Deleted users report written to deleted_users.txt")
