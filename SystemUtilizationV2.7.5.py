import sys
import psutil
import time
import subprocess
import socket
from datetime import datetime

# Log file location
LOG_FILE = "/var/log/secure"


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
    ping_cmd = ["ping", "-c", "3", server_ip] if sys.platform != "win32" else ["ping", "-n", "3", server_ip]

    try:
        process = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode == 0:
            for _ in range(3):  # Measure 3 response times
                start_time = time.time()
                process = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate()
                response_times.append(time.time() - start_time)
                time.sleep(1)

        if response_times:
            return sum(response_times) / len(response_times)
    except Exception as e:
        print(f"Unexpected error during ping: {e}")

    return None  # Server unreachable


def write_report(report_file):
    """Write system report to the file."""
    try:
        with open(report_file, "w") as f:
            f.write(f"System Report - {datetime.now()}\n")
            f.write(f"CPU Utilization: {psutil.cpu_percent(interval=1)}%\n")

            # getloadavg() is only available on Unix-based systems
            if hasattr(psutil, "getloadavg"):
                f.write(f"Max User Load: {psutil.getloadavg()[0]}\n")

            f.write(f"Disk Space Consumed: {psutil.disk_usage('/').percent}%\n")

            # Test response time
            server_ip = get_ip_address()
            average_time = test_response_time(server_ip)
            f.write(
                f"Average Response Time: {average_time:.2f} seconds\n" if average_time else "Server is unreachable\n")
    except IOError:
        print(f"Error: Cannot write to file '{report_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def log_login_attempts(report_file):
    """Log root login attempts from /var/log/secure."""
    try:
        with open(LOG_FILE, "r") as file, open(report_file, "a") as f:
            f.write("\nRoot Login Attempts:\n")
            for line in file:
                if "root" in line:
                    f.write(line)
    except IOError:
        print(f"Error: Cannot read log file '{LOG_FILE}'.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    report_file = get_filenames()
    write_report(report_file)
    log_login_attempts(report_file)
    print(f"Report written to {report_file}")