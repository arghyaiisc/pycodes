import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV data into a DataFrame
csv_file = '../data/19062024/op_44403.csv'
df = pd.read_csv(csv_file)

# Ensure the 'arrivaltime' column is treated as a string for proper plotting
df['arrivaltime'] = df['arrivaltime'].astype(str)

# Calculate the moving average of the 'lastpredtrprc' column
window_size = 5  # Define the window size for the moving average
df['moving_avg'] = df['lastpredtrprc'].rolling(window=window_size).mean()

# Plot the original data and the moving average
plt.figure(figsize=(10, 6))
plt.plot(df['arrivaltime'], df['lastpredtrprc'], label='Last Predicted Trade Price', marker='o')
plt.plot(df['arrivaltime'], df['moving_avg'], label=f'Moving Average (window size = {window_size})', linestyle='--', color='orange')

# Add title and labels
plt.title('Arrivaltime vs. Last Trade Price with Moving Average')
plt.xlabel('Arrivaltime')
plt.ylabel('Price')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Display the legend
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()

