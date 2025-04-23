import subprocess

def delete_old_logins(report_file):
    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
            old_logins = [line.strip() for line in lines[2:]]  # Skip header lines

        for username in old_logins:
            try:
                subprocess.run(['userdel', '-r', username], check=True)
                print(f"Deleted user {username}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to delete user {username}: {e}")
    except Exception as e:
        print(f"Error reading report file: {e}")

if __name__ == "__main__":
    report_file = 'deletion_report.txt'
    delete_old_logins(report_file)
