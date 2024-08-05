import pandas as pd
import os

def split_csv(input_file, output_dir, param1, param2):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Format "arrivaltime" column
    #df['arrivaltime'] = '2024-01-30 ' + df['arrivaltime']
    
    # Iterate through the data and split into multiple files
    start_index = 0
    while start_index < len(df):
        end_index = min(start_index + param1, len(df))
        # Write data to a new file
        output_file = os.path.join(output_dir, f'data_{start_index+1}-{end_index}.csv')
        df[start_index:end_index].to_csv(output_file, index=False)
        # Update start_index for the next iteration
        start_index = start_index + param2

if __name__ == "__main__":
    # Load parameters from config file
    param1 = 900  # Seconds of data to read every time
    param2 = 180   # Frequency in seconds
    input_file = '/home/arghya/project/data/data/3004/30apr0930_to_1530.csv' # CSV file to split
    output_dir = '/home/arghya/project/data/data/3004/RawData_3mins'	     # Output directory

    # Call function to split the CSV file
    split_csv(input_file, output_dir, param1, param2)

