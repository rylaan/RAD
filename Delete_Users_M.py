import sys
import subprocess

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
                    subprocess.run(['userdel', '-r', username], check=True)
                    print(f"Deleted user {username}")
                    report.write(f"Deleted user: {username}\n")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to delete user {username}: {e}")
                    report.write(f"Failed to delete user: {username} - {e}\n")
    except Exception as e:
        print(f"Error reading report file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 DeleteUsers.py <report_file.txt> <deleted_users_report.txt>")
        sys.exit(1)

    report_file = sys.argv[1]
    deleted_users_report = sys.argv[2]
    delete_old_logins(report_file, deleted_users_report)
    print(f"Deleted users report written to {deleted_users_report}")
