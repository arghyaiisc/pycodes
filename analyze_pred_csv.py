import sys
import pandas as pd
from datetime import datetime
import os

class StockAnalyzer:
    def __init__(self, input_folder, output_folder,expected_swing):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.expected_swing = expected_swing

        self.average_percentage = 0.0
        self.successful_conditions = 0
        self.swing_successful_conditions = 0

        # Add counters for the report
        self.no_swing_opportunities = 0
        self.with_swing_opportunities = 0
        self.swing_100_success = 0
        self.swing_50_70_success = 0
        self.swing_70_100_success = 0
        self.swing_below_50_success = 0

        # Process each file pair
        self.process_files()
        self.generate_report()
    
    def generate_report(self):
        # Generate final report
        print("\n*************** Report ***************")
        print(f"Files with No Swing Opportunities: {self.no_swing_opportunities}")
        print(f"Files with Swing Opportunities: {self.with_swing_opportunities}")
        print(f"Files with 100% Swing Success Percentage: {self.swing_100_success}")
        print(f"Files with 50%-70% Swing Success Percentage: {self.swing_50_70_success}")
        print(f"Files with 70%-100% Swing Success Percentage: {self.swing_70_100_success}")
        print(f"Files with Below 50% Swing Success Percentage: {self.swing_below_50_success}")    

    def process_files(self):
        # List all files in the input folder
        input_files = sorted(os.listdir(self.input_folder))
        output_files = sorted(os.listdir(self.output_folder))

        if len(input_files) != len(output_files):
            print("Warning: Number of files in input and output folders do not match.")
        
        for input_file, output_file in zip(input_files, output_files):
            input_path = os.path.join(self.input_folder, input_file)
            output_path = os.path.join(self.output_folder, output_file)

            print(f"\n*******************  Processing files: {input_file} and {output_file}  *******************\n")
            
            # Load and process the corresponding files
            self.csv_file1 = input_path
            self.csv_file2 = output_path
            
            self.successful_conditions = 0
            self.swing_successful_conditions = 0
            self.average_percentage = 0.0
            self.load_data()
            self.get_opportunities()

    def load_data(self):
        # Load the first CSV data into a DataFrame
        self.df1 = pd.read_csv(self.csv_file1)
        self.df1['arrivaltime'] = pd.to_datetime(self.df1['arrivaltime'], format='%H:%M:%S')

        # Load the second CSV data into another DataFrame
        self.df2 = pd.read_csv(self.csv_file2)
        self.df2['arrivaltime'] = pd.to_datetime(self.df2['arrivaltime'], format='%H:%M:%S')

    def get_opportunities(self):
        # Your existing code for processing `df1` and `df2`
        unique_file_seq_nums = self.df2['fileSeqNum'].dropna().unique().tolist()
        oppcount = 0
        for file_seq_num in unique_file_seq_nums:
            sequence_entries = self.df2[self.df2['fileSeqNum'] == file_seq_num]
            if not sequence_entries.empty:
                start_time = sequence_entries['arrivaltime'].min()
                end_time = sequence_entries['arrivaltime'].max()
                filtered_df1 = self.df1[
                    (self.df1['arrivaltime'] >= start_time) & 
                    (self.df1['arrivaltime'] <= end_time)
                ]
                filtered_df2 = sequence_entries
                start_value = filtered_df2['lastpredtrprc'].iloc[0]
                filtered_df3 = filtered_df2.copy()
                filtered_df3['swing'] = filtered_df2['lastpredtrprc'] - start_value
                merged_df = pd.merge(
                    filtered_df1[['arrivaltime', 'lasttrprc']], 
                    filtered_df2[['arrivaltime', 'lastpredtrprc', 'StanDev']], 
                    on='arrivaltime'
                )
                merged_df['upper_bound'] = merged_df['lastpredtrprc'] + 1.5 * merged_df['StanDev']
                merged_df['lower_bound'] = merged_df['lastpredtrprc'] - 1.5 * merged_df['StanDev']
                merged_df['within_range'] = (merged_df['lasttrprc'] >= merged_df['lower_bound']) & \
                                            (merged_df['lasttrprc'] <= merged_df['upper_bound'])
                percentage_within_range = merged_df['within_range'].mean() * 100
                self.average_percentage += percentage_within_range
                #print(f" percentage_within_range {percentage_within_range}")

                if filtered_df2['lastpredtrprc'].iloc[-1] > filtered_df2['lastpredtrprc'].iloc[0]:
                    max_predicted = filtered_df2['lastpredtrprc'].max()
                    max_actual = filtered_df1['lasttrprc'].max()
                    self.successful_conditions += max_actual >= max_predicted
                else:
                    min_predicted = filtered_df2['lastpredtrprc'].min()
                    min_actual = filtered_df1['lasttrprc'].min()
                    self.successful_conditions += min_actual <= min_predicted

                max_possible_swing = filtered_df3['swing'].abs().max()
                
                swing_points = filtered_df3[
                    (filtered_df3['swing'] >= self.expected_swing) | (filtered_df3['swing'] <= -self.expected_swing)
                ]

                if not swing_points.empty:
                    oppcount += 1
                    print(
                        f"Swing detected at file sequence: {file_seq_num}\n"
                        f"Maximum possible swing: {int(max_possible_swing)}"
                    )

                    if filtered_df2['lastpredtrprc'].iloc[-1] > filtered_df2['lastpredtrprc'].iloc[0]:
                        max_predicted_swing = filtered_df2['lastpredtrprc'].max()
                        max_actual_swing = filtered_df1['lasttrprc'].max()
                        stop_loss = filtered_df2['lastpredtrprc'].iloc[0] - self.expected_swing

                        # Check if actual swing hit stop loss before satisfying the success condition
                        hit_stop_loss = any(filtered_df1['lasttrprc'] <= stop_loss)
                        
                        if hit_stop_loss:
                            print(f"  !! NEGATIVE trade due to stop loss hit !!  ")
                        elif not (max_actual_swing >= max_predicted_swing):
                            print(f"  !! NEGATIVE trade - could not meet target!!  ")
                        else:
                            self.swing_successful_conditions += max_actual_swing >= max_predicted_swing
                           
                    else:
                        min_predicted_swing = filtered_df2['lastpredtrprc'].min()
                        min_actual_swing = filtered_df1['lasttrprc'].min()
                        stop_loss = filtered_df2['lastpredtrprc'].iloc[0] + self.expected_swing

                        # Check if actual swing hit stop loss before satisfying the success condition
                        hit_stop_loss = any(filtered_df1['lasttrprc'] >= stop_loss)

                        if hit_stop_loss:
                            print(f"  !! NEGATIVE trade due to stop loss hit !!  ")
                        elif not (min_actual_swing <= min_predicted_swing):
                            print(f"  !! NEGATIVE trade - could not meet target!!  ")
                        else:
                            self.swing_successful_conditions += min_actual_swing <= min_predicted_swing

                    


        print(f"Expected Swing: {self.expected_swing}")
        print(f"Total opportunities: {oppcount}")
        within_sd = self.average_percentage / len(unique_file_seq_nums)
        print(f"Average percentage within SD range: {within_sd:.2f}%")
        success_percentage = (self.successful_conditions / len(unique_file_seq_nums)) * 100
        print(f"Prediction success percentage: {success_percentage:.2f}%")

        if oppcount == 0:
            swing_success_percentage = 0
            self.no_swing_opportunities += 1
            print("No swing opportunity.")
        else:
            swing_success_percentage = (self.swing_successful_conditions / oppcount) * 100
            print(f"Swing success percentage: {swing_success_percentage:.2f}%")
            self.with_swing_opportunities += 1
            if swing_success_percentage == 100:
                self.swing_100_success += 1
            elif 50 <= swing_success_percentage < 70:
                self.swing_50_70_success += 1
            elif 70 <= swing_success_percentage < 100:
                self.swing_70_100_success += 1
            else:
                self.swing_below_50_success += 1


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python script.py <csv_file1_path> <csv_file2_path> <expected swing>")
        sys.exit(1)

    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]
    expected_swing = float(sys.argv[3])

    # Instantiate and run the processor
    processor = StockAnalyzer(input_folder_path, output_folder_path, expected_swing)
