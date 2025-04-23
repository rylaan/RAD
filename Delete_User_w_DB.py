import sys
import subprocess
import mysql.connector

# MySQL credentials for root/admin access
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace with actual MySQL root password
    'host': 'localhost',
    'database': 'student_users',
    'unix_socket': '/opt/bitnami/mariadb/tmp/mysql.sock'
}

def delete_old_logins(report_file, deleted_users_report):
    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
        old_logins = [line.strip() for line in lines[2:]]  # Skip header lines

        with open(deleted_users_report, 'w') as report:
            report.write("Deleted Users Report\n")
            report.write("====================\n")

            for username in old_logins:
                try:
                    # Delete the Linux user and their home directory
                    subprocess.run(['userdel', '-r', username], check=True)
                    print(f"Deleted user {username}")
                    report.write(f"Deleted user: {username}\n")

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
    if len(sys.argv) < 3:
        print("Usage: python3 DeleteUsers.py <report_file.txt> <deleted_users_report.txt>")
        sys.exit(1)

    report_file = sys.argv[1]
    deleted_users_report = sys.argv[2]
    delete_old_logins(report_file, deleted_users_report)
    print(f"Deleted users report written to {deleted_users_report}")
