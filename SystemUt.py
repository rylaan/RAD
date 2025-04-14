#Should be ran in cron, the following line will run it everyday at 12pm: 
#crontab -e => 0 12 *** SystemUtilizationV2.7.5.py

import sys
import psutil
import time
import subprocess
import socket
from datetime import datetime

# Log file location
WTMP_FILE = "/var/log/wtmp"

def get_filenames():
    """Get the report filename from command-line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <report_file.txt>")
        sys.exit(1)
    return sys.argv[1]

def get_ip_address():
    """Get the system's IP address."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "Unknown"

def test_response_time(server_ip):
    """Ping the server and measure response time."""
    response_times = []
    ping_cmd = ["ping", "-c", "3", server_ip]

    try:
        for _ in range(3):  # Measure 3 response times
            start_time = time.time()
            process = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
            response_times.append(time.time() - start_time)
            time.sleep(1)

        if response_times:
            return sum(response_times) / len(response_times)
    except Exception as e:
        print("Unexpected error during ping:", e)

    return None  # Server unreachable

def write_report(report_file):
    """Write system report to the file."""
    try:
        with open(report_file, "w") as f:
            f.write("System Report - {}\n".format(datetime.now()))
            
            cpu_utilization = psutil.cpu_percent(interval=10)
            f.write("CPU Utilization: {}%\n".format(cpu_utilization))

            if hasattr(psutil, "getloadavg"):
                max_user_load = psutil.getloadavg()[1]
                f.write("Max User Load: {}\n".format(max_user_load))

            disk_usage = psutil.disk_usage('/').percent
            f.write("Disk Space Consumed: {}%\n".format(disk_usage))

            # Test response time
            server_ip = get_ip_address()
            average_time = test_response_time(server_ip)
            if average_time is not None:
                f.write("Average Response Time: {:.2f} seconds\n".format(average_time))
            else:
                f.write("Server is unreachable\n")
    except IOError:
        print("Error: Cannot write to file '{}'.".format(report_file))
        sys.exit(1)
    except Exception as e:
        print("Unexpected error:", e)
        sys.exit(1)

def log_login_attempts(report_file):
    """Log root login attempts from /var/log/wtmp."""
    try:
        process = subprocess.Popen(["last", "root"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            with open(report_file, "a") as f:
                f.write("\nRoot Login Attempts:\n")
                f.write(output.decode())
        else:
            print("Error reading wtmp file:", error.decode())
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    report_file = get_filenames()
    write_report(report_file)
    log_login_attempts(report_file)
    print("Report written to {}".format(report_file))
