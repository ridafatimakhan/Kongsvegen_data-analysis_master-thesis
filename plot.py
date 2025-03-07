import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file (update if needed)
file_path = 'H:/Rida/outlier_removed/13072021/M14/M140713160508/filtered_pressure_cleaned.txt'

# Read the data into a DataFrame (automatically read headers from file)
sensor_data_file = pd.read_csv(
    file_path,
    delimiter=',',
    na_values=['', ' '],  # Treat empty strings as NaN
    engine='python',
    on_bad_lines='skip',  # Skip lines with too many fields
    encoding='ISO-8859-1'
)

# Ensure 'time' column is numeric, drop any rows where 'time' is unreadable
sensor_data_file['time'] = pd.to_numeric(sensor_data_file['time'], errors='coerce')
sensor_data_file = sensor_data_file.dropna(subset=['time'])

# Convert 'time' to seconds and minutes (relative to the first timestamp)
t_1 = sensor_data_file['time'].iloc[0]
sensor_data_file['time_seconds'] = (sensor_data_file['time'] - t_1) * 0.001  # Convert to seconds
sensor_data_file['time_minutes'] = sensor_data_file['time_seconds'] / 60  # Convert to minutes

# Plot the data
plt.figure(figsize=(12, 6))

# Plot Pressure 1 vs Time
sns.lineplot(
    data=sensor_data_file,
    x='time_minutes',
    y='pressure1',
    label='Pressure 1',
    color='blue'
)

# Plot Pressure 2 vs Time
sns.lineplot(
    data=sensor_data_file,
    x='time_minutes',
    y='pressure2',
    label='Pressure 2',
    color='orange'
)

# Add labels, title, and legend
plt.xlabel('Time (minutes)', fontsize=14)
plt.ylabel('Pressure (units)', fontsize=14)
plt.title('Pressure over Time', fontsize=16)
plt.legend(title='Legend', fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()
