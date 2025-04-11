import sys
import psutil
import subprocess
from datetime import datetime


def get_application_name():
    """Retrieve the application name from command-line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <application_name>")
        sys.exit(1)
    return sys.argv[1]


def get_log_filename(app_name):
    """Generate a log filename based on the application name and current date."""
    date_str = datetime.now().strftime("%d-%m-%y")
    return "{} {}.log".format(app_name, date_str)


def is_application_running(app_name):
    """Check if the application is currently running by scanning active processes."""
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'] and process.info['name'].lower() == app_name.lower():
                return True
        except psutil.NoSuchProcess:
            pass
    return False


def restart_application(app_name):
    """Attempt to restart the application using subprocess."""
    try:
        subprocess.Popen(app_name, shell=True)
        return True
    except Exception:
        return False


def log_status(log_file, message):
    """Write a timestamped message to the specified log file."""
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M")
    with open(log_file, "a") as log:
        log.write("{} {}\n".format(message, timestamp))


def main():
    """Main function to check application status and restart if necessary."""
    app_name = get_application_name()
    log_file = get_log_filename(app_name)

    if is_application_running(app_name):
        log_status(log_file, "Application {} is running smoothly".format(app_name))
    else:
        log_status(log_file, "Application {} is not running! Restarting....".format(app_name))

        if restart_application(app_name):
            log_status(log_file, "{} has been restarted".format(app_name))
        else:
            log_status(log_file, "Failed to restart {}".format(app_name))


if __name__ == "__main__":
    main()
