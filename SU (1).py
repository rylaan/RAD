import sys
import psutil
import time
import subprocess
import socket
from datetime import datetime

def get_ip_address():
    #Retrieves server's IP address
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "Unknown"

def test_response_time(server_ip):
    #Pings server and measures response time
    response_times = []
    ping_cmd = ["ping", "-c", "3", server_ip]
    try:
        for _ in range(3):  # Measures 3 response times
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

def create_report(report_file):
    try:
        with open(report_file, "w") as f:
            f.write("System Report - {}\n".format(datetime.now()))
            
            cpu_utilization = psutil.cpu_percent(interval=10)
            f.write("\nCPU Utilization: {}%\n".format(cpu_utilization))
            f.write("^average CPU usage percentage over a 15-second interval\n")
            
            load_avg = psutil.getloadavg()[0]
            f.write("\nUser Load Average: {}\n".format(load_avg))
            f.write("^average number of processes waiting for/using the CPU over the last minutes\n")
            
            disk_usage = psutil.disk_usage('/').percent
            f.write("\nDisk Space Consumed: {}%\n".format(disk_usage))
            f.write("^percentage of disk space currently in use\n")
            
            #Tests response time
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
    #Logs root login attempts
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
    # Generates time-stamped filename for report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_file = f"system_report_{timestamp}.txt"
    
    create_report(report_file)
    log_login_attempts(report_file)
    print("Report written to {}".format(report_file))
