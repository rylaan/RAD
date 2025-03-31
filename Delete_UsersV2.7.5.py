import subprocess

def delete_old_logins(report_file):
    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
            old_logins = [line.strip() for line in lines[2:]]  # Skip header lines

        for username in old_logins:
            try:
                subprocess.check_call(['userdel', '-r', username])
                print("Deleted user {}".format(username))
            except subprocess.CalledProcessError as e:
                print("Failed to delete user {}: {}".format(username, e))
    except Exception as e:
        print("Error reading report file: {}".format(e))

if __name__ == "__main__":
    report_file = 'deletion_report.txt'
    delete_old_logins(report_file)
