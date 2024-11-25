import nmap

def scan_ports(host):
    try:
        nm = nmap.PortScanner()
        print(f"Scanning {host} for the most common 1,000 TCP ports...")

        # Use -Pn to bypass host discovery and scan the most common ports
        nm.scan(host, arguments='-T4 -Pn -F')

        # Check if any hosts were found
        if nm.all_hosts():
            for scanned_host in nm.all_hosts():
                print(f"Host {scanned_host} is up.")
                for proto in nm[scanned_host].all_protocols():
                    print(f"Protocol: {proto}")
                    ports = sorted(nm[scanned_host][proto].keys())  # Sort ports for better readability
                    for port in ports:
                        state = nm[scanned_host][proto][port]['state']
                        print(f"Port {port}: {state}")
        else:
            print(f"Host {host} is down or not reachable.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    host = input("Enter the target IP or hostname: ").strip()
    scan_ports(host)
