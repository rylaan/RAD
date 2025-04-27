import time

def endless_loop():
    start_time = time.time()

    while True:
        # Your main loop code would go here
        print("Loop is running...")

        # Check if 5 minutes have passed
        elapsed_time = time.time() - start_time
        if elapsed_time >= 300:  # 300 seconds = 5 minutes
            print("Pausing for 30 seconds...")
            time.sleep(30)       # Pause for 30 seconds
            start_time = time.time()  # Reset timer after pause

        time.sleep(1)  # Short sleep to prevent high CPU usage

if __name__ == "__main__":
    endless_loop()
