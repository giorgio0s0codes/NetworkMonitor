import csv
import time
import schedule
import subprocess
import socket
import os
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CSV file path
csv_file = 'traceroute_log.csv'
target_host = 'google.com'

# Create the CSV file and write the header if it doesn't exist
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'target', 'hop', 'hostname', 'ip_address', 'response_time', 'status'])

@lru_cache(maxsize=256)  # Cache up to 256 IP-hostname lookups
def get_hostname(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        return "N/A"

def parse_traceroute_line(line, platform):
    try:
        parts = line.split()
        if platform != 'nt':  # Linux/macOS
            hop = parts[0]
            ip_address = parts[1] if '(' in parts[1] else 'N/A'
            response_time = ' '.join(parts[2:]) if len(parts) > 2 else 'N/A'
        else:  # Windows
            hop = parts[0]
            ip_address = parts[-1] if 'ms' not in parts[-1] else parts[-2]
            response_time = ' '.join(parts[1:-1]) if len(parts) > 1 else 'N/A'
        return hop, ip_address.strip('()'), response_time
    except IndexError:
        return 'N/A', 'N/A', 'N/A'

def log_traceroute():
    try:
        command = ['traceroute', target_host] if os.name != 'nt' else ['tracert', target_host]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            output, error = process.communicate(timeout=60)  # Set timeout for safety
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("Traceroute timed out.")

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        if process.returncode == 0:
            output = output.decode('utf-8').splitlines()
            for line in output[1:]:
                hop, ip_address, response_time = parse_traceroute_line(line, os.name)
                hostname = get_hostname(ip_address) if ip_address != 'N/A' else 'N/A'
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, target_host, hop, hostname, ip_address, response_time, 'Success'])
            logging.info(f"Traceroute to {target_host} completed successfully.")
        else:
            raise Exception(error.decode('utf-8').strip())
    except Exception as e:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, target_host, 'N/A', 'N/A', 'N/A', 'N/A', f"Error: {e}"])
        logging.error(f"Traceroute failed: {e}")

schedule.every(3).minutes.do(log_traceroute)

logging.info("Starting traceroute logging to CSV...")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Traceroute logging stopped.")
