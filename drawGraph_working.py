import sys
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTimeEdit, QLabel, QLineEdit, QFileDialog
from PyQt6.QtCore import QTime
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.csv_file1 = None
        self.csv_file2 = None
        self.csv_file1_directory = None
        self.csv_file2_directory = None
        self.csv_file1_list = []
        self.csv_file2_list = []
        self.csv_file1_index = 0
        self.csv_file2_index = 0

        # Create a figure and a canvas to display the plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Set minimum size for the canvas to increase the plot area
        self.canvas.setMinimumSize(800, 600)  # Adjust these values as needed

        # Create the navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Create the start and end time widgets
        self.start_time_edit = QTimeEdit(self)
        self.start_time_edit.setDisplayFormat('HH:mm:ss')
        self.start_time_edit.setTime(QTime(9, 0, 0))  # Default start time: 09:00:00
        self.start_time_edit.setFont(QFont('Arial', 14))
        self.start_time_edit.setFixedSize(120, 40)

        self.end_time_edit = QTimeEdit(self)
        self.end_time_edit.setDisplayFormat('HH:mm:ss')
        self.end_time_edit.setTime(QTime(16, 0, 0))  # Default end time: 16:00:00
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

        # Create buttons to load CSV files
        self.load_file1_button = QPushButton('Load CSV 1', self)
        self.load_file1_button.setFont(QFont('Arial', 14))
        self.load_file1_button.setFixedSize(150, 40)
        self.load_file1_button.clicked.connect(self.load_csv1)

        self.load_file2_button = QPushButton('Load CSV 2', self)
        self.load_file2_button.setFont(QFont('Arial', 14))
        self.load_file2_button.setFixedSize(150, 40)
        self.load_file2_button.clicked.connect(self.load_csv2)

        # Create buttons to load next CSV files
        self.next_file1_button = QPushButton('Next CSV 1', self)
        self.next_file1_button.setFont(QFont('Arial', 14))
        self.next_file1_button.setFixedSize(150, 40)
        self.next_file1_button.clicked.connect(self.next_csv1)

        self.next_file2_button = QPushButton('Next CSV 2', self)
        self.next_file2_button.setFont(QFont('Arial', 14))
        self.next_file2_button.setFixedSize(150, 40)
        self.next_file2_button.clicked.connect(self.next_csv2)

        # Create labels to display filenames
        self.file1_label = QLabel(self)
        self.file1_label.setFont(QFont('Arial', 12))

        self.file2_label = QLabel(self)
        self.file2_label.setFont(QFont('Arial', 12))

        # Create layout for time edit widgets, plot button, interval edit, and advance button
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_time_edit)
        controls_layout.addWidget(self.end_time_edit)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.interval_edit)
        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.advance_button)
        controls_layout.addWidget(self.load_file1_button)
        controls_layout.addWidget(self.next_file1_button)
        controls_layout.addWidget(self.load_file2_button)
        controls_layout.addWidget(self.next_file2_button)

        # Create layout for file labels
        file_labels_layout = QHBoxLayout()
        file_labels_layout.addWidget(self.file1_label)
        file_labels_layout.addWidget(self.file2_label)

        # Create the main layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addLayout(controls_layout)
        layout.addLayout(file_labels_layout)

        # Ensure the canvas stretches with the window resize
        layout.setStretchFactor(self.canvas, 1)

        # Set the main layout
        self.setLayout(layout)

        # Connect the scroll event to the on_scroll method
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

    def load_csv1(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open CSV File 1', '', 'CSV files (*.csv)')
        if file_path:
            self.csv_file1 = file_path
            self.csv_file1_directory = os.path.dirname(file_path)
            self.csv_file1_list = sorted(
                [f for f in os.listdir(self.csv_file1_directory) if f.endswith('.csv')],
                key=natural_sort_key
            )
            self.csv_file1_index = self.csv_file1_list.index(os.path.basename(file_path))
            self.file1_label.setText(f"CSV File 1: {os.path.basename(file_path)}")
            self.load_data()
            self.plot_graph()

    def load_csv2(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open CSV File 2', '', 'CSV files (*.csv)')
        if file_path:
            self.csv_file2 = file_path
            self.csv_file2_directory = os.path.dirname(file_path)
            self.csv_file2_list = sorted(
                [f for f in os.listdir(self.csv_file2_directory) if f.endswith('.csv')],
                key=natural_sort_key
            )
            self.csv_file2_index = self.csv_file2_list.index(os.path.basename(file_path))
            self.file2_label.setText(f"CSV File 2: {os.path.basename(file_path)}")
            self.load_data()
            self.plot_graph()

    def next_csv1(self):
        if self.csv_file1_directory and self.csv_file1_index + 1 < len(self.csv_file1_list):
            self.csv_file1_index += 1
            self.csv_file1 = os.path.join(self.csv_file1_directory, self.csv_file1_list[self.csv_file1_index])
            self.file1_label.setText(f"CSV File 1: {self.csv_file1_list[self.csv_file1_index]}")
            self.load_data()
            self.plot_graph()

    def next_csv2(self):
        if self.csv_file2_directory and self.csv_file2_index + 1 < len(self.csv_file2_list):
            self.csv_file2_index += 1
            self.csv_file2 = os.path.join(self.csv_file2_directory, self.csv_file2_list[self.csv_file2_index])
            self.file2_label.setText(f"CSV File 2: {self.csv_file2_list[self.csv_file2_index]}")
            self.load_data()
            self.plot_graph()

    def load_data(self):
        if self.csv_file1:
            self.df1 = pd.read_csv(self.csv_file1)
            self.df1['arrivaltime'] = pd.to_datetime(self.df1['arrivaltime'], format='%H:%M:%S')

        if self.csv_file2:
            self.df2 = pd.read_csv(self.csv_file2)
            self.df2['arrivaltime'] = pd.to_datetime(self.df2['arrivaltime'], format='%H:%M:%S')

    def plot_graph(self):
        start_time = self.start_time_edit.time().toString('HH:mm:ss')
        end_time = self.end_time_edit.time().toString('HH:mm:ss')

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if self.csv_file1:
            filtered_df1 = self.df1[
                (self.df1['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
                (self.df1['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
            ]
            ax.plot(filtered_df1['arrivaltime'], filtered_df1['lasttrprc'], label='Last Trade Price (CSV 1)', marker='o')

        if self.csv_file2:
            filtered_df2 = self.df2[
                (self.df2['arrivaltime'].dt.time >= pd.to_datetime(start_time).time()) &
                (self.df2['arrivaltime'].dt.time <= pd.to_datetime(end_time).time())
            ]
            ax.plot(filtered_df2['arrivaltime'], filtered_df2['lastpredtrprc'], label='Last Predicted Trade Price (CSV 2)', marker='.')

        ax.set_title('Arrivaltime vs. Last Trade Price')
        ax.set_xlabel('Arrivaltime')
        ax.set_ylabel('Price')
        ax.legend()
        self.canvas.draw()

    def advance_graph(self):
        try:
            interval_seconds = int(self.interval_edit.text())
        except ValueError:
            print("Please enter a valid integer for the interval.")
            return

        current_start_time = self.start_time_edit.time()
        current_end_time = self.end_time_edit.time()
        new_start_time = current_start_time.addSecs(interval_seconds)
        new_end_time = current_end_time.addSecs(interval_seconds)

        self.start_time_edit.setTime(new_start_time)
        self.end_time_edit.setTime(new_end_time)
        self.plot_graph()

    def back_graph(self):
        try:
            interval_seconds = int(self.interval_edit.text())
        except ValueError:
            print("Please enter a valid integer for the interval.")
            return

        current_start_time = self.start_time_edit.time()
        current_end_time = self.end_time_edit.time()
        new_start_time = current_start_time.addSecs(-interval_seconds)
        new_end_time = current_end_time.addSecs(-interval_seconds)

        self.start_time_edit.setTime(new_start_time)
        self.end_time_edit.setTime(new_end_time)
        self.plot_graph()

    def on_scroll(self, event):
        ax = event.inaxes
        if ax is not None:
            zoom_factor = 1.1 if event.button == 'up' else 1 / 1.1
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            xdata, ydata = event.xdata, event.ydata
            ax.set_xlim([xdata - (xdata - xlim[0]) / zoom_factor,
                         xdata + (xlim[1] - xdata) / zoom_factor])
            ax.set_ylim([ydata - (ydata - ylim[0]) / zoom_factor,
                         ydata + (ylim[1] - ydata) / zoom_factor])
            self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    plot_widget = PlotWidget()
    plot_widget.show()
    sys.exit(app.exec())
