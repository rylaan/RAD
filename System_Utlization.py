import sys
import psutil
import time
from datetime import datetime
import subprocess
import socket

# log file location
log_file = '/var/log/secure'

def get_filenames():
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <report_file.txt>")
        sys.exit(1)
    return sys.argv[1]

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def test_response_time(server_ip):
    response_times = []

    for _ in range(10):
        start_time = time.time()
        try:
            response = subprocess.run(['ping', '-c', '1', server_ip], capture_output=True, check=True)
            end_time = time.time()
            response_times.append(end_time - start_time)
        except subprocess.CalledProcessError:
            response_times.append(None)
        except Exception as e:
            print(f"Unexpected error during ping: {e}")
            response_times.append(None)

        time.sleep(1)

    avg_response_time = sum(filter(None, response_times)) / len(filter(None, response_times))
    return avg_response_time

def write_report(report_file):
    try:
        with open(report_file, 'w') as f:
            f.write(f"System Report - {datetime.now()}\n")
            f.write(f"CPU Utilization: {psutil.cpu_percent(interval=1)}%\n")
            f.write(f"Max User Load: {psutil.getloadavg()[0]}\n")
            f.write(f"Disk Space Consumed: {psutil.disk_usage('/').percent}%\n")

            # Test response time
            server_ip = get_ip_address()
            average_time = test_response_time(server_ip)
            if average_time:
                f.write(f"Average Response Time: {average_time:.2f} seconds\n")
            else:
                f.write("Average Response Time: Server is unreachable\n")
    except FileNotFoundError:
        print(f"Error: File '{report_file}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied when trying to write '{report_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def log_login_attempts():
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()

        with open(report_file, 'a') as f:
            f.write("\nRoot Login Attempts:\n")
            for line in lines:
                if "root" in line:
                    f.write(line)
    except PermissionError:
        print(f"Error: Permission denied when trying to read '{log_file}'.")
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    report_file = get_filenames()
    write_report(report_file)
    log_login_attempts()
    print(f"Report written to {report_file}")
