import sys
import psutil
import time
import subprocess
import socket
from datetime import datetime

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


def generate_cpu_load(duration=60):
    """Generate CPU load by performing intensive calculations."""
    end_time = time.time() + duration
    while time.time() < end_time:
        [x**2 for x in range(100000)]  # Increased range
        for _ in range(100):  # Added nested loop
            [x**3 for x in range(10000)]  # More complex calculations

def write_report(report_file):
    """Write system report to the file."""
    try:
        with open(report_file, "w") as f:
            f.write("System Report - {}\n".format(datetime.now()))
            
            # Generate CPU load for 60 seconds
            print(psutil.cpu_percent(interval=60))
            generate_cpu_load(duration=60)
            print(psutil.cpu_percent(interval=60))
            # Increase the interval to 15 seconds for CPU utilization measurement
            cpu_utilization = psutil.cpu_percent(interval=15)
            print("CPU Utilization: {}%".format(cpu_utilization))  # Debugging print statement
            f.write("\nCPU Utilization: {}%\n".format(cpu_utilization))
            f.write("^average CPU usage percentage over a 15-second interval\n")
            try:
                load_avg = psutil.getloadavg()[0]
                print("User Load Average: {}".format(load_avg))  # Debugging print statement
                f.write("\nUser Load Average: {}\n".format(load_avg))
                f.write("^average number of processes waiting to be executed over the last 5 minutes\n")
            except AttributeError:
                print("Load average not supported on this system.")
                f.write("User Load Average: Not supported\n")
            disk_usage = psutil.disk_usage('/').percent
            print("Disk Space Consumed: {}%".format(disk_usage))  # Debugging print statement
            f.write("\nDisk Space Consumed: {}%\n".format(disk_usage))
            f.write("^percentage of disk space currently in use\n")
            # Test response time
            server_ip = get_ip_address()
            average_time = test_response_time(server_ip)
            if average_time is not None:
                f.write("\nServer Response Time: {:.2f} seconds\n".format(average_time))
                f.write("^average time taken for the server to respond to a ping request\n")
            else:
                f.write("Server is unreachable\n")
    except IOError:
        print("Error: Cannot write to file '{}'.format(report_file)")
        sys.exit(1)
    except Exception as e:
        print("Unexpected error:", e)
        sys.exit(1)

def log_login_attempts(report_file):
    """Log root login attempts from /var/log/wtmp."""
    try:
        process = subprocess.Popen(["last", "adminuser", "-n", "5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    # Generate the report filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_file = f"system_report_{timestamp}.txt"
    
    write_report(report_file)
    log_login_attempts(report_file)
    print("Report written to {}".format(report_file))
