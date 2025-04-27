import time
import sys
import psutil
import subprocess
from datetime import datetime
import os

def get_script_name():
    """Retrieve the Python script name from command-line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python monitor.py <script_name.py>")
        sys.exit(1)
    return sys.argv[1]

def get_log_filename(script_name):
    """Generate a log filename based on the script name and current date."""
    date_str = datetime.now().strftime("%d-%m-%y")
    base_name = os.path.splitext(script_name)[0]  # Remove .py extension for nicer log name
    return f"{base_name} {date_str}.log"

def is_script_running(script_name):
    """Check if the Python script is currently running by scanning active processes."""
    for process in psutil.process_iter(['cmdline']):
        try:
            cmdline = process.info['cmdline']
            if cmdline and script_name in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def restart_script(script_name):
    """Attempt to restart the Python script."""
    try:
        subprocess.Popen(["python", script_name])
        return True
    except Exception as e:
        print(f"Failed to restart {script_name}: {e}")
        return False

def log_status(log_file, message):
    """Write a timestamped message to the specified log file."""
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    with open(log_file, "a") as log:
        log.write(f"{timestamp} - {message}\n")

def main():
    """Main function to monitor the Python script and restart if necessary."""
    script_name = get_script_name()
    log_file = get_log_filename(script_name)

    if is_script_running(script_name):
        log_status(log_file, f"Script '{script_name}' is running smoothly.")
    else:
        log_status(log_file, f"Script '{script_name}' is NOT running! Restarting...")
        if restart_script(script_name):
            log_status(log_file, f"'{script_name}' has been restarted.")
        else:
            log_status(log_file, f"Failed to restart '{script_name}'.")

if __name__ == "__main__":
    while True:
        main()  # Run the monitoring once
        time.sleep(60)  # Wait for 60 seconds (1 minute) before checking again
