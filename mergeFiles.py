import pandas as pd
import glob
import os

def merge_csv_files(folder_path, output_file):
    """
    Merges CSV files in a folder into a single file using the `combine_first` method.

    Args:
        folder_path (str): Path to the folder containing CSV files.
        output_file (str): Path to the output file.
    """
    # Get a list of all CSV files in the folder and sort them based on file name
    csv_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))

    # Initialize an empty DataFrame for the merged data
    merged_df = pd.DataFrame()

    # Iterate through each CSV file
    for csv_file in csv_files:
        # Read the CSV file into a DataFrame
        data_df = pd.read_csv(csv_file)
        
        # Set 'arrivaltime' as the index for easier merging
        data_df.set_index('arrivaltime', inplace=True)
        
        # Merge the current data frame with the merged data frame using combine_first
        # This prioritizes data from the current file (data_df) over the existing merged data
        merged_df = data_df.combine_first(merged_df)
    
    # Reset the index and save the merged DataFrame to the output file
    merged_df.reset_index(inplace=True)
    merged_df.to_csv(output_file, index=False)

if __name__ == '__main__':
    # Specify the folder path and output file path
    import sys
    folder_path = sys.argv[1]  # Get the folder path from command line argument
    output_file = sys.argv[2]  # Get the output file path from command line argument

    # Call the function to merge the CSV files
    merge_csv_files(folder_path, output_file)

    print(f"CSV files merged and saved to: {output_file}")

