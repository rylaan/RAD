import os
import subprocess
import mysql.connector
import datetime

# MySQL credentials for root/admin access
DB_CONFIG = {
    'user': 'root',
    'password': 'Password',  # Replace with actual MySQL root password
    'host': 'localhost',
    'database': 'student_users',
    'unix_socket': '/opt/bitnami/mariadb/tmp/mysql.sock'
}

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
    
    # Create mail spool for the user
    mail_spool = f'/var/mail/{username}'
    subprocess.run(['sudo', 'touch', mail_spool])
    subprocess.run(['sudo', 'chown', f'{username}:mail', mail_spool])
    print(f"Mail spool created for user {username}")
    
    # Create student's MySQL database
    create_student_database(username)
    
    # Create student's MySQL user for remote access
    create_student_mysql_user(username)

def create_database(username):
    db_name = f"{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Created database: {db_name}")
    except Exception as e:
        print(f"Error creating database for {username}: {e}")

def create_mysql_user(username):
    db_name = f"{username}"
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Create user for remote access
        cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY 'password';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"MySQL user '{username}'@'%' created and granted access to '{db_name}'.")
    except Exception as e:
        print(f"Error creating MySQL user for {username}: {e}")

if __name__ == "__main__":
    old_usernames = ['olduser1', 'olduser2', 'olduser3']
    for username in old_usernames:
        create_old_user(username)
