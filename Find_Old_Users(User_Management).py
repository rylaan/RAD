import os
import pwd
import datetime
import sys

# List of logins to exclude from deletion
EXCLUDE_LOGINS = ['admin', 'special_user', 'varnish', 'mysql']

def get_old_logins():
    current_time = datetime.datetime.now()
    threshold_date = current_time - datetime.timedelta(days=5*365)  # 5 years ago
    old_logins = []
    for user in pwd.getpwall():
        if user.pw_uid >= 1000 and 'home' in user.pw_dir:  # Skip system users
            if user.pw_name in EXCLUDE_LOGINS:
                continue
            try:
                modification_date = datetime.datetime.fromtimestamp(os.path.getmtime(user.pw_dir))
                if modification_date < threshold_date:
                    old_logins.append((user.pw_name, modification_date))
            except Exception as e:
                print(f"Error processing user {user.pw_name}: {e}")
    return old_logins

def generate_report():
    report_file = "old_users.txt"
    old_logins = get_old_logins()
    with open(report_file, 'w') as f:
        f.write("Accounts Recommended for Deletion:\n")
        f.write("=================================\n")
        if old_logins:
            for username, modification_date in old_logins:
                f.write(f"{username} (Last modified: {modification_date.strftime('%Y-%m-%d')})\n")
        else:
            f.write("No old user accounts found.\n")
    print(f"Report written to {report_file}")

if __name__ == "__main__":
    generate_report()
