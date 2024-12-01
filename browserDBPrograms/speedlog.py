import mysql.connector
import speedtest
import time
import schedule

# Establish database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="redmo",
    password="210681",
    database="monitor",
    charset='utf8mb4',
    collation='utf8mb4_unicode_ci'
)

# Create a cursor object
cursor = db_connection.cursor()

def log_speed():
    try:
        # Fetch building_id dynamically (if needed)
        building_name = "Building A"
        sql_fetch = "SELECT id FROM buildings WHERE name = %s"
        cursor.execute(sql_fetch, (building_name,))
        result = cursor.fetchone()
        
        if result is None:
            print(f"Building '{building_name}' not found.")
            return
        
        building_id = result[0]

        # Initialize speedtest
        print(f"Recording started")
        st = speedtest.Speedtest()
        download_speed = st.download() / 1_000_000  # Mbps
        upload_speed = st.upload() / 1_000_000      # Mbps
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Insert record into database
        sql_insert = """
        INSERT INTO speed_logs (building_id, timestamp, download_speed, upload_speed)
        VALUES (%s, %s, %s, %s)
        """
        values = (building_id, timestamp, download_speed, upload_speed)
        cursor.execute(sql_insert, values)
        db_connection.commit()

        print(f"Record inserted successfully for building '{building_name}':",
              timestamp, download_speed, upload_speed)
    
    except Exception as e:
        print(f"Error: {e}")

# Track the total elapsed time
start_time = time.time()

# Schedule the log_speed function to run every 2 minutes
schedule.every(2).minutes.do(log_speed)

print("Program started. Logging speed every 2 minutes for 10 minutes.")

# Keep the program running for 10 minutes
try:
    while True:
        schedule.run_pending()
        time.sleep(1)  # Prevent CPU overuse

        # Check if 10 minutes have passed
        elapsed_time = time.time() - start_time
        if elapsed_time > 10 * 60:  # 10 minutes in seconds
            print("10 minutes elapsed. Stopping the program.")
            break
except KeyboardInterrupt:
    print("Program stopped manually.")

# Close cursor and database connection when stopping
cursor.close()
db_connection.close()
print("Database connection closed.")
