import time
from datetime import datetime

def get_log_filename():
    """Generate a log filename based on the current date."""
    date_str = datetime.now().strftime("%d-%m-%y")
    return f"loop_monitor_{date_str}.log"

def log_status(log_file, message):
    """Write a timestamped message to the specified log file."""
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    with open(log_file, "a") as log:
        log.write(f"{timestamp} - {message}\n")

def main():
    """Main function to monitor the infinite loop."""
    log_file = get_log_filename()
    cycle_count = 0

    while True:
        log_status(log_file, f"Cycle {cycle_count}: Loop is running.")
        time.sleep(300)  # 5 minutes
        log_status(log_file, f"Cycle {cycle_count}: Pausing for 30 seconds.")
        time.sleep(30)   # 30 seconds pause
        cycle_count += 1

if __name__ == "__main__":
    main()
