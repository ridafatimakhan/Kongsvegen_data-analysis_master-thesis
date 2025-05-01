# Import required libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from hmmlearn import hmm
from pykalman import KalmanFilter

# File path and initial setup
sns.set(style="darkgrid")
file_path = 'H:/Rida/Svalbard_data/outlier_removed/18.07.2021/M08/M08-0718173755/filtered_pressure_cleaned.txt'
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]
R_body_to_global = np.array([
    [0, 1, 0],
    [-1, 0, 0],
    [0, 0, -1]
])

# Load data
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
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# Convert time to seconds and minutes
t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

# Drop rows with NaNs in critical columns
data_file.dropna(subset=['accx', 'accy', 'accz'], inplace=True)
# print([col.strip() for col in data_file.columns])

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

# Store filtered values in DataFrame
data_file['filtered_X'] = filtered_accel_x
data_file['filtered_Y'] = filtered_accel_y
data_file['filtered_Z'] = filtered_accel_z

# Feature engineering for HMM
window_size = 5
rolling_std = data_file['filtered_X'].rolling(window=window_size).std()
pressure_mean = data_file[['pressure1', 'pressure2']].mean(axis=1)
pressure_rolling_std = pressure_mean.rolling(window=window_size).std()
features = pd.concat([rolling_std, pressure_rolling_std], axis=1).dropna()
features.columns = ['acc_x_std', 'pressure_std']

# HMM model
model = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=10, random_state=42)
model.fit(features)
hidden_states = model.predict(features)

# Align predictions with original dat
data_file['HMM_state'] = np.nan
data_file.loc[features.index, 'HMM_state'] = hidden_states
data_file['HMM_state'].ffill(inplace=True)

# Identify stall (assumed to be state with lower acc std)
# The model learns the hidden states from the data — it labels them internally as 0 and 1.
stall_state = model.means_[:, 0].argmin()
stall_mask = data_file['HMM_state'] == stall_state

# Find stall regions longer than 3 seconds
hatch_regions = []
start_idx = None
for i in range(len(data_file)):
    if stall_mask.iloc[i]:
        if start_idx is None:
            start_idx = i
    else:
        if start_idx is not None:
            end_idx = i - 1
            duration = data_file['time_seconds'].iloc[end_idx] - data_file['time_seconds'].iloc[start_idx]
            if duration >= 3:
                hatch_regions.append((start_idx, end_idx))
            start_idx = None

stall_count = len(hatch_regions)
stall_duration = sum(data_file['time_seconds'].iloc[end] - data_file['time_seconds'].iloc[start] for start, end in hatch_regions)
deployment_duration = data_file['time_seconds'].iloc[-1] - data_file['time_seconds'].iloc[0]

stall_count, stall_duration, deployment_duration

# Plotting accelerations (accx, accy, accz) and pressure data with stall regions
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), sharex=True)

# Plot X acceleration
ax1.plot(data_file['time_seconds'], data_file['X_forward'], label='Original Acc X', color='gray', linestyle='--')
ax1.plot(data_file['time_seconds'], data_file['filtered_X'], label='Filtered Acc X', color='black', linewidth=1.5)
for start, end in hatch_regions:
    ax1.axvspan(data_file['time_seconds'].iloc[start], data_file['time_seconds'].iloc[end], color='red', alpha=0.3, hatch='//')
ax1.set_ylabel('Accel X [$m/s^2$]', fontsize=18)
ax1.legend(loc='upper right', fontsize=14)

# Plot Y acceleration
ax2.plot(data_file['time_seconds'], data_file['Y_lateral'], label='Original Acc Y', color='gray', linestyle='--')
ax2.plot(data_file['time_seconds'], data_file['filtered_Y'], label='Filtered Acc Y', color='black', linewidth=1.5)
for start, end in hatch_regions:
    ax2.axvspan(data_file['time_seconds'].iloc[start], data_file['time_seconds'].iloc[end], color='red', alpha=0.3, hatch='//')
ax2.set_ylabel('Accel Y [$m/s^2$]', fontsize=18)
ax2.legend(loc='upper right', fontsize=14)

# Plot Z acceleration
ax3.plot(data_file['time_seconds'], data_file['Z_upward'], label='Original Acc Z', color='gray', linestyle='--')
ax3.plot(data_file['time_seconds'], data_file['filtered_Z'], label='Filtered Acc Z', color='black', linewidth=1.5)
for start, end in hatch_regions:
    ax3.axvspan(data_file['time_seconds'].iloc[start], data_file['time_seconds'].iloc[end], color='red', alpha=0.3, hatch='//')
ax3.set_xlabel('Time [seconds]', fontsize=18)
ax3.set_ylabel('Accel Z [$m/s^2$]', fontsize=18)
ax3.legend(loc='upper right', fontsize=14)

# Plot pressure data
ax4.plot(data_file['time_seconds'], data_file['pressure1'], label='Pressure 1', color='green')
ax4.plot(data_file['time_seconds'], data_file['pressure2'], label='Pressure 2', color='orange')
for start, end in hatch_regions:
    ax4.axvspan(data_file['time_seconds'].iloc[start], data_file['time_seconds'].iloc[end], color='red', alpha=0.3, hatch='//')
ax4.set_xlabel('Time [seconds]', fontsize=18)
ax4.set_ylabel('Pressure [hPa]', fontsize=18)
ax4.legend(loc='upper right', fontsize=14)

plt.tight_layout()
plt.show()


# Print total number of stalls
print(f"Total number of stalls: {stall_count}")
print(f"Total stall duration: {stall_duration:.2f} seconds")
print(f"Total deployment duration: {deployment_duration:.2f} seconds")



# print(data_file.columns)
# print(data_file[['time', 'filtered_X', 'filtered_Y', 'filtered_Z', 'pressure1', 'pressure2']].head(10))






