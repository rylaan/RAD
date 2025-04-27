import time
import sys
import psutil
import subprocess
from datetime import datetime
import shlex


def get_application_name():
    if len(sys.argv) < 2:
        print("Usage: python script.py <application_name>")
        sys.exit(1)
    return sys.argv[1]


def get_log_filename(app_name):
    date_str = datetime.now().strftime("%d-%m-%y")
    return f"{app_name} {date_str}.log"


def is_application_running(app_name):
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'] and app_name.lower() in process.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def restart_application(app_name):
    try:
        command = shlex.split(app_name)
        subprocess.Popen(command)
        return True
    except Exception as e:
        print(f"Failed to restart {app_name}: {e}")
        return False


def log_status(log_file, message):
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M")
    with open(log_file, "a") as log:
        log.write(f"{message} {timestamp}\n")


def main():
    app_name = get_application_name()
    log_file = get_log_filename(app_name)

    while True:
        if is_application_running(app_name):
            log_status(log_file, f"Application '{app_name}' is running smoothly.")
        else:
            log_status(log_file, f"Application '{app_name}' is not running! Restarting...")
            if restart_application(app_name):
                log_status(log_file, f"'{app_name}' has been restarted.")
            else:
                log_status(log_file, f"Failed to restart '{app_name}'.")

        print(f"Sleeping for 2 minutes...\n")
        time.sleep(120)  # Wait for 2 minutes before checking again


if __name__ == "__main__":
    main()
