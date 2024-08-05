import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTimeEdit, QLabel
from PyQt6.QtCore import QTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure

class PlotWidget(QWidget):
    def __init__(self, folder_path, plot_title, price_column):
        super().__init__()

        self.folder_path = folder_path
        self.plot_title = plot_title
        self.price_column = price_column

        # Get list of CSV files in the folder and sort them
        self.csv_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')],
                                key=lambda x: int(x.split('_')[-1].split('.')[0]))

        # Initialize current file index
        self.current_file_index = 0

        # Create a figure and a canvas to display the plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Create the navigation toolbar
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Create the start and end time widgets
        self.start_time_edit = QTimeEdit(self)
        self.start_time_edit.setDisplayFormat('HH:mm:ss')
        self.start_time_edit.setTime(QTime(9, 0, 0))

        self.end_time_edit = QTimeEdit(self)
        self.end_time_edit.setDisplayFormat('HH:mm:ss')
        self.end_time_edit.setTime(QTime(16, 0, 0))

        # Create the plot button
        self.plot_button = QPushButton('Plot', self)
        self.plot_button.clicked.connect(self.plot_graph)

        # Create navigation buttons
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.back_file)

        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.next_file)

        # Create a QLabel to display the current file name
        self.file_name_label = QLabel(self)

        # Create layout for time edit widgets and buttons
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_time_edit)
        controls_layout.addWidget(self.end_time_edit)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.file_name_label)  # Add file name label to the layout

        # Create the main layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addLayout(controls_layout)

        # Set the main layout
        self.setLayout(layout)

        # Load the data and initialize the plot
        self.load_data()
        self.plot_graph()

    def load_data(self):
        # Load the CSV file at the current index
        csv_file_path = os.path.join(self.folder_path, self.csv_files[self.current_file_index])
        self.df = pd.read_csv(csv_file_path)
        # Convert 'arrivaltime' column to datetime format
        self.df['arrivaltime'] = pd.to_datetime(self.df['arrivaltime'], format='%H:%M:%S')
        
        # Update the file name label
        self.file_name_label.setText(f"File: {self.csv_files[self.current_file_index]}")

    def plot_graph(self):
    
        # Get start and end times from the time edit widgets
        start_time = self.start_time_edit.time().toString('HH:mm:ss')
        end_time = self.end_time_edit.time().toString('HH:mm:ss')

        # Filter the data based on the specified time range
        filtered_df = self.df[
            (self.df['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
            (self.df['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
        ]

        # Clear the existing plot
        self.figure.clear()

        # Create a new plot
        ax = self.figure.add_subplot(111)
        ax.plot(filtered_df['arrivaltime'], filtered_df[self.price_column], label='Last Trade Price', marker='o')

        # Add title and labels
        ax.set_title(f'Arrivaltime vs. Last Trade Price ({self.plot_title})')
        ax.set_xlabel('Arrivaltime')
        ax.set_ylabel('Last Trade Price')

        # Display the legend
        ax.legend()

        # Update the canvas
        self.canvas.draw()

    def next_file(self):
        # Move to the next file if possible and update data and plot
        if self.current_file_index < len(self.csv_files) - 1:
            self.current_file_index += 1
            self.load_data()
            self.plot_graph()

    def back_file(self):
        # Move to the previous file if possible and update data and plot
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.load_data()
            self.plot_graph()

class ParallelPlotWidget(QWidget):
    def __init__(self, folder1_path, folder2_path):
        super().__init__()

        # Create PlotWidget instances for each folder with the appropriate price columns
        self.plot_widget1 = PlotWidget(folder1_path, 'Folder 1', 'lastpredtrprc')
        self.plot_widget2 = PlotWidget(folder2_path, 'Folder 2', 'lasttrprc')

        # Create a horizontal layout to hold both PlotWidget instances
        layout = QHBoxLayout()
        layout.addWidget(self.plot_widget1)
        layout.addWidget(self.plot_widget2)

        # Set the main layout
        self.setLayout(layout)

if __name__ == '__main__':
    # Initialize the QApplication
    app = QApplication(sys.argv)

    # Get the folder paths from the command line arguments
    if len(sys.argv) < 3:
        print("Usage: python script.py <folder1_path> <folder2_path>")
        sys.exit(1)
    folder2_path = sys.argv[1]
    folder1_path = sys.argv[2]

    # Create the ParallelPlotWidget
    parallel_plot_widget = ParallelPlotWidget(folder1_path, folder2_path)

    # Show the widget
    parallel_plot_widget.show()

    # Start the event loop
    sys.exit(app.exec())

