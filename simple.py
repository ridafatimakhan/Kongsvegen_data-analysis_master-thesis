import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
file_path = 'H:/Rida/13072021/B10/Original/B100713154414.txt'

# Define column names for the dataset (first 17 columns)
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# Read the data into a DataFrame (only the first 17 columns)
sensor_data_file = pd.read_csv(
    file_path,
    names=column_names,
    delimiter=',',
    header=None,
    na_values=['', ' '],  # Treat empty strings as NaN
    engine='python',
    usecols=range(17),  # Use only the first 17 columns
    on_bad_lines='skip'  # Skip lines with too many fields
)

# Replace invalid entries with NaN and convert columns to numeric
sensor_data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        sensor_data_file[col] = pd.to_numeric(sensor_data_file[col], errors='coerce')

# Convert 'time' to seconds and minutes based on the teacher's hint
t_1 = sensor_data_file['time'].iloc[0]  # First time value
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
