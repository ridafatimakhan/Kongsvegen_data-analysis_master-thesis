import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")

# Define the path to the data file
input_file_path = 'H:/Rida/Dataset/13072021/M21/M210713161036.txt'

# Define the desired output directory
output_directory = 'H:/Rida/new_data/13072021/M21/M210713161036.txt'

# Define column names for the dataset (first 17 columns)
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# Read the data into a DataFrame (only the first 17 columns)
data_file = pd.read_csv(
    input_file_path,
    names=column_names,
    delimiter=',',
    header=None,
    na_values=['', ' '],  
    engine='python',
    usecols=range(17),  
    on_bad_lines='skip',
    encoding='ISO-8859-1'
)

# Replace invalid entries with NaN and convert columns to numeric
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# Convert 'time' to seconds and minutes based on the first timestamp
t_1 = data_file['time'].iloc[0]  # First time value
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001  # Convert to seconds
data_file['time_minutes'] = data_file['time_seconds'] / 60  # Convert to minutes

# Calculate the rolling variance
window_size = 50  # Define the rolling window size
data_file['rolling_variance1'] = data_file['pressure1'].rolling(window=window_size).var()
data_file['rolling_variance2'] = data_file['pressure2'].rolling(window=window_size).var()

# Define a threshold for variance
k = 2 # Multiplier for sensitivity

# Threshold for pressure1
rolling_mean1 = data_file['rolling_variance1'].mean()
rolling_std1 = data_file['rolling_variance1'].std()
threshold1 = rolling_mean1 + k * rolling_std1

# Threshold for pressure2
rolling_mean2 = data_file['rolling_variance2'].mean()
rolling_std2 = data_file['rolling_variance2'].std()
threshold2 = rolling_mean2 + k * rolling_std2

# Filter the dataset to include only regions with high variance
roi_data1 = data_file[data_file['rolling_variance1'] > threshold1]
roi_data2 = data_file[data_file['rolling_variance2'] > threshold2]

# Function to filter data based on ROI start and end times and save to a specified directory
def save_filtered_data(data_file, roi_data, time_column, output_directory, output_filename):
    # Ensure the directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Construct the full output file path
    output_file = os.path.join(output_directory, output_filename)

    # Ensure ROI data is sorted by time
    roi_data = roi_data.sort_values(by=time_column)

    # Get start and end times
    start_time = roi_data[time_column].iloc[0]
    end_time = roi_data[time_column].iloc[-1]

    # Filter original data within the time range
    filtered_data = data_file[(data_file[time_column] >= start_time) & (data_file[time_column] <= end_time)]

    # Save filtered data to a .txt file
    filtered_data.to_csv(output_file, index=False, sep='\t')  # Save as tab-separated values
    print(f"Filtered data saved to {output_file}")

# Save data filtered by ROI for pressure1
save_filtered_data(data_file, roi_data1, 'time', output_directory, 'filtered_pressure1.txt')

# Save data filtered by ROI for pressure2
save_filtered_data(data_file, roi_data2, 'time', output_directory, 'filtered_pressure2.txt')

# Plot filtered pressure data
filtered_file_path = os.path.join(output_directory, 'filtered_pressure1.txt')

# Define column names for the filtered dataset
filtered_column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz',
    'time_seconds', 'time_minutes', 'rolling_variance1', 'rolling_variance2'
]

# Read the filtered data into a DataFrame
filtered_data = pd.read_csv(
    filtered_file_path,
    delimiter='\t',  # Use tab as the delimiter
    names=filtered_column_names,  # Assign column names
    header=0,  # Use the first row as the header
    usecols=['time', 'pressure1', 'pressure2'],  # Load only necessary columns
    na_values=['', ' '],  # Treat empty strings as NaN
    engine='python'
)

# Reset time to start from zero in the filtered data
filtered_t0 = filtered_data['time'].iloc[0]
filtered_data['time_seconds'] = (filtered_data['time'] - filtered_t0) * 0.001
filtered_data['time_minutes'] = filtered_data['time_seconds'] / 60

# Plot Pressure1 and Pressure2 over time
plt.figure(figsize=(12, 6))
plt.plot(filtered_data['time_seconds'], filtered_data['pressure1'], label='Filtered Pressure 1', color='blue')
plt.plot(filtered_data['time_seconds'], filtered_data['pressure2'], label='Filtered Pressure 2', color='orange')

# Add labels, legend, and title
plt.xlabel('Time [seconds]', fontsize=16)
plt.ylabel('Pressure [hPa]', fontsize=16)
plt.legend(fontsize=14)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# Save the plot
plot_output_file = os.path.join(output_directory, 'cutout_pressure_plot.png')
os.makedirs(output_directory, exist_ok=True)
plt.savefig(plot_output_file, dpi=300, bbox_inches='tight')
print(f"Plot saved to: {plot_output_file}")

# Display the plot
#plt.show()

# Check if the plot has values less than 5 minutes
if filtered_data['time_minutes'].max() < 5:
    print("The plot has no values beyond 5 minutes. It is considered useless.")
else:
    print("The plot contains sufficient data for analysis.")

print("Data processing and visualization complete.")



