import mysql.connector
import subprocess
import re
import time

# Establish database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="redmo",
    password="210681",
    database="monitor",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci"
)

# Create a cursor object
cursor = db_connection.cursor()

# Function to perform traceroute and log the first 3 hops
def log_traceroute(destination="ibero.mx", building_id=1):
    try:
        print(f"Running traceroute to {destination}")
        result = subprocess.run(
            ["traceroute", "-m", "3", destination],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Process the traceroute output
        hops = []
        for line in result.stdout.splitlines():
            match = re.match(r"^\s*(\d+)\s+([\w\.-]+|\*)\s+\(?([\d\.]+|\*)\)?", line)
            if match:
                hop_number, hostname, ip = match.groups()
                hops.append((int(hop_number), hostname, ip))

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # If no hops are found, log the failure
        if not hops:
            sql_insert = """
            INSERT INTO tracer_logs (building_id, target, hop, hostname, ip_address, timestamp, status)
            VALUES (%s, %s, NULL, NULL, NULL, %s, 'Failure')
            """
            cursor.execute(sql_insert, (building_id, destination, timestamp))
            db_connection.commit()
            print(f"Traceroute to {destination} failed. Logged as failure.")
            return

        print(f"Traceroute completed at {timestamp}. Recording the first 3 hops.")

        # Insert the hops into the database
        for hop in hops[:3]:
            hop_number, hostname, ip = hop
            sql_insert = """
            INSERT INTO tracer_logs (building_id, target, hop, hostname, ip_address, timestamp, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Success')
            """
            cursor.execute(sql_insert, (building_id, destination, hop_number, hostname, ip, timestamp))

        db_connection.commit()
        print(f"Recorded {len(hops[:3])} hops successfully.")

    except Exception as e:
        print(f"Error: {e}")

# Run the traceroute function once
log_traceroute()

# Close cursor and database connection
cursor.close()
db_connection.close()
print("Program completed and database connection closed.")
