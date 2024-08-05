import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTimeEdit, QLabel, QLineEdit
from PyQt6.QtCore import QTime, QTimer
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure


class PlotWidget(QWidget):
    def __init__(self, csv_file1, csv_file2):
        super().__init__()

        self.csv_file1 = csv_file1
        self.csv_file2 = csv_file2

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

        # Create layout for time edit widgets, plot button, interval edit, and advance button
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_time_edit)
        controls_layout.addWidget(self.end_time_edit)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.interval_edit)
        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.advance_button)

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
        self.df1['arrivaltime'] = pd.to_datetime(
            self.df1['arrivaltime'], format='%H:%M:%S')

        # Load the second CSV data into another DataFrame
        self.df2 = pd.read_csv(self.csv_file2)
        self.df2['arrivaltime'] = pd.to_datetime(
            self.df2['arrivaltime'], format='%H:%M:%S')

    def plot_graph(self):
        # Get start and end times from the time edit widgets
        start_time = self.start_time_edit.time().toString('HH:mm:ss')
        end_time = self.end_time_edit.time().toString('HH:mm:ss')

        # Filter the data based on the specified time range
        filtered_df1 = self.df1[
            (self.df1['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
            (self.df1['arrivaltime'].dt.time <=
             pd.to_datetime(end_time).time())
        ]

        filtered_df2 = self.df2[
            (self.df2['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
            (self.df2['arrivaltime'].dt.time <=
             pd.to_datetime(end_time).time())
        ]

        # Clear the existing plot
        self.figure.clear()

        # Create a new plot
        ax = self.figure.add_subplot(111)

        # Plot the first CSV data
        ax.plot(filtered_df1['arrivaltime'], filtered_df1['lasttrprc'],
                label='Last Trade Price (CSV 1)', marker='o')

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
                
        # Slicing the DataFrame to get every other row
        filtered_df2_alternate = filtered_df2.iloc[::60]


        # Plot the second CSV data
        ax.plot(filtered_df2_alternate['arrivaltime'], filtered_df2_alternate['lastpredtrprc'],
                label='Last Predicted Trade Price (CSV 2)', marker='.')

        # Add title and labels
        ax.set_title('Arrivaltime vs. Last Trade Price')
        ax.set_xlabel('Arrivaltime')
        ax.set_ylabel('Price')

        # Display the legend
        ax.legend()

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
        current_start_time = self.end_time_edit.time() 
        current_end_time = self.start_time_edit.time()

        # Add the interval to the current start and end times
        new_start_time = current_end_time.addSecs(interval_seconds)
        new_end_time = current_start_time.addSecs(interval_seconds) 

        # Update the start and end time edit widgets
        self.start_time_edit.setTime(new_end_time)
        self.end_time_edit.setTime(new_start_time)

        # Replot the graph with the new start and end times
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

