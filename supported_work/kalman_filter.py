import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="darkgrid")
file_path = 'H:/Rida/outlier_removed/18.07.2021/M04/M040718173701/filtered_pressure_cleaned.txt'
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# rotation matrix
# (90-degree rotation around Z-axis with flip on Z)
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
    skiprows=1  # This will skip the first row
)

data_file.replace('�', pd.NA, inplace=True) # clean invalid values
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# here this convert time to seconds and minutes
t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

# this drop rows with NaNs in critical columns
data_file.dropna(subset=['accx', 'accy', 'accz'], inplace=True)

# function to rotate acceleration data into global frame
def rotate_acceleration(accx, accy, accz, R_body_to_global):
    acc_body = np.array([accx, accy, accz])  # original body-frame
    acc_global = R_body_to_global @ acc_body
    return acc_global

# applying the rotation to the acceleration data in the DataFrame
data_file[['X_forward', 'Y_lateral', 'Z_upward']] = data_file.apply(
    lambda row: rotate_acceleration(row['accx'], row['accy'], row['accz'], R_body_to_global), axis=1, result_type="expand"
)


def kalman_filter(accel_data, process_variance, measurement_variance, initial_state=0, initial_covariance=1):
    # initialize state and covariance
    x = initial_state
    P = initial_covariance
    filtered_data = []

    # Kalman filter loop
    for z in accel_data:
        # prediction step (no change in state model here, assume constant acceleration)
        x_pred = x
        P_pred = P + process_variance

        # update step
        K = P_pred / (P_pred + measurement_variance)  # Kalman gain
        x = x_pred + K * (z - x_pred)  # update the state estimate
        P = (1 - K) * P_pred  # update the covariance

        # storing filtered result
        filtered_data.append(x)
    
    return np.array(filtered_data)

# example global acceleration data (X_forward, Y_lateral, Z_upward)
accel_data_x = data_file['X_forward'].values
accel_data_y = data_file['Y_lateral'].values
accel_data_z = data_file['Z_upward'].values

# defining process and measurement variances (these are tuning parameters)
process_variance = 1e-4  # assumed process variance (system noise)
measurement_variance = 0.05  # assumed measurement variance (sensor noise)

# apply Kalman filter to the X_forward, Y_lateral, Z_upward data
filtered_accel_x = kalman_filter(accel_data_x, process_variance, measurement_variance)
filtered_accel_y = kalman_filter(accel_data_y, process_variance, measurement_variance)
filtered_accel_z = kalman_filter(accel_data_z, process_variance, measurement_variance)

fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True, sharey=False)

# X_forward (Global Lateral Acceleration)
axes[0].plot(data_file['time_minutes'], accel_data_x, label='Original X_forward', color='tab:blue', alpha=0.5)
axes[0].plot(data_file['time_minutes'], filtered_accel_x, label='Forward acceleration (x_kalman)', color='tab:orange')
axes[0].set_ylabel('Acceleration (m/s^2)')
#axes[0].set_title('Kalman Filter Applied to X_forward Acceleration')
axes[0].legend()

# Y_lateral (Global Forward Acceleration)
axes[1].plot(data_file['time_minutes'], accel_data_y, label='Original Y_lateral', color='tab:green', alpha=0.5)
axes[1].plot(data_file['time_minutes'], filtered_accel_y, label='Lateral acceleration (y_kalman)', color='tab:red')
axes[1].set_ylabel('Acceleration (m/s^2)')
#axes[1].set_title('Kalman Filter Applied to Y_lateral Acceleration')
axes[1].legend()

# Z_upward (Global Downward Acceleration)
axes[2].plot(data_file['time_minutes'], accel_data_z, label='Original Z_upward', color='tab:purple', alpha=0.5)
axes[2].plot(data_file['time_minutes'], filtered_accel_z, label='Upward acceleration (z_kalman)', color='tab:brown')
axes[2].set_xlabel('Time (minutes)')
axes[2].set_ylabel('Acceleration (m/s^2)')
#axes[2].set_title('Kalman Filter Applied to Z_upward Acceleration')
axes[2].legend()
plt.tight_layout()
plt.show()

