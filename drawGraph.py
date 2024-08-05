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
import numpy as np


class PlotWidget(QWidget):
    def __init__(self, csv_file1, csv_file2):
        super().__init__()

        self.csv_file1 = csv_file1
        self.csv_file2 = csv_file2

        # Flag to track visibility of first CSV data plot
        self.show_csv1_plot = True

        # Flag to track visibility of the legend
        self.show_legend = True

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

        # Create the interval input and advance button
        self.interval_edit = QLineEdit(self)
        self.interval_edit.setPlaceholderText('Interval (s)')
        self.interval_edit.setFont(QFont('Arial', 14))
        self.interval_edit.setFixedSize(120, 40)

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

        # Create layout for time edit widgets, plot button, interval edit, and advance button
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_time_edit)
        controls_layout.addWidget(self.end_time_edit)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.interval_edit)
        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.advance_button)
        controls_layout.addWidget(self.toggle_csv1_button)
        controls_layout.addWidget(self.toggle_legend_button)

        # Display the CSV file name
        file_label = QLabel(f"CSV File 2: {self.csv_file2}")
        file_label.setMaximumHeight(20)

        # Create the main layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(file_label)
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

    def plot_graph(self):
        # Get start and end times from the time edit widgets
        start_time = self.start_time_edit.time().toString('HH:mm:ss')
        end_time = self.end_time_edit.time().toString('HH:mm:ss')

        # Filter the data based on the specified time range
        filtered_df1 = self.df1[
            (self.df1['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
            (self.df1['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
        ]

        filtered_df2 = self.df2[
            (self.df2['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
            (self.df2['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
        ]

        # Calculate Bollinger Bands for filtered_df1['lasttrprc']
        window = 20
        multiplier = 2

        filtered_df1['SMA'] = filtered_df1['lasttrprc'].rolling(window=window).mean()
        filtered_df1['STD'] = filtered_df1['lasttrprc'].rolling(window=window).std()
        filtered_df1['Upper Band'] = filtered_df1['SMA'] + (multiplier * filtered_df1['STD'])
        filtered_df1['Lower Band'] = filtered_df1['SMA'] - (multiplier * filtered_df1['STD'])

         # Calculate RSI for filtered_df1['lasttrprc']
        delta = filtered_df1['lasttrprc'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        RS = gain / loss
        filtered_df1['RSI'] = 100 - (100 / (1 + RS))

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
            #         label='Lower Bollinger Band', color='green', linestyle='--')

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

        # Plot the second CSV data
        ax.plot(filtered_df2['arrivaltime'], filtered_df2['lastpredtrprc'],
                label='Last Predicted Trade Price (CSV 2)', marker='.', color='orange',alpha=0.4, lw=1)
        ax.plot(filtered_df2['arrivaltime'], filtered_df2['ClusterCentroidHigh'],
                label='Price with highest probability (CSV 2)', marker='.', color='cyan',alpha=0.5, lw=8)
        ax.plot(filtered_df2['arrivaltime'], filtered_df2['ClusterCentroidLow'],
                label='Price with Lowest probability (CSV 2)', marker='.', color='magenta',alpha=0.6, lw=8)
        ax.plot(filtered_df2['arrivaltime'], filtered_df2['Max_Centroid'],
                label='Highest Price (CSV 2)', marker='^', color='green',alpha=0.7, lw=1)
        ax.plot(filtered_df2['arrivaltime'], filtered_df2['Min_Centroid'],
                label='Lowest Price (CSV 2)', marker='v', color='red',alpha=0.7, lw=1)
        
        #ax.plot(filtered_df2['arrivaltime'], filtered_df2['ClusterCentroidHigh'] + 6*filtered_df2['StanDev'],
                #label='target price)', marker='.', color='brown')
        
        # Calculate the minimum value of 'ClusterCentroidHigh'
        min_cluster_centroid_high = filtered_df2['ClusterCentroidHigh'].min()
        max_stan_dev = filtered_df2['StanDev'].max()
        stop_loss_values = [min_cluster_centroid_high - 6 * max_stan_dev] * len(filtered_df2['arrivaltime'])
        # Plot with the stop loss values
        ax.plot(filtered_df2['arrivaltime'], stop_loss_values,
                label='stop loss', marker='.', color='black')
        
        # Initialize counters
        buy_signals_count = 0
        successful_trades_count = 0
        net_profit = 0
        total_profits = 0
        total_losses = 0
        total_investment = 1000
        #stock_count = 0

        # Loop through the filtered_df2 DataFrame to find BUY signals and successful trades
        for i in range(4, len(filtered_df2), 60):
            if i + 60 < len(filtered_df2):
                max_centroid_current = filtered_df2['Max_Centroid'].iloc[i]
                min_centroid_current = filtered_df2['Min_Centroid'].iloc[i]
                min_centroid_next = filtered_df2['Min_Centroid'].iloc[i + 60]
                max_centroid_next = filtered_df2['Max_Centroid'].iloc[i + 60]

                if max_centroid_next < min_centroid_current:
                    stock_count = total_investment/max_centroid_next
                    print(f"stock count : {stock_count}")
                    # Plot BUY signal marker
                    ax.plot(filtered_df2['arrivaltime'].iloc[i + 60], max_centroid_next,
                            marker='*', color='yellow', markersize=15, label='BUY' if buy_signals_count == 0 else "")
                    buy_signals_count += 1                
                    

                    # Plot Stop Loss marker
                    ax.plot(filtered_df2['arrivaltime'].iloc[i + 60], min_centroid_next,
                            marker='x', color='green', markersize=15, label='Stop Loss' if buy_signals_count == 1 else "")

                    # Determine the index of the next BUY signal
                    next_buy_signal_index = None
                    for j in range(i + 60 + 1, len(filtered_df2), 60):
                        if j + 60 < len(filtered_df2) and filtered_df2['Max_Centroid'].iloc[j + 60] < filtered_df2['Min_Centroid'].iloc[j]:
                            next_buy_signal_index = j + 60
                            break
                    if next_buy_signal_index is None:
                        next_buy_signal_index = len(filtered_df2)

                    # Check if lasttrprc in filtered_df1 reaches the target price before the next BUY signal
                    target_price = min_centroid_current
                    stop_loss = min_centroid_next
                    trade_successful = False
                    print(f"Target Price: {target_price}")

                    for k in range(i + 60, next_buy_signal_index):
                        if k >= len(filtered_df1):
                            break  # Ensure we do not exceed the bounds of filtered_df1
                            
                        if filtered_df1['lasttrprc'].iloc[k] < stop_loss:
                            # Price drops below stop loss, trade fails
                            
                            net_loss = (stop_loss - max_centroid_next)*stock_count
                            net_profit += net_loss
                            total_losses += net_loss
                            print(f"Trade failed: Loss = {net_loss}")
                            break

                        if filtered_df1['lasttrprc'].iloc[k] >= target_price:
                            # Price reaches or exceeds target price, trade successful
                            trade_successful = True
                            
                            profit = (filtered_df1['lasttrprc'].iloc[k] - max_centroid_next)*stock_count
                            net_profit += profit
                            total_profits += profit
                            ax.plot(filtered_df1['arrivaltime'].iloc[k], filtered_df1['lasttrprc'].iloc[k],
                                    marker='o', color='pink', markersize=15, label='Successful Trade' if successful_trades_count == 0 else "")
                            successful_trades_count += 1
                            print(f"Trade successful: Profit = {profit}")
                            break

        # Display the total count of BUY signals and successful trades on the plot
        ax.text(0.95, 0.95, f'Total BUY signals: {buy_signals_count}', horizontalalignment='right',
                verticalalignment='top', transform=ax.transAxes, fontsize=12, color='green', bbox=dict(facecolor='white', alpha=0.5))

        ax.text(0.95, 0.90, f'Successful Trades: {successful_trades_count}', horizontalalignment='right',
                verticalalignment='top', transform=ax.transAxes, fontsize=12, color='red', bbox=dict(facecolor='white', alpha=0.5))

        # Display the net profit, total profits, and total losses on the plot
        ax.text(0.95, 0.85, f'Net Profit: {net_profit:.2f}', horizontalalignment='right',
                verticalalignment='top', transform=ax.transAxes, fontsize=12, color='blue', bbox=dict(facecolor='white', alpha=0.5))

        ax.text(0.95, 0.80, f'Total Profits: {total_profits:.2f}', horizontalalignment='right',
                verticalalignment='top', transform=ax.transAxes, fontsize=12, color='blue', bbox=dict(facecolor='white', alpha=0.5))

        ax.text(0.95, 0.75, f'Total Losses: {total_losses:.2f}', horizontalalignment='right',
                verticalalignment='top', transform=ax.transAxes, fontsize=12, color='blue', bbox=dict(facecolor='white', alpha=0.5))




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
