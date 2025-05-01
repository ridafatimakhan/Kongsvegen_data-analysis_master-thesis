import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="darkgrid")

file_path = 'H:/Rida/Svalbard_data/Screened_data/18072021/M24/M24-0718173840.txt/filtered_pressure1.txt'
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# rotation matrix
R_body_to_global = np.array([
    [0, 1, 0],
    [-1, 0, 0],
    [0, 0, -1]
])

data_file = pd.read_csv(
    file_path,
    names=column_names,
    delimiter='\t',
    header=None,
    na_values=['', ' '],
    engine='python',
    usecols=range(17),
    on_bad_lines='skip',
    skiprows=1
)

data_file.replace('�', pd.NA, inplace=True)  # clean invalid values
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# Convert time to seconds and minutes
t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

# Drop rows with NaNs in critical columns
data_file.dropna(subset=['accx', 'accy', 'accz'], inplace=True)

# Function to rotate acceleration data into global frame
def rotate_acceleration(accx, accy, accz, R_body_to_global):
    acc_body = np.array([accx, accy, accz])  # original body-frame
    acc_global = R_body_to_global @ acc_body
    return acc_global

# Applying the rotation to the acceleration data in the DataFrame
data_file[['X_forward', 'Y_lateral', 'Z_upward']] = data_file.apply(
    lambda row: rotate_acceleration(row['accx'], row['accy'], row['accz'], R_body_to_global), axis=1, result_type="expand"
)

# Kalman filter
def kalman_filter(accel_data, process_variance, measurement_variance, initial_state=0, initial_covariance=1):
    x = initial_state
    P = initial_covariance
    filtered_data = []

    for z in accel_data:
        x_pred = x
        P_pred = P + process_variance
        K = P_pred / (P_pred + measurement_variance)
        x = x_pred + K * (z - x_pred)
        P = (1 - K) * P_pred
        filtered_data.append(x)
    
    return np.array(filtered_data)

# Example global acceleration data
accel_data_x = data_file['X_forward'].values
accel_data_y = data_file['Y_lateral'].values
accel_data_z = data_file['Z_upward'].values

# Apply Kalman filter
process_variance = 1e-4
measurement_variance = 0.05
filtered_accel_x = kalman_filter(accel_data_x, process_variance, measurement_variance)
filtered_accel_y = kalman_filter(accel_data_y, process_variance, measurement_variance)
filtered_accel_z = kalman_filter(accel_data_z, process_variance, measurement_variance)

# Compute rolling variance for filtered_accel_x
window_size = 100  # Rolling window size
rolling_variance = pd.Series(filtered_accel_x).rolling(window=window_size).var()

# Identify regions where rolling variance is below threshold (e.g., 10% of the maximum variance)
variance_threshold = 0.01 * rolling_variance.max()
flat_regions = rolling_variance[rolling_variance < variance_threshold]

# Adding a condition to check the duration of flat regions and mark if duration is greater than or equal to 1 second
time_threshold = 3 # 3 second duration for the flat region
hatch_regions = []

# Find the indices of the flat regions
start_idx = None
for i in range(1, len(flat_regions)):
    if flat_regions.index[i] - flat_regions.index[i-1] == 1:
        if start_idx is None:
            start_idx = flat_regions.index[i-1]
        if i == len(flat_regions) - 1:
            end_idx = flat_regions.index[i]
            duration = data_file['time_seconds'][end_idx] - data_file['time_seconds'][start_idx]
            if duration >= time_threshold:  # Only include if duration is >= 1 second
                hatch_regions.append((start_idx, end_idx))
    else:
        if start_idx is not None:
            end_idx = flat_regions.index[i-1]
            duration = data_file['time_seconds'][end_idx] - data_file['time_seconds'][start_idx]
            if duration >= time_threshold:  # Only include if duration is >= 1 second
                hatch_regions.append((start_idx, end_idx))
        start_idx = None

# Plotting with 3 subplots for X, Y, and Z acceleration
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12), sharex=True)

# Subplot 1: Acceleration X
ax1.plot(data_file['time_seconds'], accel_data_x, label='Forward acceleration (unfiltered)', color='blue', alpha=0.5)
ax1.plot(data_file['time_seconds'], filtered_accel_x, label='Forward acceleration (filtered)', color='black', alpha=0.8)
for start_idx, end_idx in hatch_regions:
    ax1.axvspan(data_file['time_seconds'][start_idx], data_file['time_seconds'][end_idx], color='gray', alpha=0.3, hatch='//')
ax1.set_ylabel('Acceleration X [$m/s^2$]' ,  fontsize=20)
#ax1.set_title('Filtered Acceleration X with Flat Regions (≥ 1 second)')
ax1.legend(loc='upper right' ,  fontsize=14)
ax1.tick_params(axis='both', labelsize=20)  # Increase tick label size

# Subplot 2: Acceleration Y
ax2.plot(data_file['time_seconds'], accel_data_y, label='Lateral acceleration (unfiltered)', color='purple', alpha=0.5)
ax2.plot(data_file['time_seconds'], filtered_accel_y, label='Lateral acceleration (filtered)', color='black', alpha=0.8)
for start_idx, end_idx in hatch_regions:
    ax2.axvspan(data_file['time_seconds'][start_idx], data_file['time_seconds'][end_idx], color='gray', alpha=0.3, hatch='//')
ax2.set_ylabel('Acceleration Y [$m/s^2$]',  fontsize=20)
#ax2.set_title('Filtered vs Unfiltered Acceleration Y')
ax2.legend(loc='upper right' ,  fontsize=14)
ax2.tick_params(axis='both', labelsize=20)  # Increase tick label size

# Subplot 3: Acceleration Z
ax3.plot(data_file['time_seconds'], accel_data_z, label='Upward acceleration (unfiltered)', color='teal', alpha=0.5)
ax3.plot(data_file['time_seconds'], filtered_accel_z, label='Upward acceleration (filtered)', color='black', alpha=0.8)
for start_idx, end_idx in hatch_regions:
    ax3.axvspan(data_file['time_seconds'][start_idx], data_file['time_seconds'][end_idx], color='gray', alpha=0.3, hatch='//')
ax3.set_xlabel('Time [seconds]',  fontsize=20)
ax3.set_ylabel('Acceleration Z [$m/s^2$]' ,  fontsize=20)
#ax3.set_title('Filtered vs Unfiltered Acceleration Z')
ax3.legend(loc='upper right' ,  fontsize=14)
ax3.tick_params(axis='both', labelsize=20)  # Increase tick label size

plt.tight_layout()
plt.show()


# Separate plot for pressure1 and pressure2
fig_pressure, ax_pressure = plt.subplots(figsize=(12, 4))

ax_pressure.plot(data_file['time_seconds'], data_file['pressure1'], label='Pressure 1', color='green')
ax_pressure.plot(data_file['time_seconds'], data_file['pressure2'], label='Pressure 2', color='orange')

# Add the same hatch regions from acceleration to pressure plot
for start_idx, end_idx in hatch_regions:
    ax_pressure.axvspan(
        data_file['time_seconds'][start_idx],
        data_file['time_seconds'][end_idx],
        color='gray',
        alpha=0.3,
        hatch='//'
    )
ax_pressure.set_xlabel('Time [seconds]',  fontsize=20)
ax_pressure.set_ylabel('Pressure [hPa]',  fontsize=20)
#ax_pressure.set_title('Pressure1 and Pressure2 over Time with Flat Acceleration Regions')
ax_pressure.tick_params(axis='both', labelsize=20)  # Adjust tick label size
ax_pressure.legend(loc='upper right',  fontsize=14)

plt.tight_layout()
plt.show()

# 1. Total number of frozen sensor events
num_frozen_events = len(hatch_regions)
print(f"Total number of times the sensor was frozen (flat regions): {num_frozen_events}")

# 2. Total time the sensor was frozen
total_frozen_time = sum(
    data_file['time_seconds'][end] - data_file['time_seconds'][start]
    for start, end in hatch_regions
)
print(f"Total time the sensor was frozen: {total_frozen_time:.2f} seconds")

# 3. Total deployment time
deployment_duration = data_file['time_seconds'].iloc[-1] - data_file['time_seconds'].iloc[0]
print(f"Total deployment time: {deployment_duration:.2f} seconds")




