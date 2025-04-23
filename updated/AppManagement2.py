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
    return f"{app_name} {date_str}.log"


def is_application_running(app_name):
    """Check if the application is currently running by scanning active processes."""
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'] and app_name.lower() in process.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def restart_application(app_name):
    """Attempt to restart a command-line application."""
    try:
        # Split the command for subprocess (safer than shell=True)
        command = app_name.split()
        subprocess.Popen(command)
        return True
    except Exception as e:
        print(f"Failed to restart {app_name}: {e}")
        return False


def log_status(log_file, message):
    """Write a timestamped message to the specified log file."""
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M")
    with open(log_file, "a") as log:
        log.write(f"{message} {timestamp}\n")


def main():
    """Main function to check application status and restart if necessary."""
    app_name = get_application_name()
    log_file = get_log_filename(app_name)

    if is_application_running(app_name):
        log_status(log_file, f"Application '{app_name}' is running smoothly.")
    else:
        log_status(log_file, f"Application '{app_name}' is not running! Restarting...")
        if restart_application(app_name):
            log_status(log_file, f"'{app_name}' has been restarted.")
        else:
            log_status(log_file, f"Failed to restart '{app_name}'.")


if __name__ == "__main__":
    main()
