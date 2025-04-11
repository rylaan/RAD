import subprocess

def delete_old_logins(report_file):
    try:
        with open(report_file, 'r') as f:
            lines = f.readlines()
            # Skip the first two lines assuming they're headers, then strip newlines and ignore empty lines
            old_logins = [line.strip() for line in lines[2:] if line.strip()]

        for username in old_logins:
            try:
                subprocess.check_call(['userdel', '-r', username])
                print("Deleted user {}".format(username))
            except subprocess.CalledProcessError as e:
                print("Failed to delete user {}: {}".format(username, e))
            except FileNotFoundError:
                print("Command 'userdel' not found. Are you running this on a Unix-like system?")
    except FileNotFoundError:
        print("Error: Report file '{}' not found.".format(report_file))
    except Exception as e:
        print("Error reading report file: {}".format(e))

if __name__ == "__main__":
    report_file = 'deletion_report.txt'
    delete_old_logins(report_file)
