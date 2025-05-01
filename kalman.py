import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.spatial.transform import Rotation as R

# Configure Seaborn for better aesthetics
sns.set(style="darkgrid")

# Define file paths
file_path = 'H:/Rida/outlier_removed/13.07.2021/M16/M160713160519/filtered_pressure_cleaned.txt'
output_directory = 'H:/Rida/kalman/M16/'

# Column names
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# Read the data
data_file = pd.read_csv(
    file_path,
    names=column_names,
    delimiter=',',
    header=None,
    na_values=['', ' '],
    engine='python',
    usecols=range(17),
    on_bad_lines='skip'
)

# Clean invalid values
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# Convert time to seconds and minutes
t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

# Drop rows with NaNs in critical columns
data_file.dropna(subset=['accx', 'accy', 'accz', 'gyx', 'gyy', 'gyz'], inplace=True)

# Reorient IMU data to world frame (x=lateral, y=forward, z=down → ENU: y, x, -z)
acc_local = data_file[['accx', 'accy', 'accz']].to_numpy()
acc_world = np.stack((acc_local[:,1], acc_local[:,0], -acc_local[:,2]), axis=-1)

gyro_local = data_file[['gyx', 'gyy', 'gyz']].to_numpy()
gyro_world = np.stack((gyro_local[:,1], gyro_local[:,0], -gyro_local[:,2]), axis=-1)

time = data_file['time_seconds'].to_numpy()
dt = np.mean(np.diff(time))

# Initialize orientation
orientation_quat = np.array([1.0, 0.0, 0.0, 0.0])
global_acc_list = []
z_rotation_list = []
z_acceleration_list = []

# Orientation estimation
for i in range(len(acc_world)):
    acc_sample = acc_world[i]
    gyro_sample = gyro_world[i]

    omega = gyro_sample
    theta = np.linalg.norm(omega * dt)
    if theta != 0:
        axis = omega / np.linalg.norm(omega)
        delta_q = R.from_rotvec(axis * theta).as_quat()
    else:
        delta_q = np.array([0, 0, 0, 1])  # No rotation

    # Update orientation
    current_rot = R.from_quat(orientation_quat)
    delta_rot = R.from_quat(delta_q)
    updated_rot = current_rot * delta_rot
    orientation_quat = updated_rot.as_quat()

    # Extract Z-axis rotation (yaw)
    euler_angles = updated_rot.as_euler('xyz', degrees=True)
    yaw = euler_angles[2]  # Z-axis rotation
    z_rotation_list.append(yaw)

    # Convert to global acceleration
    R_matrix = updated_rot.as_matrix()
    acc_global = R_matrix @ acc_sample - np.array([0, 0, 9.81])  # gravity-compensated
    global_acc_list.append(acc_global)

    # Store Z-axis acceleration (vertical component)
    z_acceleration_list.append(acc_global[0])  # Extracting the Z-axis (vertical) component of acceleration

global_acc = np.array(global_acc_list)
z_rotation = np.array(z_rotation_list)
z_acceleration = np.array(z_acceleration_list)
time_minutes = data_file['time_minutes'].to_numpy()

# Plot Z-axis rotation (Yaw)
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(time_minutes, z_rotation, label='Yaw (Z-axis rotation)', color='teal')
plt.xlabel("Time (minutes)")
plt.ylabel("Yaw Angle (°)")
plt.title("Z-axis (Yaw) Rotation Over Time")
plt.legend()

# Plot Z-axis acceleration (Vertical acceleration)
plt.subplot(2, 1, 2)
plt.plot(time_minutes, z_acceleration, label='Z-axis acceleration (m/s²)', color='orange')
plt.xlabel("Time (minutes)")
plt.ylabel("Acceleration (m/s²)")
plt.title("Z-axis Acceleration (Vertical) Over Time")
plt.legend()

plt.tight_layout()
plt.show()
