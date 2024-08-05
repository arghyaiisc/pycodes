import os
import pandas as pd
import sys

def process_csv_files(folder_path):
    # Get a list of CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Iterate through each CSV file
    for csv_file in csv_files:
        # Read the CSV file
        df = pd.read_csv(os.path.join(folder_path, csv_file), header=None)

        # Add header to the DataFrame
        df.columns = ['arrivaltime', 'sectoken', 'lasttrprc']

        # Modify the timestamp format
        df['arrivaltime'] = df['arrivaltime'].str.split().str[-1]

        # Save the modified DataFrame back to the CSV file
        df.to_csv(os.path.join(folder_path, csv_file), index=False)

if __name__ == "__main__":
    # Check if the folder path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)
    
    # Get the folder path from the command-line argument
    folder_path = sys.argv[1]
    
    # Process the CSV files in the folder
    process_csv_files(folder_path)

