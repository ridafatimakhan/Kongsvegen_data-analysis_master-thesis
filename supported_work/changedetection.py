import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")
file_path = 'H:/Rida/outlier_removed/13072021/M15/M150713160801/filtered_pressure_cleaned.txt'

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

# Define time intervals (every 2.5 seconds)
bin_size = 2.5
time_bins = np.arange(0, max(time) + bin_size, bin_size)
sensor_data_file['time_bin'] = pd.cut(sensor_data_file['time_seconds'], bins=time_bins, labels=time_bins[:-1])

# Compute average pressure in each time bin
avg_pressure1 = sensor_data_file.groupby('time_bin')['pressure1'].mean().reset_index()
avg_pressure2 = sensor_data_file.groupby('time_bin')['pressure2'].mean().reset_index()

# Compute difference in consecutive averages
diff_pressure1 = avg_pressure1['pressure1'].diff()
diff_pressure2 = avg_pressure2['pressure2'].diff()

# Identify steps (positive changes) and edges (negative changes)
steps1 = avg_pressure1.iloc[1:][diff_pressure1[1:] > 3]
edges1 = avg_pressure1.iloc[1:][diff_pressure1[1:] < -3]
steps2 = avg_pressure2.iloc[1:][diff_pressure2[1:] > 3]
edges2 = avg_pressure2.iloc[1:][diff_pressure2[1:] < -3]

# Plotting
fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharex=True)

# First subplot: Averaged pressure1 vs. time with marked steps and edges
axes[0, 0].plot(avg_pressure1['time_bin'], avg_pressure1['pressure1'], label='Avg Pressure1', color='b')
axes[0, 0].scatter(steps1['time_bin'], steps1['pressure1'], color='g', marker='^', label='Step', zorder=3)
axes[0, 0].scatter(edges1['time_bin'], edges1['pressure1'], color='m', marker='v', label='Edge', zorder=3)
axes[0, 0].set_ylabel('Averaged Pressure1')
axes[0, 0].set_title('Averaged Pressure1 Over Time (2.5s Interval)')
axes[0, 0].legend()

# Second subplot: Averaged pressure2 vs. time with marked steps and edges
axes[0, 1].plot(avg_pressure2['time_bin'], avg_pressure2['pressure2'], label='Avg Pressure2', color='b')
axes[0, 1].scatter(steps2['time_bin'], steps2['pressure2'], color='g', marker='^', label='Step', zorder=3)
axes[0, 1].scatter(edges2['time_bin'], edges2['pressure2'], color='m', marker='v', label='Edge', zorder=3)
axes[0, 1].set_ylabel('Averaged Pressure2')
axes[0, 1].set_title('Averaged Pressure2 Over Time (2.5s Interval)')
axes[0, 1].legend()

# Third subplot: Raw pressure1 with steps and edges
axes[1, 0].plot(time, pressure1, label='Pressure1', color='g', alpha=0.6)
axes[1, 0].scatter(steps1['time_bin'], steps1['pressure1'], color='g', marker='^', label='Step', zorder=3)
axes[1, 0].scatter(edges1['time_bin'], edges1['pressure1'], color='m', marker='v', label='Edge', zorder=3)
axes[1, 0].set_ylabel('Pressure1')
axes[1, 0].set_title('Pressure1 Over Time')
axes[1, 0].legend()

# Fourth subplot: Raw pressure2 with steps and edges
axes[1, 1].plot(time, pressure2, label='Pressure2', color='r', alpha=0.6)
axes[1, 1].scatter(steps2['time_bin'], steps2['pressure2'], color='g', marker='^', label='Step', zorder=3)
axes[1, 1].scatter(edges2['time_bin'], edges2['pressure2'], color='m', marker='v', label='Edge', zorder=3)
axes[1, 1].set_ylabel('Pressure2')
axes[1, 1].set_title('Pressure2 Over Time')
axes[1, 1].legend()

# Fifth subplot: Acceleration magnitude over time
axes[2, 0].plot(time, acc_magnitude, label='Acceleration Magnitude', color='c')
axes[2, 0].set_xlabel('Time (seconds)')
axes[2, 0].set_ylabel('Acceleration Magnitude')
axes[2, 0].set_title('Acceleration Magnitude Over Time')
axes[2, 0].legend()

# Remove empty subplot (bottom-right corner)
fig.delaxes(axes[2, 1])

plt.tight_layout()
plt.show()
