import subprocess
import os
import sys

def delete_old_logins(report_file):
    # Check if the file exists before proceeding
    if not os.path.isfile(report_file):
        print("Error: Report file '{}' not found.".format(report_file))
        sys.exit(1)

    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
            # Skip header lines and strip each username, ignore empty/blank lines
            old_logins = [line.strip() for line in lines[2:] if line.strip()]

        if not old_logins:
            print("No users to delete.")
            return

        for username in old_logins:
            try:
                subprocess.check_call(['userdel', '-r', username])
                print("✅ Deleted user '{}'".format(username))
            except subprocess.CalledProcessError as e:
                print("❌ Failed to delete user '{}': {}".format(username, e))
            except FileNotFoundError:
                print("❌ 'userdel' command not found. Are you running on a Linux/Unix system?")
                break

    except Exception as e:
        print("Unexpected error while reading report file: {}".format(e))

if __name__ == "__main__":
    report_file = 'deletion_report.txt'
    delete_old_logins(report_file)
