import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="darkgrid")

file_path = 'H:/Rida/Svalbard_data/Screened_data/18072021/M04/M040718173701.txt/filtered_pressure1.txt'

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

# Read the data
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

data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

data_file.dropna(subset=['accx', 'accy', 'accz'], inplace=True)

# Rotation function
def rotate_acceleration(accx, accy, accz, R_body_to_global):
    acc_body = np.array([accx, accy, accz])
    acc_global = R_body_to_global @ acc_body
    return acc_global

# Apply rotation
data_file[['X_forward', 'Y_lateral', 'Z_upward']] = data_file.apply(
    lambda row: rotate_acceleration(row['accx'], row['accy'], row['accz'], R_body_to_global),
    axis=1, result_type="expand"
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

accel_data_x = data_file['X_forward'].values
accel_data_y = data_file['Y_lateral'].values
accel_data_z = data_file['Z_upward'].values

process_variance = 1e-4
measurement_variance = 0.05

filtered_accel_x = kalman_filter(accel_data_x, process_variance, measurement_variance)
filtered_accel_y = kalman_filter(accel_data_y, process_variance, measurement_variance)
filtered_accel_z = kalman_filter(accel_data_z, process_variance, measurement_variance)

# STEP DETECTION
norm_filtered_accel_z = (filtered_accel_z - np.mean(filtered_accel_z)) / np.std(filtered_accel_z)
Z_THRESHOLD = np.std(norm_filtered_accel_z) * 1.5
print(f"Z-Threshold: {Z_THRESHOLD:.2f}")
MIN_STEP_DURATION = 5

z_low = norm_filtered_accel_z < -Z_THRESHOLD
z_low_indices = np.where(z_low)[0]

steps = []
if len(z_low_indices) > 0:
    current_step = [z_low_indices[0]]
    for i in range(1, len(z_low_indices)):
        if z_low_indices[i] - z_low_indices[i-1] == 1:
            current_step.append(z_low_indices[i])
        else:
            if len(current_step) >= MIN_STEP_DURATION:
                steps.append((current_step[0], current_step[-1]))
            current_step = [z_low_indices[i]]
    if len(current_step) >= MIN_STEP_DURATION:
        steps.append((current_step[0], current_step[-1]))

# POOL DETECTION (Updated: sensor-specific STD)
WINDOW_SIZE = 2
MIN_REGION_DURATION = 0.001

def detect_high_pressure_regions_dual(pressure1, pressure2, time_seconds, 
                                      window_size=WINDOW_SIZE, 
                                      std_multiplier=3, 
                                      min_duration=MIN_REGION_DURATION):
    """
    Detects high-pressure regions using each sensor's own STD + median.
    """

    def _detect_single(pressure_data):
        smoothed = pd.Series(pressure_data).rolling(window=window_size, center=True).mean().values
        baseline = np.nanmedian(smoothed)
        std = np.nanstd(smoothed)
        dynamic_threshold = baseline + std_multiplier * std
        print(f"Sensor - Median pressure: {baseline:.2f}, STD: {std:.2f}, Threshold: {dynamic_threshold:.2f}")
        return smoothed > dynamic_threshold

    above_threshold_1 = _detect_single(pressure1)
    above_threshold_2 = _detect_single(pressure2)
    combined_threshold = above_threshold_1 | above_threshold_2


    regions = []
    in_region = False
    start_idx = 0

    for i in range(len(combined_threshold)):
        if combined_threshold[i] and not in_region:
            start_idx = i
            in_region = True
        elif not combined_threshold[i] and in_region:
            end_idx = i
            if (end_idx - start_idx) >= min_duration:
                regions.append((start_idx, end_idx))
            in_region = False

    if in_region and (len(combined_threshold) - start_idx) >= min_duration:
        regions.append((start_idx, len(combined_threshold) - 1))

    print(f"Detected {len(regions)} high-pressure regions.")
    return regions

# Detect high-pressure regions
pools = detect_high_pressure_regions_dual(
    data_file['pressure1'].values,
    data_file['pressure2'].values,
    data_file['time_seconds'].values
)

# Plotting
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

# Acceleration X
ax1.plot(data_file['time_seconds'], accel_data_x, label='Forward acceleration (unfiltered)', color='blue', alpha=0.5)
ax1.plot(data_file['time_seconds'], filtered_accel_x, label='Forward acceleration (filtered)', color='black', alpha=0.8)
for step_start, step_end in steps:
    ax1.axvspan(data_file['time_seconds'].iloc[step_start],
                data_file['time_seconds'].iloc[step_end],
                color='gray', alpha=0.3)
for pool_start, pool_end in pools:
    ax1.axvspan(data_file['time_seconds'].iloc[pool_start],
                data_file['time_seconds'].iloc[pool_end],
                color='red', alpha=1.0, hatch='\\\\')
ax1.set_ylabel('Acceleration X [$m/s^2$]', fontsize=18)
ax1.legend(loc='upper right', fontsize=18)
ax1.tick_params(axis='both', labelsize=18)

# Acceleration Y
ax2.plot(data_file['time_seconds'], accel_data_y, label='Lateral acceleration (unfiltered)', color='purple', alpha=0.5)
ax2.plot(data_file['time_seconds'], filtered_accel_y, label='Lateral acceleration (filtered)', color='black', alpha=0.8)
for step_start, step_end in steps:
    ax2.axvspan(data_file['time_seconds'].iloc[step_start],
                data_file['time_seconds'].iloc[step_end],
                color='gray', alpha=0.3)
for pool_start, pool_end in pools:
    ax2.axvspan(data_file['time_seconds'].iloc[pool_start],
                data_file['time_seconds'].iloc[pool_end],
                color='red', alpha=1.0, hatch='\\\\')
ax2.set_ylabel('Acceleration Y [$m/s^2$]', fontsize=18)
ax2.legend(loc='upper right', fontsize=18)
ax2.tick_params(axis='both', labelsize=18)

# Acceleration Z
ax3.plot(data_file['time_seconds'], accel_data_z, label='Upward acceleration (unfiltered)', color='teal', alpha=0.5)
ax3.plot(data_file['time_seconds'], filtered_accel_z, label='Upward acceleration (filtered)', color='black', alpha=0.8)
for step_start, step_end in steps:
    ax3.axvspan(data_file['time_seconds'].iloc[step_start],
                data_file['time_seconds'].iloc[step_end],
                color='gray', alpha=0.3)
for pool_start, pool_end in pools:
    ax3.axvspan(data_file['time_seconds'].iloc[pool_start],
                data_file['time_seconds'].iloc[pool_end],
                color='red', alpha=1.0, hatch='\\\\')
ax3.set_xlabel('Time [seconds]', fontsize=18)
ax3.set_ylabel('Acceleration Z [$m/s^2$]', fontsize=18)
ax3.legend(loc='upper right', fontsize=18)
ax3.tick_params(axis='both', labelsize=18)

# Pressure
ax4.plot(data_file['time_seconds'], data_file['pressure1'],
         label='Pressure 1', color='blue', alpha=0.8)
ax4.plot(data_file['time_seconds'], data_file['pressure2'],
         label='Pressure 2', color='green', alpha=0.8)
for step_start, step_end in steps:
    ax4.axvspan(data_file['time_seconds'].iloc[step_start],
                data_file['time_seconds'].iloc[step_end],
                color='gray', alpha=0.3)
for pool_start, pool_end in pools:
    ax4.axvspan(data_file['time_seconds'].iloc[pool_start],
                data_file['time_seconds'].iloc[pool_end],
                color='red', alpha=1.0, hatch='\\\\')
ax4.set_xlabel('Time [seconds]', fontsize=18)
ax4.set_ylabel('Pressure', fontsize=18)
ax4.legend(loc='upper right', fontsize=18)
ax4.tick_params(axis='both', labelsize=18)

plt.tight_layout()
# plt.savefig("output_plot.pdf", dpi=300)
plt.show()

# Print step timings
print(f"Detected {len(steps)} steps:")
for i, (start, end) in enumerate(steps):
    print(f"Step {i+1}: {data_file['time_seconds'].iloc[start]:.2f}s to {data_file['time_seconds'].iloc[end]:.2f}s")

# Print pool timings
print(f"\nDetected {len(pools)} pools:")
for i, (start, end) in enumerate(pools):
    print(f"Pool {i+1}: {data_file['time_seconds'].iloc[start]:.2f}s to {data_file['time_seconds'].iloc[end]:.2f}s")
    print(f"  Max pressure1: {data_file['pressure1'].iloc[start:end+1].max():.2f}")
    print(f"  Max pressure2: {data_file['pressure2'].iloc[start:end+1].max():.2f}")
