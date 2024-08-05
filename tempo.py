import csv
import sys
from datetime import datetime

# Function to parse the timestamp string into datetime object
def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

# Function to sort the data based on timestamp
def sort_data(csv_file):
    with open(csv_file, 'r', newline='') as file:  # Open in binary mode to handle \r\n
        reader = csv.reader(file)
        data = [row for row in reader]

    # Sort the data based on the first element (timestamp)
    sorted_data = sorted(data, key=lambda x: parse_timestamp(x[0]))

    return sorted_data

if __name__ == "__main__":
    # Check if CSV file name is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    sorted_data = sort_data(csv_file)

    # Write sorted data back to the CSV file without ^M characters
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in sorted_data:
            # Replace '\r' characters in each row
            row = [col.replace('\r', '') for col in row]
            writer.writerow(row)

    print(f"Sorted data has been written to {csv_file}.")

