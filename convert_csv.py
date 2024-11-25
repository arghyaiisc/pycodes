import pandas as pd
from datetime import datetime
import os
import argparse

def format_datetime(date, time):
    """
    Convert the source Date and Time columns to the required datetime format.
    """
    datetime_obj = datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M:%S")
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

def filter_time_range(df, time_col, start_time, end_time):
    """
    Filter rows to include only those within the specified time range.
    """
    # Ensure the time column is a datetime type
    df[time_col] = pd.to_datetime(df[time_col])

    # Extract the time part and filter rows
    df = df[(df[time_col].dt.time >= start_time) & (df[time_col].dt.time <= end_time)]

    return df

def impute_missing_data(df, time_col, freq="1s"):
    """
    Remove duplicates based on the time column, handle missing times, 
    and fill missing values using forward and backward fill.
    """
    # Convert time column to datetime
    df[time_col] = pd.to_datetime(df[time_col])

    # Set time column as the index
    df = df.set_index(time_col)

    # Create a complete time range based on the frequency
    full_time_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq=freq)

    # Reindex to include the full time range
    df = df.reindex(full_time_range)

    # Reset the index and rename it to the time column
    df.index.name = time_col
    df = df.reset_index()

    # Fill missing values using forward fill followed by backward fill
    df = df.ffill().bfill()

    return df

def convert_csv(source_path, target_path):
    """
    Convert all CSV files from the source folder to the target folder.
    """
    converted_files = []
    os.makedirs(target_path, exist_ok=True)

    for file_name in os.listdir(source_path):
        if file_name.endswith(".csv"):
            source_file = os.path.join(source_path, file_name)
            target_file = os.path.join(target_path, file_name)

            # Read the source file
            source_df = pd.read_csv(source_file)

            # Transform the data
            target_df = pd.DataFrame({
                "arrivaltime": source_df.apply(lambda row: format_datetime(row["Date"], row["Time"]), axis=1),
                "sectoken": source_df["Ticker"],
                "lasttrprc": source_df["LTP"]
            })

            # Remove duplicates and handle missing data
            target_df = target_df.drop_duplicates(subset="arrivaltime")

            # Filter rows within 09:15:00 to 15:00:00
            target_df = filter_time_range(target_df, "arrivaltime", 
                                          start_time=datetime.strptime("09:15:00", "%H:%M:%S").time(), 
                                          end_time=datetime.strptime("15:00:00", "%H:%M:%S").time())

            # Handle missing data
            target_df = impute_missing_data(target_df, "arrivaltime")

            # Save the transformed file to the target folder
            target_df.to_csv(target_file, index=False, quotechar='"')
            print(f"Converted: {source_file} -> {target_file}")
            converted_files.append((target_file, file_name))

    return converted_files

def split_csv(input_file, output_dir, param1, param2):
    """
    Split a single CSV file into smaller files.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Iterate through the data and split into multiple files
    start_index = 0
    while start_index < len(df):
        end_index = min(start_index + param1, len(df))
        
        # Write data to a new file
        output_file = os.path.join(output_dir, f'data_{start_index+1}-{end_index}.csv')
        df[start_index:end_index].to_csv(output_file, index=False, quotechar='"')
        
        print(f"Created: {output_file}")
        start_index += param2

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert and split CSV files.')
    parser.add_argument('source_folder', type=str, help='Path to the source folder containing CSV files')
    parser.add_argument('target_folder', type=str, help='Path to the target folder for converted files')
    parser.add_argument('param1', type=int, help='Number of rows per split file')
    parser.add_argument('param2', type=int, help='Step to move forward between splits')

    args = parser.parse_args()

    # Convert CSV files
    converted_files = convert_csv(args.source_folder, args.target_folder)

    # Split the converted files
    for converted_file, original_name in converted_files:
        # Create a subfolder for each original file
        subfolder_name = os.path.splitext(original_name)[0]
        split_output_dir = os.path.join(args.target_folder, subfolder_name)

        # Split the converted file
        split_csv(converted_file, split_output_dir, args.param1, args.param2)

    print("Conversion and splitting completed!")
