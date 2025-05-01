import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="darkgrid")

file_path = 'H:/Rida/Svalbard_data/Screened_data/18072021/M23/M23-0718144836.txt/filtered_pressure1.txt'

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


# Parameters
Z_THRESHOLD = 5  # Adjust to change sensitivity (lower = more sensitive)
MIN_STEP_DURATION = 5  # Minimum samples to count as a step

# Detect steps where filtered_accel_z < Z_THRESHOLD
z_low = filtered_accel_z < Z_THRESHOLD
z_low_indices = np.where(z_low)[0]

# Group consecutive low-Z periods (steps)
steps = []
if len(z_low_indices) > 0:
    current_step = [z_low_indices[0]]
    for i in range(1, len(z_low_indices)):
        if z_low_indices[i] - z_low_indices[i-1] == 1:  # Consecutive samples
            current_step.append(z_low_indices[i])
        else:
            if len(current_step) >= MIN_STEP_DURATION:
                steps.append((current_step[0], current_step[-1]))
            current_step = [z_low_indices[i]]
    # Add the last step if valid
    if len(current_step) >= MIN_STEP_DURATION:
        steps.append((current_step[0], current_step[-1]))


# Updated parameters for region detection
WINDOW_SIZE = 2          # Rolling window size (adjust based on sampling rate)
PRESSURE_THRESHOLD = 15   # Minimum pressure to consider as "high"
MIN_REGION_DURATION = 0.001  # Minimum consecutive samples to form a region

def detect_high_pressure_regions_dual(pressure1, pressure2, window_size=WINDOW_SIZE,
                                    threshold=PRESSURE_THRESHOLD, min_duration=MIN_REGION_DURATION):
    """Detects high-pressure regions in BOTH sensors and merges overlapping regions."""
    def _detect_single(pressure_data):
        # Calculate baseline and dynamic threshold
        baseline = np.mean(pressure_data)
        print(f"Mean pressure: {baseline}")  # Print the mean pressure
        dynamic_threshold = baseline + threshold

        # Smooth the data
        smoothed = pd.Series(pressure_data).rolling(window=window_size, center=True).mean().values

        # Find where pressure crosses threshold
        above_threshold = smoothed > dynamic_threshold

        # Detect regions
        regions = []
        in_region = False
        start_idx = 0

        for i in range(len(above_threshold)):
            if above_threshold[i] and not in_region:
                # Find where the rise begins (look backward to baseline)
                look_back = max(0, i - window_size * 2)
                for j in range(i, look_back, -1):
                    if smoothed[j] <= baseline:
                        start_idx = j
                        break
                else:
                    start_idx = i
                in_region = True

            elif not above_threshold[i] and in_region:
                # Find where pressure returns to baseline (look forward)
                look_forward = min(len(smoothed), i + window_size * 2)
                for j in range(i, look_forward):
                    if smoothed[j] <= baseline:
                        end_idx = j
                        break
                else:
                    end_idx = i

                if (end_idx - start_idx) >= min_duration:
                    regions.append((start_idx, end_idx))
                in_region = False

        # Handle region continuing to end of data
        if in_region and (len(smoothed) - start_idx) >= min_duration:
            look_back = max(0, len(smoothed) - window_size * 2)
            for j in range(len(smoothed)-1, look_back, -1):
                if smoothed[j] <= baseline:
                    end_idx = j
                    break
            else:
                end_idx = len(smoothed)
            regions.append((start_idx, end_idx))

        return regions

    # Detect regions in both sensors
    regions1 = _detect_single(pressure1)
    regions2 = _detect_single(pressure2)

    # Combine and merge overlapping regions
    all_regions = regions1 + regions2
    all_regions.sort()

    pools = []
    if all_regions:
        current_start, current_end = all_regions[0]
        for start, end in all_regions[1:]:
            if start <= current_end + window_size:  # Merge if regions are close
                current_end = max(current_end, end)
            else:
                pools.append((current_start, current_end))
                current_start, current_end = start, end
        pools.append((current_start, current_end))

    return pools

# Detect high-pressure regions (now using the dual-sensor function)
pools = detect_high_pressure_regions_dual(
    data_file['pressure1'].values,
    data_file['pressure2'].values
)


# Plotting
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

# Acceleration X
ax1.plot(data_file['time_seconds'], accel_data_x, label='Forward acceleration (unfiltered)', color='blue', alpha=0.5)
ax1.plot(data_file['time_seconds'], filtered_accel_x, label='Forward acceleration (filtered)', color='black', alpha=0.8)
for step_start, step_end in steps:
    ax1.axvspan(data_file['time_seconds'].iloc[step_start],
                data_file['time_seconds'].iloc[step_end],
                color='gray', alpha=0.3) #, hatch='//'
for pool_start, pool_end in pools:
    ax1.axvspan(data_file['time_seconds'].iloc[pool_start],
                   data_file['time_seconds'].iloc[pool_end],
                   color='red', alpha=1.0, hatch='\\\\')
ax1.set_ylabel('Acceleration X [$m/s^2$]', fontsize=14)
ax1.legend(loc='upper right', fontsize=14)
ax1.tick_params(axis='both', labelsize=14)

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
ax2.set_ylabel('Acceleration Y [$m/s^2$]', fontsize=14)
ax2.legend(loc='upper right', fontsize=14)
ax2.tick_params(axis='both', labelsize=14)

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
ax3.set_xlabel('Time [seconds]', fontsize=14)
ax3.set_ylabel('Acceleration Z [$m/s^2$]', fontsize=14)
ax3.legend(loc='upper right', fontsize=14)
ax3.tick_params(axis='both', labelsize=14)

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

ax4.set_xlabel('Time [seconds]', fontsize=14)
ax4.set_ylabel('Pressure', fontsize=14)
ax4.legend(loc='upper right', fontsize=14)
ax4.tick_params(axis='both', labelsize=14)

plt.tight_layout()
plt.show()

# Print step timings
print(f"Detected {len(steps)} steps:")
for i, (start, end) in enumerate(steps):
    print(f"Step {i+1}: {data_file['time_seconds'].iloc[start]:.2f}s to {data_file['time_seconds'].iloc[end]:.2f}s")

# Print step timings
print(f"Detected {len(pools)} pools:")
for i, (start, end) in enumerate(pools):
    print(f"Pool {i+1}: {data_file['time_seconds'].iloc[start]:.2f}s to {data_file['time_seconds'].iloc[end]:.2f}s")
