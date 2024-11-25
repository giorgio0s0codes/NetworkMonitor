import requests

# Prompt user for the URL
url = input("Enter the target URL: ").strip()

try:
    # Send a GET request
    response = requests.get(url)
    
    # Print the HTTP status code
    print(f"HTTP Response Code: {response.status_code}")
except requests.exceptions.RequestException as e:
    # Handle any request-related errors
    print(f"An error occurred: {e}")
