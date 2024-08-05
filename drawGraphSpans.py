import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTimeEdit, QFileDialog
from PyQt6.QtCore import QTime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.csv_file1 = None
        self.csv_file2 = None

        # Create a figure and a canvas to display the plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Create the navigation toolbar
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Create the start and end time widgets
        self.start_time_edit = QTimeEdit(self)
        self.start_time_edit.setDisplayFormat('HH:mm:ss')
        self.start_time_edit.setTime(QTime(9, 0, 0))  # Default start time: 09:00:00

        self.end_time_edit = QTimeEdit(self)
        self.end_time_edit.setDisplayFormat('HH:mm:ss')
        self.end_time_edit.setTime(QTime(16, 0, 0))  # Default end time: 16:00:00

        # Create the plot button
        self.plot_button = QPushButton('Plot', self)
        self.plot_button.clicked.connect(self.plot_graph)

        # Create the next button
        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.next_pair)

        # Create the browse buttons
        self.browse_button1 = QPushButton('Browse File 1', self)
        self.browse_button1.clicked.connect(self.browse_csv_file1)

        self.browse_button2 = QPushButton('Browse File 2', self)
        self.browse_button2.clicked.connect(self.browse_csv_file2)

        # Create layout for time edit widgets, plot button, next button, and browse buttons
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_time_edit)
        controls_layout.addWidget(self.end_time_edit)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.browse_button1)
        controls_layout.addWidget(self.browse_button2)

        # Create the main layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addLayout(controls_layout)

        # Set the main layout
        self.setLayout(layout)

    def browse_csv_file1(self):
        """
        Open a file dialog to select the first CSV file.
        """
        csv_file1, _ = QFileDialog.getOpenFileName(self, "Select CSV File 1", "", "CSV Files (*.csv)")
        if csv_file1:
            self.csv_file1 = csv_file1
            self.load_data()
            self.plot_graph()

    def browse_csv_file2(self):
        """
        Open a file dialog to select the second CSV file.
        """
        csv_file2, _ = QFileDialog.getOpenFileName(self, "Select CSV File 2", "", "CSV Files (*.csv)")
        if csv_file2:
            self.csv_file2 = csv_file2
            self.load_data()
            self.plot_graph()

    def load_data(self):
        if self.csv_file1:
            # Load the first CSV data into a DataFrame
            self.df1 = pd.read_csv(self.csv_file1)
            self.df1['arrivaltime'] = pd.to_datetime(self.df1['arrivaltime'], format='%H:%M:%S')

        if self.csv_file2:
            # Load the second CSV data into another DataFrame
            self.df2 = pd.read_csv(self.csv_file2)
            self.df2['arrivaltime'] = pd.to_datetime(self.df2['arrivaltime'], format='%H:%M:%S')

    def plot_graph(self):
        # Clear the existing plot
        self.figure.clear()

        if self.csv_file1:
            # Get start and end times from the time edit widgets
            start_time = self.start_time_edit.time().toString('HH:mm:ss')
            end_time = self.end_time_edit.time().toString('HH:mm:ss')

            # Filter the data based on the specified time range
            filtered_df1 = self.df1[
                (self.df1['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
                (self.df1['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
            ]

            # Create a new plot for the first CSV file
            ax = self.figure.add_subplot(111)
            ax.plot(filtered_df1['arrivaltime'], filtered_df1['lasttrprc'], label='Last Trade Price (CSV 1)', marker='o')

            # Add title and labels
            ax.set_title('Arrivaltime vs. Last Trade Price')
            ax.set_xlabel('Arrivaltime')
            ax.set_ylabel('Price')

            # Display the legend
            ax.legend()

        if self.csv_file2:
            # Get start and end times from the time edit widgets
            start_time = self.start_time_edit.time().toString('HH:mm:ss')
            end_time = self.end_time_edit.time().toString('HH:mm:ss')

            # Filter the data based on the specified time range
            filtered_df2 = self.df2[
                (self.df2['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
                (self.df2['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
            ]

            # Create a new plot for the second CSV file
            ax = self.figure.add_subplot(111)

            # Plot the second CSV data
            ax.plot(filtered_df2['arrivaltime'], filtered_df2['lasttrprc'], label='Last Trade Price (CSV 2)', marker='o')

            # Add title and labels
            ax.set_title('Arrivaltime vs. Last Trade Price')
            ax.set_xlabel('Arrivaltime')
            ax.set_ylabel('Price')

            # Display the legend
            ax.legend()

        # Update the canvas
        self.canvas.draw()

    def next_pair(self):
        """
        Load and plot the next pair of files.
        """
        pass  # Implement this method if needed

if __name__ == '__main__':
    # Initialize the QApplication
    app = QApplication(sys.argv)

    # Create the PlotWidget
    plot_widget = PlotWidget()

    # Show the widget
    plot_widget.show()

    # Start the event loop
    sys.exit(app.exec())

