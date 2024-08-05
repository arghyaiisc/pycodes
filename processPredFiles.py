import pandas as pd
import sys

# Read the CSV file path from the command line argument
file_path = sys.argv[1]

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)


# Sort the DataFrame by the arrivaltime column in descending order
df_sorted = df.sort_values(by='arrivaltime', ascending=False)

# Drop duplicates based on the arrivaltime column, keeping the first occurrence
df_no_duplicates = df_sorted.drop_duplicates(subset='arrivaltime', keep='first')

# Reverse the DataFrame to restore the original order
df_final = df_no_duplicates[::-1]

# Save the final DataFrame to a CSV file
output_file_path = file_path.replace('.csv', '_filtered.csv')
df_final.to_csv(output_file_path, index=False)

