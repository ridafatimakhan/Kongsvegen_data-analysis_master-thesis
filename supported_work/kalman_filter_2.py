import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import correlate

sns.set(style="darkgrid")

file_path = 'H:/Rida/outlier_removed/15.07.2021/M16/M160715161745/filtered_pressure_cleaned.txt'
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# Rotation matrix
R_body_to_global = np.array([
    [0, 1, 0],
    [-1, 0, 0],
    [0, 0, -1]
])

data_file = pd.read_csv(
    file_path,
    names=column_names,
    delimiter=',',
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

# Rotate acceleration data into global frame
def rotate_acceleration(accx, accy, accz, R_body_to_global):
    acc_body = np.array([accx, accy, accz])
    acc_global = R_body_to_global @ acc_body
    return acc_global

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

# Apply Kalman filter to acceleration data
process_variance = 1e-4
measurement_variance = 0.05
filtered_accel_x = kalman_filter(data_file['X_forward'].values, process_variance, measurement_variance)
filtered_accel_y = kalman_filter(data_file['Y_lateral'].values, process_variance, measurement_variance)
filtered_accel_z = kalman_filter(data_file['Z_upward'].values, process_variance, measurement_variance)

# Compute rolling variance for filtered_accel_x
window_size = 100
rolling_variance = pd.Series(filtered_accel_x).rolling(window=window_size).var()

# Identify flat regions (low variance and at least 1 sec duration)
variance_threshold = 0.01 * rolling_variance.max()
flat_regions = rolling_variance[rolling_variance < variance_threshold]
time_threshold = 1
hatch_regions = []

start_idx = None
for i in range(1, len(flat_regions)):
    if flat_regions.index[i] - flat_regions.index[i-1] == 1:
        if start_idx is None:
            start_idx = flat_regions.index[i-1]
        if i == len(flat_regions) - 1:
            end_idx = flat_regions.index[i]
            duration = data_file['time_seconds'][end_idx] - data_file['time_seconds'][start_idx]
            if duration >= time_threshold:
                hatch_regions.append((start_idx, end_idx))
    else:
        if start_idx is not None:
            end_idx = flat_regions.index[i-1]
            duration = data_file['time_seconds'][end_idx] - data_file['time_seconds'][start_idx]
            if duration >= time_threshold:
                hatch_regions.append((start_idx, end_idx))
        start_idx = None

# ======= TEMPLATE MATCHING FOR PRESSURE1 =======
template_start_time = 354.35
template_end_time = 359.40
template_indices = data_file[(data_file['time_seconds'] >= template_start_time) & 
                             (data_file['time_seconds'] <= template_end_time)].index
template = data_file.loc[template_indices, 'pressure1'].values
template_length = len(template)

# Normalize template and full signal
template_norm = (template - np.mean(template)) / np.std(template)
signal = data_file['pressure1'].values
signal_norm = (signal - np.mean(signal)) / np.std(signal)

# Cross-correlation
corr = correlate(signal_norm, template_norm, mode='valid')
corr_threshold = 0.8 * max(corr)
match_indices = np.where(corr > corr_threshold)[0]

# Remove overlapping/close matches
min_separation = int(template_length * 0.8)
filtered_matches = []
last_idx = -min_separation
for idx in match_indices:
    if idx - last_idx >= min_separation:
        filtered_matches.append(idx)
        last_idx = idx

# ======= PLOTTING =======
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Acceleration subplot
ax1.plot(data_file['time_seconds'], data_file['X_forward'], label='Forward accx (unfiltered)', color='blue', alpha=0.5)
ax1.plot(data_file['time_seconds'], filtered_accel_x, label='Forward accx (filtered)', color='black', alpha=0.8)
for start_idx, end_idx in hatch_regions:
    ax1.axvspan(data_file['time_seconds'][start_idx], data_file['time_seconds'][end_idx], color='red', alpha=0.3)
ax1.set_ylabel('Acceleration X')
ax1.set_title('Filtered Acceleration X with Flat Regions (≥ 1 second)')
ax1.legend(loc='upper right')

# Pressure subplot
ax2.plot(data_file['time_seconds'], data_file['pressure1'], label='Pressure 1', color='green')
ax2.plot(data_file['time_seconds'], data_file['pressure2'], label='Pressure 2', color='orange')

# Highlight template region
ax2.axvspan(template_start_time, template_end_time, color='black', alpha=0.2, hatch='xx', label='Template')

# Highlight matched regions using cross-correlation
for idx in filtered_matches:
    start_time = data_file['time_seconds'].iloc[idx]
    end_time = data_file['time_seconds'].iloc[min(idx + template_length, len(data_file) - 1)]
    ax2.axvspan(start_time, end_time, color='grey', alpha=0.3, hatch='//')

ax2.set_xlabel('Time (seconds)')
ax2.set_ylabel('Pressure (hPa)')
ax2.set_title('Pressure1 and Pressure2 with Matched Template Regions')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()
