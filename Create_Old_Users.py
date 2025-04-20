import os
import subprocess
import datetime

def create_old_user(username):
    # Create the user
    subprocess.run(['sudo', 'useradd', '-m', username])

    # Set the creation date to 5+ years ago
    creation_date = datetime.datetime.now() - datetime.timedelta(days=5*365)
    creation_timestamp = int(creation_date.timestamp())
    
    # Update the home directory creation time
    home_dir = f'/home/{username}'
    os.utime(home_dir, (creation_timestamp, creation_timestamp))

    print(f"User {username} created with home directory timestamp set to {creation_date}")

if __name__ == "__main__":
    old_usernames = ['olduser1', 'olduser2', 'olduser3']
    for username in old_usernames:
        create_old_user(username)
