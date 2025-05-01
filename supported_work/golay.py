import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import savgol_filter

# Set Seaborn style for better plots
sns.set(style="darkgrid")

# File paths
input_file_path = 'H:/Rida/new/13072021/M18/M180713151102/filtered_pressure1.txt'
output_directory = 'H:/Rida/new/outlier_removed/M18/M180713151102'
os.makedirs(output_directory, exist_ok=True)

# Column names
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz',
    'time_seconds', 'time_minutes', 'rolling_variance1', 'rolling_variance2'
]

# Read file
data_file = pd.read_csv(
    input_file_path,
    delimiter='\t',
    names=column_names,
    header=0,
    usecols=range(17),  # Load only the first 17 columns
    na_values=['', ' '],
    engine='python'
)

# Convert time
t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

# --- Outlier Removal using IQR ---
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.10)
    Q3 = df[column].quantile(0.90)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

data_file_cleaned = remove_outliers(data_file, 'pressure1')
data_file_cleaned = remove_outliers(data_file_cleaned, 'pressure2')

# --- Apply Savitzky-Golay Filter ---
window_length = 101  # Must be odd and < total rows
polyorder = 2

if len(data_file_cleaned) > window_length:
    data_file_cleaned['pressure1_smooth'] = savgol_filter(data_file_cleaned['pressure1'], window_length, polyorder)
    data_file_cleaned['pressure2_smooth'] = savgol_filter(data_file_cleaned['pressure2'], window_length, polyorder)
else:
    print("Warning: Not enough data to apply Savitzky-Golay filter.")

# --- Save cleaned data ---
output_file_path = os.path.join(output_directory, 'filtered_pressure_cleaned.txt')
data_file_cleaned.to_csv(output_file_path, index=False, sep=',')

# --- Plotting ---
plt.figure(figsize=(10, 6))
plt.plot(data_file_cleaned['time_minutes'], data_file_cleaned['pressure1_smooth'], label='Smoothed Pressure1', color='blue')
plt.plot(data_file_cleaned['time_minutes'], data_file_cleaned['pressure2_smooth'], label='Smoothed Pressure2', color='orange')
plt.title('Pressure Over Time (Smoothed & Cleaned Data)', fontsize=14)
plt.xlabel('Time (minutes)', fontsize=12)
plt.ylabel('Pressure (hPa)', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.legend()
plt.grid(True)

# Save plot
plot_file_path = os.path.join(output_directory, 'pressure_plot_smoothed.png')
plt.savefig(plot_file_path)
plt.show()

print(f" Cleaned data saved to: {output_file_path}")
print(f" Plot saved to: {plot_file_path}")
