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

# Function to create a new user and set up their home and public_html directories
# If the user already exists, it logs the failure. If any command fails, it logs the specific reason.
def create_or_update_user(username, default_password, log_file):
    import subprocess
    home_dir = "/home/{}".format(username)  # Define the path for the user's home directory
    timestamp = datetime.now().strftime("%m-%d-%y %I:%M%p").lower()  # Get current timestamp in a readable format

    # Helper function to write failure logs with the reason
    def log(reason):
        with open(log_file, "a") as logf:
            logf.write("Failed {} on {}: {}\n".format(username, timestamp, reason))

    # Check if the user already exists in the system
    if user_exists(username):
        log("User already exists.")  # Log the reason and return early
        return

    # List of shell commands to execute in order to fully set up the user environment
    # Each entry is a tuple: (command_string, description_of_what_it_does_if_it_fails)
    commands = [
        ("useradd -m -s /bin/bash {}".format(username), "User creation failed"),
        ("echo '{}:{}' | chpasswd".format(username, default_password), "Setting password failed"),
        ("mkdir -p {}/public_html".format(home_dir), "Creating public_html failed"),
        ("chmod 755 {}/public_html".format(home_dir), "Setting permissions for public_html failed"),
        ("chmod 755 {}".format(home_dir), "Setting permissions for home directory failed"),
        ("chown {}:{} {}".format(username, username, home_dir), "Setting ownership of home directory failed"),
        ("chown {}:{} {}/public_html".format(username, username, home_dir), "Setting ownership of public_html failed"),
        ("cp /home/dlash/public_html/helloworld1.html {}/public_html/helloworld.html".format(home_dir), "Copying HTML file failed"),
        ("chmod 644 {}/public_html/helloworld.html".format(home_dir), "Setting permissions on HTML file failed"),
        ("chown {}:{} {}/public_html/helloworld.html".format(username, username, home_dir), "Setting ownership of HTML file failed")
    ]

    # Loop through each command and execute it
    for cmd, err_msg in commands:
        # Run the shell command and capture stdout and stderr
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        # Check the return code to determine if the command was successful
        if proc.returncode != 0:
            # If not, log the error message with the stderr output and stop further processing
            log("{}: {}".format(err_msg, err.strip()))
            return

    # If all commands succeeded, log the successful creation
    with open(log_file, "a") as log:
        log.write("Created {} on {} pass:{} user:{}\n".format(username, timestamp, default_password, username))


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
