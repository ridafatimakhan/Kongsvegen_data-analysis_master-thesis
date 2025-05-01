import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
file_path = 'H:/Rida/Dataset/13072021/M18/M180713151102.txt'

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
    na_values=['', ' '],
    engine='python',
    usecols=range(17),
    on_bad_lines='skip',
    encoding='ISO-8859-1'
)

# Replace invalid entries with NaN and convert columns to numeric
sensor_data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        sensor_data_file[col] = pd.to_numeric(sensor_data_file[col], errors='coerce')

# Convert 'time' to seconds and minutes
t_1 = sensor_data_file['time'].iloc[0]
sensor_data_file['time_seconds'] = (sensor_data_file['time'] - t_1) * 0.001
sensor_data_file['time_minutes'] = sensor_data_file['time_seconds'] / 60

# Compute rolling standard deviation for pressure1
window_size = 100
sensor_data_file['pressure1_std'] = sensor_data_file['pressure1'].rolling(window=window_size).std()

# Identify regions where std exceeds a threshold
threshold = sensor_data_file['pressure1_std'].mean() + sensor_data_file['pressure1_std'].std()
high_fluct = sensor_data_file[sensor_data_file['pressure1_std'] > threshold]

import matplotlib.patches as patches

# Plot the data
plt.figure(figsize=(10, 5))
sns.lineplot(data=sensor_data_file, x='time_minutes', y='pressure1', label='Pressure 1', color='orange')
sns.lineplot(data=sensor_data_file, x='time_minutes', y='pressure2', label='Pressure 2', color='blue')

# Define high fluctuation area
if not high_fluct.empty:
    start_time = high_fluct['time_minutes'].iloc[0]
    end_time = high_fluct['time_minutes'].iloc[-1]
    mid_time = (start_time + end_time) / 2
    pressure_min = sensor_data_file[['pressure1', 'pressure2']].min().min()
    pressure_max = sensor_data_file[['pressure1', 'pressure2']].max().max()
    vertical_center = (pressure_min + pressure_max) / 2

    # Add ellipse to highlight region
    ellipse_width = end_time - start_time + 2 # Add padding
    ellipse_height = pressure_max - pressure_min + 100  # Add padding
    ellipse = patches.Ellipse(
        (mid_time, vertical_center),  # (x_center, y_center)
        width=ellipse_width,
        height=ellipse_height,
        linewidth=2,
        edgecolor='grey',
        facecolor='grey'
    )
    plt.gca().add_patch(ellipse)

# Add arrow and annotation
plt.annotate('Region of Interest (ROI)',
             xy=(mid_time, vertical_center),  # arrow points here
             xytext=(mid_time + 5, vertical_center + 50),  # text location
             arrowprops=dict(color='black', arrowstyle='->'),  # black arrow
             fontsize=12,
             weight='bold')


# Final touches
plt.xlabel('Time [minutes]', fontsize=16)
plt.ylabel('Pressure [hPa]', fontsize=16)
plt.legend(fontsize=14)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)


plt.tight_layout()
plt.show()
