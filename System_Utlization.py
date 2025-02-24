import psutil
import time
from datetime import datetime
import subprocess

# report and log files
report_file = 'system_report.txt'
log_file = '/var/log/auth.log'
server_ip = ''


def test_response_time(server_ip):
    response_times = []

    for _ in range(10):
        start_time = time.time()
        response = subprocess.run(['ping', '-c', '1', server_ip], capture_output=True)
        end_time = time.time()

        if response.returncode == 0:
            response_times.append(end_time - start_time)
        else:
            response_times.append(None)

        time.sleep(1)

    avg_response_time = sum(filter(None, response_times)) / len(filter(None, response_times))
    return avg_response_time


def write_report():
    with open(report_file, 'w') as f:
        f.write(f"System Report - {datetime.now()}\n")
        f.write(f"CPU Utilization: {psutil.cpu_percent(interval=1)}%\n")
        f.write(f"Max User Load: {psutil.getloadavg()[0]}\n")
        f.write(f"Disk Space Consumed: {psutil.disk_usage('/').percent}%\n")

        # Test response time
        average_time = test_response_time(server_ip)
        if average_time:
            f.write(f"Average Response Time: {average_time:.2f} seconds\n")
        else:
            f.write("Average Response Time: Server is unreachable\n")

        f.write(f"Errors: Not available in psutil\n")


def log_login_attempts():
    with open(log_file, 'r') as file:
        lines = file.readlines()

    with open(report_file, 'a') as f:
        f.write("\nRoot Login Attempts:\n")
        for line in lines:
            if "root" in line:
                f.write(line)


if __name__ == "__main__":
    write_report()
    log_login_attempts()
    print(f"Report written to {report_file}")