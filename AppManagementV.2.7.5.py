import sys  # Import system module to handle command-line arguments
import psutil  # Import psutil to check running processes
import subprocess  # Import subprocess to restart applications
from datetime import datetime  # Import datetime to manage timestamps


def get_application_name():
    """Retrieve the application name from command-line arguments."""
    if len(sys.argv) < 2:  # Check if the application name is provided as an argument
        print "Usage: python script.py <application_name>"  # Display usage instruction
        sys.exit(1)  # Exit script with an error code
    return sys.argv[1]  # Return the provided application name


def get_log_filename(app_name):
    """Generate a log filename based on the application name and current date."""
    date_str = datetime.now().strftime("%d-%m-%y")  # Get current date in dd-mm-yy format
    return "{} {}.log".format(app_name, date_str)  # Format log filename using .format()


def is_application_running(app_name):
    """Check if the application is currently running by scanning active processes."""
    for process in psutil.process_iter():  # Iterate over running processes
        try:
            if process.name().lower() == app_name.lower():
                # Check if the process name matches the application name (case insensitive)
                return True  # Return True if the application is found running
        except psutil.NoSuchProcess:
            pass  # Ignore processes that no longer exist
    return False  # Return False if the application is not found


def restart_application(app_name):
    """Attempt to restart the application using subprocess."""
    try:
        subprocess.Popen(app_name, shell=True)  # Start the application as a new process
        return True  # Return True if the restart was successful
    except Exception as e:  # Catch any errors during execution
        return False  # Return False if restart failed


def log_status(log_file, message):
    """Write a timestamped message to the specified log file."""
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M")  # Get current timestamp
    with open(log_file, "a") as log:  # Open the log file in append mode
        log.write("{} {}\n".format(message, timestamp))  # Write log entry with timestamp


def main():
    """Main function to check application status and restart if necessary."""
    app_name = get_application_name()  # Retrieve application name from user input
    log_file = get_log_filename(app_name)  # Generate a log filename

    if is_application_running(app_name):  # Check if the application is running
        log_status(log_file, "Application {} is running smoothly".format(app_name))
        # Log that the application is running fine
    else:
        log_status(log_file, "Application {} is not running! Restarting....".format(app_name))
        # Log that the application is down and needs to be restarted

        if restart_application(app_name):  # Attempt to restart the application
            log_status(log_file, "{} has been restarted".format(app_name))
            # Log success if application restarts
        else:
            log_status(log_file, "Failed to restart {}".format(app_name))
            # Log failure if application could not be restarted


# Check if the script is being run as the main program
if __name__ == "__main__":
    main()  # Execute the main function
