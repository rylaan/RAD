import os
import subprocess
import sys
import pwd
import getpass
from datetime import datetime

# Function to check if the script is being run as root
def check_root():
    if os.geteuid() != 0:  # Check the effective user ID; root has an ID of 0
        print "Script must be run as root."  # Inform the user if not running as root
        sys.exit(1)  # Exit the script with an error code

# Function to retrieve the CSV filename from command-line arguments
def get_filenames():
    if len(sys.argv) < 2:  # Check if a filename argument is provided
        print "Usage: sudo python script.py <username.csv>"  # Print usage instruction
        sys.exit(1)  # Exit script due to missing argument
    return sys.argv[1]  # Return the provided filename

# Function to read usernames from the specified CSV file
def read_usernames(filename):
    try:
        with open(filename, "r") as f:  # Open the file in read mode
            return f.read().strip().split(",")  # Read content, remove extra spaces, and split into a list
    except IOError:  # Handle file not found or read errors
        print "Error: File '{}' not found.".format(filename)  # Print error message
        sys.exit(1)  # Exit script

# Function to check if a user already exists on the system
def user_exists(username):
    try:
        pwd.getpwnam(username)  # Attempt to fetch user details
        return True  # User exists
    except KeyError:  # Exception occurs if user is not found
        return False  # User does not exist

# Function to run shell commands safely
def run_command(cmd):
    try:
        subprocess.check_call(cmd, shell=True)  # Execute the command
    except subprocess.CalledProcessError:  # Handle errors in command execution
        return False  # Command execution failed
    return True  # Command executed successfully

# Function to create or update a user account
def create_or_update_user(username, default_password, log_file):
    home_dir = "/home/{}".format(username)  # Define the user's home directory path
    timestamp = datetime.now().strftime("%m-%d-%y %I:%M%p").lower()  # Get the current timestamp

    if user_exists(username):  # Check if user already exists
        log_entry = "Failed {}\n".format(username)  # Log failure if user already exists
    else:
        # Commands to create a new user and set up their environment
        commands = [
            "useradd -m -s /bin/bash {}".format(username),  # Create a new user with a home directory
            "echo '{}:{}' | chpasswd".format(username, default_password),  # Set user password
            "mkdir -p {}/public_html".format(home_dir),  # Create the public_html directory
            "chmod 755 {}/public_html".format(home_dir),  # Set permissions for public_html
            "chmod 755 {}".format(home_dir),  # Set permissions for home directory
            "chown {}:{} {}".format(username, username, home_dir),  # Set ownership of home directory
            "chown {}:{} {}/public_html".format(username, username, home_dir),  # Set ownership of public_html
            "cp /home/dlash/public_html/helloworld1.html {}/public_html/helloworld.html".format(home_dir),  # Copy default HTML file
            "chmod 644 {}/public_html/helloworld.html".format(home_dir),  # Set permissions for the HTML file
            "chown {}:{} {}/public_html/helloworld.html".format(username, username, home_dir)  # Set ownership of the HTML file
        ]

        # Execute all commands and check if they succeed
        success = all(run_command(cmd) for cmd in commands)
        if success:
            log_entry = "Created {} on {} pass:{} user:{}\n".format(username, timestamp, default_password, username)  # Log success
        else:
            log_entry = "Failed {}\n".format(username)  # Log failure

    # Append the log entry to the log file
    with open(log_file, "a") as log:
        log.write(log_entry)

# Main function to control the script execution
def main():
    check_root()  # Ensure the script is run as root
    input_file = get_filenames()  # Get the input filename from arguments
    usernames = read_usernames(input_file)  # Read usernames from the file

    # Get default password from environment variable or prompt the user
    default_password = os.environ.get("DEFAULT_PASSWORD", None)
    if not default_password:  # If not set, prompt the user for a password
        default_password = getpass.getpass("Enter default password: ")

    # Generate a log filename with a timestamp
    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    log_filepath = os.path.join(os.getcwd(), log_filename)  # Define full log file path

    # Process each username from the CSV file
    for username in usernames:
        if username.strip():  # Ensure the username is not empty
            create_or_update_user(username.strip(), default_password, log_filepath)

    print "Script execution complete. Log saved to {}".format(log_filepath)  # Inform user of completion

# Entry point of the script
if __name__ == "__main__":
    main()  # Run the main function
