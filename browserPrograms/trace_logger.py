import csv
import time
import schedule
import subprocess
import socket
import os

# CSV file path
csv_file = 'traceroute_log.csv'
target_host = 'google.com'  # Set the target IP or hostname for traceroute

# Create the CSV file and write the header if it doesn't exist
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'target', 'hop', 'hostname', 'ip_address', 'response_time', 'status'])

def get_hostname(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        return "N/A"  # If the IP address has no associated hostname

def log_traceroute():
    try:
        # Run the traceroute command (use 'tracert' on Windows)
        command = ['traceroute', target_host] if os.name != 'nt' else ['tracert', target_host]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Get the current timestamp
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Parse output and write each hop to CSV
        if process.returncode == 0:
            output = output.decode('utf-8').splitlines()
            for line in output[1:]:  # Skip the first line (header in traceroute)
                parts = line.split()
                
                if os.name != 'nt':  # Linux/macOS format parsing
                    hop = parts[0]
                    ip_address = parts[1] if '(' in parts[1] else 'N/A'
                    response_time = ' '.join(parts[2:]) if len(parts) > 2 else 'N/A'
                else:  # Windows tracert format parsing
                    hop = parts[0]
                    ip_address = parts[-1] if 'ms' not in parts[-1] else parts[-2]
                    response_time = ' '.join(parts[1:-1]) if len(parts) > 1 else 'N/A'
                
                # Resolve the IP address to hostname
                hostname = get_hostname(ip_address.strip('()')) if ip_address != 'N/A' else 'N/A'

                # Append each hop result to the CSV file
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, target_host, hop, hostname, ip_address, response_time, 'Success'])
            
            print(f"{timestamp} | Traceroute to {target_host} completed successfully.")
        
        else:
            raise Exception(error.decode('utf-8').strip())
    
    except Exception as e:
        # Log error if traceroute fails
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, target_host, 'N/A', 'N/A', 'N/A', 'N/A', f"Error: {e}"])
        
        print(f"{timestamp} | Error: {e}")

# Schedule the traceroute (every 10 minutes, for example)
schedule.every(1).minutes.do(log_traceroute)

print("Starting traceroute logging to CSV...")
while True:
    schedule.run_pending()
    time.sleep(1)
