import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import find_peaks

# Set the style for the plot
sns.set(style="darkgrid")

# File path
file_path = 'H:/Rida/outlier_removed/13072021/M15/M150713160801/filtered_pressure_cleaned.txt'

# Read the sensor data file
sensor_data_file = pd.read_csv(
    file_path,
    delimiter=',',
    na_values=['', ' '],  
    engine='python',
    on_bad_lines='skip',  
    encoding='ISO-8859-1'
)

# Ensure 'time' column is numeric, drop unreadable rows
sensor_data_file['time'] = pd.to_numeric(sensor_data_file['time'], errors='coerce')
sensor_data_file = sensor_data_file.dropna(subset=['time'])

# Convert 'time' to seconds
t_1 = sensor_data_file['time'].iloc[0]
sensor_data_file['time_seconds'] = (sensor_data_file['time'] - t_1) * 0.001  

# Extract data
time = sensor_data_file['time_seconds'].values
pressure1 = sensor_data_file['pressure1'].values  
pressure2 = sensor_data_file['pressure2'].values  
accx = sensor_data_file['accx'].values
accy = sensor_data_file['accy'].values
accz = sensor_data_file['accz'].values

# Compute acceleration magnitude
acc_magnitude = np.sqrt(accx**2 + accy**2 + accz**2)

# Detect peaks in acceleration above 35
acc_peaks, _ = find_peaks(acc_magnitude, height=30)

# Detect peaks in pressure1 and pressure2
pressure1_peaks, _ = find_peaks(pressure1)
pressure2_peaks, _ = find_peaks(pressure2)

# Find common peaks in all three signals
common_peaks = np.intersect1d(np.intersect1d(acc_peaks, pressure1_peaks), pressure2_peaks)

# Apply the new condition: Remove peaks where the difference from the previous value is < 10 hPa
filtered_peaks = []
for peak in common_peaks:
    if peak > 0:  # Ensure we don't access negative index
        if abs(pressure1[peak] - pressure1[peak - 1]) >= 5 or abs(pressure2[peak] - pressure2[peak - 1]) >= 5:
            filtered_peaks.append(peak)

filtered_peaks = np.array(filtered_peaks, dtype=int)  # Convert to NumPy array

# Create subplots
fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

# Plot Acceleration Magnitude
axes[0].plot(time, acc_magnitude, label="Acceleration Mag", color="b", alpha=0.7)
axes[0].scatter(time[filtered_peaks], acc_magnitude[filtered_peaks], color='r', label="IDC", marker='x')
axes[0].set_ylabel("Acceleration Magnitude [m/s²]")
axes[0].legend()
axes[0].set_title("Acceleration Magnitude Over Time")

# Plot Pressure 1
axes[1].plot(time, pressure1, label="Pressure 1", color="g", alpha=0.7)
axes[1].scatter(time[filtered_peaks], pressure1[filtered_peaks], color='r', label="IDC", marker='x')
axes[1].set_ylabel("Pressure Sensor 1 [hPa]")
axes[1].legend()
axes[1].set_title("Pressure Sensor 1 Over Time")

# Plot Pressure 2
axes[2].plot(time, pressure2, label="Pressure 2", color="orange", alpha=0.7)
axes[2].scatter(time[filtered_peaks], pressure2[filtered_peaks], color='r', label="IDC", marker='x')
axes[2].set_xlabel("Time [seconds]")
axes[2].set_ylabel("Pressure Sensor 2 [hPa]")
axes[2].legend()
axes[2].set_title("Pressure Sensor 2 Over Time")

# Adjust layout
plt.tight_layout()
plt.show()
