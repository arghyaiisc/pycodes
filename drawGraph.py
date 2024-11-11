import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTimeEdit, QLabel, QLineEdit
from PyQt6.QtCore import QTime, QTimer
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import os


class PlotWidget(QWidget):
    def __init__(self, csv_file1, csv_file2):
        super().__init__()

        self.csv_file1 = csv_file1
        self.csv_file2 = csv_file2

        # Flag to track visibility of first CSV data plot
        self.show_csv1_plot = True

        # Flag to track visibility of the legend
        self.show_legend = True
        self.show_SD = True

        # Create a figure and a canvas to display the plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Create the navigation toolbar
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Create the start and end time widgets
        self.start_time_edit = QTimeEdit(self)
        self.start_time_edit.setDisplayFormat('HH:mm:ss')
        # Default start time: 09:00:00
        self.start_time_edit.setTime(QTime(9, 0, 0))
        self.start_time_edit.setFont(QFont('Arial', 14))
        self.start_time_edit.setFixedSize(120, 40)

        self.end_time_edit = QTimeEdit(self)
        self.end_time_edit.setDisplayFormat('HH:mm:ss')
        # Default end time: 16:00:00
        self.end_time_edit.setTime(QTime(16, 0, 0))
        self.end_time_edit.setFont(QFont('Arial', 14))
        self.end_time_edit.setFixedSize(120, 40)

        # Create the plot button
        self.plot_button = QPushButton('Plot', self)
        self.plot_button.setFont(QFont('Arial', 14))
        self.plot_button.setFixedSize(100, 40)
        self.plot_button.clicked.connect(self.plot_graph)

        # Create the get opp button
        self.opp_button = QPushButton('Opp', self)
        self.opp_button.setFont(QFont('Arial', 14))
        self.opp_button.setFixedSize(100, 40)
        self.opp_button.clicked.connect(self.get_opportunities)

        # Create the next button
        self.next_button = QPushButton('Next', self)
        self.next_button.setFont(QFont('Arial', 14))
        self.next_button.setFixedSize(100, 40)
        self.next_button.clicked.connect(self.increment_sequence_number)

        # Create the prev buttonimport os
        self.prev_button = QPushButton('Prev', self)
        self.prev_button.setFont(QFont('Arial', 14))
        self.prev_button.setFixedSize(100, 40)
        self.prev_button.clicked.connect(self.decrement_sequence_number)

        # Create the interval input and advance button
        self.interval_edit = QLineEdit(self)
        self.interval_edit.setPlaceholderText('Interval (s)')
        self.interval_edit.setFont(QFont('Arial', 14))
        self.interval_edit.setFixedSize(120, 40)

        # Create the probability_edit input
        self.probability_edit = QLineEdit(self)
        self.probability_edit.setPlaceholderText('Probability (s)')
        self.probability_edit.setFont(QFont('Arial', 14))
        self.probability_edit.setFixedSize(120, 40)

        # Create the swing_edit input
        self.swing_edit = QLineEdit(self)
        self.swing_edit.setPlaceholderText('Swing (s)')
        self.swing_edit.setFont(QFont('Arial', 14))
        self.swing_edit.setFixedSize(120, 40)

        # Create the sequence_edit input
        self.sequence_edit = QLineEdit(self)
        self.sequence_edit.setPlaceholderText('Sequence (s)')
        self.sequence_edit.setFont(QFont('Arial', 14))
        self.sequence_edit.setFixedSize(120, 40)

        self.advance_button = QPushButton('Advance', self)
        self.advance_button.setFont(QFont('Arial', 14))
        self.advance_button.setFixedSize(100, 40)
        self.advance_button.clicked.connect(self.advance_graph)

        self.back_button = QPushButton('Back', self)
        self.back_button.setFont(QFont('Arial', 14))
        self.back_button.setFixedSize(100, 40)
        self.back_button.clicked.connect(self.back_graph)

        # Create the toggle button for the first CSV data plot
        self.toggle_csv1_button = QPushButton('Hide CSV 1 Plot', self)
        self.toggle_csv1_button.setFont(QFont('Arial', 14))
        self.toggle_csv1_button.setFixedSize(150, 40)
        self.toggle_csv1_button.clicked.connect(self.toggle_csv1_plot)

        # Create the toggle button for the legend
        self.toggle_legend_button = QPushButton('Hide Legend', self)
        self.toggle_legend_button.setFont(QFont('Arial', 14))
        self.toggle_legend_button.setFixedSize(150, 40)
        self.toggle_legend_button.clicked.connect(self.toggle_legend)

        self.toggle_SD_button = QPushButton('Hide SD', self)
        self.toggle_SD_button.setFont(QFont('Arial', 14))
        self.toggle_SD_button.setFixedSize(150, 40)
        self.toggle_SD_button.clicked.connect(self.toggle_SD)

        # Create layout for time edit widgets, plot button, interval edit, and advance button
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_time_edit)
        controls_layout.addWidget(self.end_time_edit)
        controls_layout.addWidget(self.sequence_edit)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.opp_button)
        controls_layout.addWidget(self.interval_edit)
        controls_layout.addWidget(self.probability_edit)
        controls_layout.addWidget(self.swing_edit)
        #controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.advance_button)
        controls_layout.addWidget(self.toggle_csv1_button)
        controls_layout.addWidget(self.toggle_legend_button)
        controls_layout.addWidget(self.toggle_SD_button)

        # Display the CSV file name
        file_label = QLabel(f"CSV File 2: {self.csv_file2}")
        file_label.setMaximumHeight(20)

        # Create the main layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(file_label)
        probability = float(self.probability_edit.text() or 0.7)
        swing_value = int(self.swing_edit.text() or 100)
        file_seq_num = int(self.sequence_edit.text() or 1)
        layout.addWidget(self.canvas)
        layout.addLayout(controls_layout)

        # Set the main layout
        self.setLayout(layout)

        # Load the data and initialize the plot
        self.load_data()
        self.plot_graph()

        # Connect the scroll event to the on_scroll method
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

    def load_data(self):
        # Load the first CSV data into a DataFrame
        self.df1 = pd.read_csv(self.csv_file1)
        self.df1['arrivaltime'] = pd.to_datetime(self.df1['arrivaltime'], format='%H:%M:%S')

        # Load the second CSV data into another DataFrame
        self.df2 = pd.read_csv(self.csv_file2)
        self.df2['arrivaltime'] = pd.to_datetime(self.df2['arrivaltime'], format='%H:%M:%S')
    

    def plot_graph(self,file_seq_num=None):
        # Get start and end times from the time edit widgets
        start_time = self.start_time_edit.time().toString('HH:mm:ss')
        end_time = self.end_time_edit.time().toString('HH:mm:ss')

        # Filter the data based on the specified time range
        filtered_df1 = self.df1[
            (self.df1['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
            (self.df1['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
        ]

        # filtered_df2 = self.df2[
        #     (self.df2['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
        #     (self.df2['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
        # ]

        unique_file_seq_nums = self.df2['fileSeqNum'].dropna().unique().tolist()

        #file_seq_num = 10
        # If file_seq_num is not provided, get it from the edit box
        file_seq_num = int(self.sequence_edit.text() or unique_file_seq_nums[0])
        print(f"start_time {start_time}")
        print(f"file_seq_num {file_seq_num}")
        # Ensure the arrivaltime is a datetime object
        # Find the entries for the specified file sequence number
        sequence_entries = self.df2[self.df2['fileSeqNum'] == file_seq_num]

        

        # Check if any entries exist for the given sequence number
        if not sequence_entries.empty:
            # Get the start_time (1st entry) and end_time (last entry) for the specified fileSeqNum
            start_time = sequence_entries['arrivaltime'].min()  # First entry
            end_time = sequence_entries['arrivaltime'].max()    # Last entry

            # Update the start and end time edit widgets
            self.start_time_edit.setTime(start_time.time())
            self.end_time_edit.setTime(end_time.time())

            filtered_df1 = self.df1[
                (self.df1['arrivaltime'] >= start_time) & 
                (self.df1['arrivaltime'] <= end_time)
            ]

            filtered_df2 = sequence_entries  # Use only data from the provided sequence number
            
            # Clear the existing plot
            self.figure.clear()

            # Create a new plot
            ax = self.figure.add_subplot(111)

            # Filter the DataFrame based on start_time and end_time
            # filtered_df2 = self.df2[
            #     (self.df2['arrivaltime'] >= start_time) & 
            #     (self.df2['arrivaltime'] <= end_time)
            # ]

        # Calculate Bollinger Bands for filtered_df1['lasttrprc']
        # window = 20
        # multiplier = 2

        # filtered_df1['SMA'] = filtered_df1['lasttrprc'].rolling(window=window).mean()
        # filtered_df1['STD'] = filtered_df1['lasttrprc'].rolling(window=window).std()
        # filtered_df1['Upper Band'] = filtered_df1['SMA'] + (multiplier * filtered_df1['STD'])
        # filtered_df1['Lower Band'] = filtered_df1['SMA'] - (multiplier * filtered_df1['STD'])

        #  # Calculate RSI for filtered_df1['lasttrprc']
        # delta = filtered_df1['lasttrprc'].diff()
        # gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        # loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        # RS = gain / loss
        # filtered_df1['RSI'] = 100 - (100 / (1 + RS))

        # Clear the existing plot
        self.figure.clear()

        # Create a new plot
        ax = self.figure.add_subplot(111)

        # Plot the first CSV data if the flag is set to True
        if self.show_csv1_plot:
            ax.plot(filtered_df1['arrivaltime'], filtered_df1['lasttrprc'],
                    label='Last Trade Price (CSV 1)', marker='o', color='blue')

            # Calculate the mean of the 'lasttrprc' column in the filtered DataFrame
            # mean_lasttrprc = filtered_df1['lasttrprc'].mean()
            # std_lasttrprc = filtered_df1['lasttrprc'].std()
            # meanSDH = mean_lasttrprc + 2*std_lasttrprc
            # meanSDL = mean_lasttrprc - 2*std_lasttrprc
            # # Plot the mean line for 'lasttrprc'
            # ax.axhline(meanSDH, color='red', linestyle='--', label=f'Mean Last Trade Price: {meanSDH:.2f}')
            # ax.axhline(meanSDL, color='yellow', linestyle='--', label=f'Mean Last Trade Price: {meanSDL:.2f}')

             # Plot Bollinger Bands
            # ax.plot(filtered_df1['arrivaltime'], filtered_df1['Upper Band'],
            #         label='Upper Bollinger Band', color='red', linestyle='--')
            # ax.plot(filtered_df1['arrivaltime'], filtered_df1['Lower Band'],
            #         label='Lower Bollinger Band', color='green', linestylimport ose='--')

        # Find the starting time of the second CSV data
        if not filtered_df2.empty:
            second_start_time = filtered_df2['arrivaltime'].iloc[0]

            # Find the corresponding `lasttrprc` in the first CSV data at the second start time
            first_lasttrprc_at_start_time = filtered_df1.loc[filtered_df1['arrivaltime']
                                                             == second_start_time, 'lasttrprc']

            if not first_lasttrprc_at_start_time.empty:
                # Compute the offset
                offset = first_lasttrprc_at_start_time.iloc[0] - \
                    filtered_df2['lastpredtrprc'].iloc[0]
                offset1 = first_lasttrprc_at_start_time.iloc[0] - \
                    filtered_df2['ClusterCentroidHigh'].iloc[0]
                offset2 = first_lasttrprc_at_start_time.iloc[0] - \
                    filtered_df2['ClusterCentroidLow'].iloc[0]

        # Slicing the DataFrame to get every other row
        filtered_df2_alternate = filtered_df2.iloc[::60]

        # Plot the second CSV datwindow = 20
        # multiplier = 2

        # filtered_df1['SMA'] = filtered_df1['lasttrprc'].rolling(window=window).mean()
        # filtered_df1['STD'] = filtered_df1['lasttrprc'].rolling(window=window).std()
        # filtered_df1['Upper Band'] = filtered_df1['SMA'] + (multiplier * filtered_df1['STD'])
        # filtered_df1['Lower Band'] = filtered_df1['SMA'] - (multiplier * filtered_df1['STD'])

        #  # Calculate RSI for filtered_df1['lasttrprc']
        # delta = filtered_df1['lasttrprc'].diff()
        # gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        # loss = (-delta.where(delta
        ax.plot(filtered_df2['arrivaltime'], filtered_df2['lastpredtrprc'],
                label='Last Predicted Trade Price (CSV 2)', marker='.', color='orange',alpha=0.4, lw=4)
        # ax.plot(filtered_df2['arrivaltime'], filtered_df2['ClusterCentroidHigh'],
        #         label='Price with highest probability (CSV 2)', marker='.', color='cyan',alpha=0.5, lw=8)
        if self.show_SD:
            ax.plot(filtered_df2['arrivaltime'], filtered_df2['lastpredtrprc'] + filtered_df2['StanDev'],
                    label='M+StanDev', marker='.', color='green',alpha=0.6, lw=4)
            ax.plot(filtered_df2['arrivaltime'], filtered_df2['lastpredtrprc'] - filtered_df2['StanDev'],
                    label='M-StanDev', marker='.', color='red',alpha=0.6, lw=4)
        #ax.plot(filtered_df2['arrivaltime'], filtered_df2['ClusterCentroidLow'],
                #label='Price with Lowest probability (CSV 2)', marker='.', color='magenta',alpha=0.6, lw=8)
        # ax.plot(filtered_df2['arrivaltime'], filtered_df2['Max_Centroid'],
        #          label='Highest Price (CSV 2)', marker='^', color='green',alpha=0.7, lw=1)
        # ax.plot(filtered_df2['arrivaltime'], filtered_df2['Min_Centroid'],
        #          label='Lowest Price (CSV 2)', marker='v', color='red',alpha=0.7, lw=1)
        
        #ax.plot(filtered_df2['arrivaltime'], filtered_df2['ClusterCentroidHigh'] + 6*filtered_df2['StanDev'],
                #label='target price)', marker='.', color='brown')
        
        # Calculate the minimum value of 'ClusterCentroidHigh'
        min_cluster_centroid_high = filtered_df2['ClusterCentroidHigh'].min()
        max_stan_dev = filtered_df2['StanDev'].max()
        stop_loss_values = [min_cluster_centroid_high - 6 * max_stan_dev] * len(filtered_df2['arrivaltime'])
        # Plot with the stop loss values
        #ax.plot(filtered_df2['arrivaltime'], stop_loss_values,
                #label='stop loss', marker='.', color='black')
        
        # Merge filtered_df1 and filtered_df2 on the 'arrivaltime' column
        merged_df = pd.merge(filtered_df1, filtered_df2, on='arrivaltime', suffixes=('_df1', '_df2'))

        # Get the start value of 'lastpredtrprc'
        start_value = filtered_df2['lastpredtrprc'].iloc[0]
        print(f"Start value of lastpredtrprc: {start_value}")

        # Calculate the swing from the start value
        filtered_df2['swing'] = filtered_df2['lastpredtrprc'] - start_value

        # Print the swing values
        print("\nSwing values:")
        print(filtered_df2[['arrivaltime', 'lastpredtrprc', 'swing']])

        probability = float(self.probability_edit.text() or 0.7)
        swing_value = int(self.swing_edit.text() or 100)

        # Find all swing points with ±100 points
        swing_points = filtered_df2[
            (filtered_df2['swing'] >= swing_value) | (filtered_df2['swing'] <= -swing_value)
        ]

        # Filter for the first swing point with clusterProb > 0.7
        #swing_with_high_prob = swing_points[swing_points['clusterProb'] > probability].head(1)
        swing_with_high_prob = pd.DataFrame()
        prob_type = 'High_Prob'
        if (filtered_df2['swing'] >= swing_value).any():
            swing_with_high_prob = swing_points[swing_points['High_Prob'] > probability].head(1)
            prob_type = 'High_Prob'
        if (filtered_df2['swing'] <= -swing_value).any():
            swing_with_high_prob = swing_points[swing_points['Low_Prob'] > probability].head(1)
            prob_type = 'Low_Prob'
        #swing_with_high_prob = swing_points[swing_points['clusterProb'] > 0].head(1)

        # Check if a valid swing point with high probability exists
        if not swing_with_high_prob.empty:
            row = swing_with_high_prob.iloc[0]  # Extract the first row as a Series
            
            # Print success message to the command prompt
            print(
                f"Swing detected at {row['arrivaltime']} with "
                f"clusterProb {row['clusterProb']:.2f}."
            )

            # Annotate the point on the plot
            ax.text(
                row['arrivaltime'], row['lastpredtrprc'], 
                f"Swing: {row['lastpredtrprc']}\nProb: {row[prob_type]:.2f}", 
                color='red', fontsize=10, ha='center', va='bottom'
            )
        
            # Define output CSV file path
            # Get the directory of self.csv_file2
            # output_dir_swingfile = os.path.dirname(self.csv_file2)
            # output_csv_path = os.path.join(output_dir_swingfile, "filtered_swing_data.csv")

            # # Convert the 'arrivaltime' column to only show time (HH:MM:SS)
            # temp_df = filtered_df2.copy()
            # temp_df['arrivaltime'] = temp_df['arrivaltime'].dt.time  # Extract only the time part
            
            # # Check if the file exists to determine if header should be written
            # write_header = not os.path.exists(output_csv_path)
           
            # # Save filtered_df2 to CSV, appending if the file exists
            # temp_df.to_csv(
            #     output_csv_path, 
            #     mode='a', 
            #     index=False, 
            #     header=write_header,  # Only write the header if the file is new
            #     columns=[
            #         'arrivaltime', 'sectoken', 'lastpredtrprc', 'StanDev', 'low_prc', 'high_prc',
            #         'ClusterCentroidHigh', 'High_Prob', 'ClusterCentroidLow', 'Low_Prob', 
            #         'Max_Centroid', 'Min_Centroid', 'clusterIdx', 'clusterProb', 'fileSeqNum'
            #     ]
            # )
        else:
            # Print a message if no swing point with high probability is found
            print("No swing point with ±100 points and clusterProb > 0.7 detected.")

        



        # Add title and labels
        ax.set_title('Arrivaltime vs. Last Trade Price')
        ax.set_xlabel('Arrivaltime')
        ax.set_ylabel('Price')

        # Display the legend based on the flag
        if self.show_legend:
            ax.legend()

        # Plot RSI in a separate subplot
        # ax2 = self.figure.add_subplot(212)  # RSI plot
        # ax2.plot(filtered_df1['arrivaltime'], filtered_df1['RSI'], label='RSI', color='purple')
        # ax2.axhline(70, color='red', linestyle='--')  # Overbought threshold
        # ax2.axhline(30, color='green', linestyle='--')  # Oversold threshold

        # ax2.set_title('RSI')
        # ax2.set_xlabel('Arrivaltime')
        # ax2.set_ylabel('RSI')
        # if self.show_legend:
        #     ax2.legend()

        # Update the canvas
        self.canvas.draw()
    def get_opportunities(self):
        # Get start and end times from the time edit widgets
        start_time = self.start_time_edit.time().toString('HH:mm:ss')
        end_time = self.end_time_edit.time().toString('HH:mm:ss')

        # filtered_df2 = self.df2[
        #     (self.df2['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
        #     (self.df2['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
        # ]

        unique_file_seq_nums = self.df2['fileSeqNum'].dropna().unique().tolist()
        oppcount = 0
        # Loop through each unique file sequence number
        for file_seq_num in unique_file_seq_nums:
            #file_seq_num = 10
            # If file_seq_num is not provided, get it from the edit box
            #file_seq_num = int(self.sequence_edit.text() or unique_file_seq_nums[0])
            # print(f"start_time {start_time}")
            # print(f"file_seq_num {file_seq_num}")
            # Ensure the arrivaltime is a datetime object
            # Find the entries for the specified file sequence number
            sequence_entries = self.df2[self.df2['fileSeqNum'] == file_seq_num]

            

            # Check if any entries exist for the given sequence number
            if not sequence_entries.empty:
                # Get the start_time (1st entry) and end_time (last entry) for the specified fileSeqNum
                start_time = sequence_entries['arrivaltime'].min()  # First entry
                end_time = sequence_entries['arrivaltime'].max()    # Last entry

                # Update the start and end time edit widgets
                self.start_time_edit.setTime(start_time.time())
                self.end_time_edit.setTime(end_time.time())            

                filtered_df2 = sequence_entries  # Use only data from the provided sequence number
                
               
            # Get the start value of 'lastpredtrprc'
            start_value = filtered_df2['lastpredtrprc'].iloc[0]
            #print(f"Start value of lastpredtrprc: {start_value}")

            # Calculate the swing from the start value
            filtered_df3 = filtered_df2.copy()
            filtered_df3['swing'] = filtered_df2['lastpredtrprc'] - start_value
           
            # Calculate the maximum non-zero swing
            max_possible_swing = filtered_df3['swing'].abs().max()

            # Print the swing values
            #print("\nSwing values:")
            #print(filtered_df2[['arrivaltime', 'lastpredtrprc', 'swing']])

            probability = float(self.probability_edit.text() or 0)
            swing_value = int(self.swing_edit.text() or 100)

            # Find all swing points with ±100 points
            swing_points = filtered_df3[
                (filtered_df3['swing'] >= swing_value) | (filtered_df3['swing'] <= -swing_value)
            ]

            # Filter for the first swing point with clusterProb > 0.7
            #swing_with_high_prob = swing_points[swing_points['clusterProb'] > probability].head(1)
            swing_with_high_prob = pd.DataFrame()
            prob_type = 'High_Prob'
            if (filtered_df3['swing'] >= swing_value).any():
                swing_with_high_prob = swing_points[swing_points['High_Prob'] > probability].head(1)
                prob_type = 'High_Prob'
            if (filtered_df3['swing'] <= -swing_value).any():
                swing_with_high_prob = swing_points[swing_points['Low_Prob'] > probability].head(1)
                prob_type = 'Low_Prob'
            #swing_with_high_prob = swing_points[swing_points['clusterProb'] > 0].head(1)

            # Check if a valid swing point with high probability exists
            if not swing_with_high_prob.empty:
                row = swing_with_high_prob.iloc[0]  # Extract the first row as a Series
                oppcount = oppcount + 1
                # Print success message to the command prompt
                print(
                    f"Swing detected at file sequence : {file_seq_num}"
                    f" Maximum possible swing: {int(max_possible_swing)}"
                )
            #else:
                # Print a message if no swing point with high probability is found
                #print("No swing point detected.")
        print(f"Total opportunities : {oppcount}")

    def increment_sequence_number(self):
        # Retrieve the current sequence number from the edit box
        current_seq_num = int(self.sequence_edit.text() or 1)
        
        # Increment the sequence number
        updated_seq_num = current_seq_num + 1
        
        # Update the edit box with the new sequence number
        self.sequence_edit.setText(str(updated_seq_num))
        
        # Call the plot_graph method with the updated sequence number
        self.plot_graph(updated_seq_num)

    def decrement_sequence_number(self):
        # Retrieve the current sequence number from the edit box
        current_seq_num = int(self.sequence_edit.text() or 0)
        
        # Increment the sequence number
        updated_seq_num = current_seq_num - 1
        
        # Update the edit box with the new sequence number
        self.sequence_edit.setText(str(updated_seq_num))
        
        # Call the plot_graph method with the updated sequence number
        self.plot_graph(updated_seq_num)


    def advance_graph(self):
        try:
            # Get the interval from the interval edit widget
            interval_seconds = int(self.interval_edit.text())
        except ValueError:
            print("Please enter a valid integer for the interval.")
            return

        # Get the current start and end times
        current_start_time = self.start_time_edit.time()
        current_end_time = self.end_time_edit.time()

        # Add the interval to the current start and end times
        new_start_time = current_start_time.addSecs(interval_seconds)
        new_end_time = current_end_time.addSecs(interval_seconds)

        # Update the start and end time edit widgets
        self.start_time_edit.setTime(new_start_time)
        self.end_time_edit.setTime(new_end_time)

        # Replot the graph with the new start and end times
        self.plot_graph()

    def back_graph(self):
        try:
            # Get the interval from the interval edit widget
            interval_seconds = int(self.interval_edit.text())
        except ValueError:
            print("Please enter a valid integer for the interval.")
            return

        # Get the current start and end times
        current_start_time = self.start_time_edit.time()
        current_end_time = self.end_time_edit.time()

        # Subtract the interval from the current start and end times
        new_start_time = current_start_time.addSecs(-interval_seconds)
        new_end_time = current_end_time.addSecs(-interval_seconds)

        # Update the start and end time edit widgets
        self.start_time_edit.setTime(new_start_time)
        self.end_time_edit.setTime(new_end_time)

        # Replot the graph with the new start and end times
        self.plot_graph()

    def toggle_csv1_plot(self):
        """
        Toggle the visibility of the first CSV data plot.
        """
        self.show_csv1_plot = not self.show_csv1_plot
        self.toggle_csv1_button.setText(
            'Show CSV 1 Plot' if not self.show_csv1_plot else 'Hide CSV 1 Plot')
        self.plot_graph()

    def toggle_legend(self):
        """
        Toggle the visibility of the legend.
        """
        self.show_legend = not self.show_legend
        self.toggle_legend_button.setText(
            'Show Legend' if not self.show_legend else 'Hide Legend')
        self.plot_graph()

    def toggle_SD(self):
        """
        Toggle the visibility of the SD.
        """
        self.show_SD = not self.show_SD
        self.toggle_SD_button.setText(
            'Show SD' if not self.show_SD else 'Hide SD')
        self.plot_graph()

    def on_scroll(self, event):
        """
        Handle scroll event for zooming in and out.

        Args:
            event: The scroll event.
        """
        # Get the current axes
        ax = event.inaxes

        if ax is not None:
            # Determine the zoom factor
            zoom_factor = 1.1 if event.button == 'up' else 1/1.1

            # Apply zoom to the x-axis and y-axis
            ax.set_xlim([event.xdata - (event.xdata - ax.get_xlim()[0]) * zoom_factor,
                         event.xdata + (ax.get_xlim()[1] - event.xdata) * zoom_factor])
            ax.set_ylim([event.ydata - (event.ydata - ax.get_ylim()[0]) * zoom_factor,
                         event.ydata + (ax.get_ylim()[1] - event.ydata) * zoom_factor])

            # Redraw the canvas
            self.canvas.draw()


if __name__ == '__main__':
    # Initialize the QApplication
    app = QApplication(sys.argv)

    # Get the CSV file paths from the command line argument
    if len(sys.argv) < 3:
        print("Usage: python script.py <csv_file1_path> <csv_file2_path>")
        sys.exit(1)
    csv_file1_path = sys.argv[1]
    csv_file2_path = sys.argv[2]

    # Create the PlotWidget
    plot_widget = PlotWidget(csv_file1_path, csv_file2_path)

    # Show the widget
    plot_widget.show()

    # Start the event loop
    sys.exit(app.exec())
