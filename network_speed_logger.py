import speedtest
import csv
import time
import schedule
import os

# CSV file path
csv_file = 'network_speed.csv'

# Create the CSV file and write the header if it doesn't exist
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'download_speed', 'upload_speed'])

def log_speed():
    try:
        # Initialize speedtest
        st = speedtest.Speedtest()
        
        # Perform download and upload tests
        download_speed = st.download() / 1_000_000  # Convert from bps to Mbps
        upload_speed = st.upload() / 1_000_000      # Convert from bps to Mbps
        
        # Get the current timestamp
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Append the results to the CSV file
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, download_speed, upload_speed])
        
        print(f"{timestamp} | Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps")
        
    except Exception as e:
        print(f"Error: {e}")

# Schedule the speed test (every # minutes, for example)
schedule.every(1).minutes.do(log_speed)

print("Starting network speed logging to CSV...")
while True:
    schedule.run_pending()
    time.sleep(1)
