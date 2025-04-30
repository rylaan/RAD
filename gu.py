import time

def generate_cpu_load(duration=60):
    """Generate CPU load by performing intensive calculations."""
    end_time = time.time() + duration
    while time.time() < end_time:
        [x**2 for x in range(100000)]  # Increased range
        for _ in range(100):  # Added nested loop
            [x**3 for x in range(10000)]  # More complex calculations

if __name__ == "__main__":
    generate_cpu_load(duration=60)
