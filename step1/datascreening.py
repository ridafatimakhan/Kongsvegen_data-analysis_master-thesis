import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
file_path = 'H:/Rida/13072021/M16/M160713160519.txt'
# Define the desired output directory
output_directory ='H:/Rida/filtered/13072021/M16/M160713160519.txt'
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
    file_path,
    names=column_names,
    delimiter=',',
    header=None,
    na_values=['', ' '],  # Treat empty strings as NaN
    engine='python',
    usecols=range(17),  # Use only the first 17 columns
    on_bad_lines='skip'  # Skip lines with too many fields
)

# Replace invalid entries with NaN and convert columns to numeric
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# Convert 'time' to seconds and minutes based on the teacher's hint
t_1 = data_file['time'].iloc[0]  # First time value
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001  # Convert to seconds
data_file['time_minutes'] = data_file['time_seconds'] / 60  # Convert to minutes

# Calculate the rolling variance
window_size = 50  # Define the rolling window size
data_file['rolling_variance1'] = data_file['pressure1'].rolling(window=window_size).var()
data_file['rolling_variance2'] = data_file['pressure2'].rolling(window=window_size).var()

# Define a threshold for variance
k = 1  # Multiplier for sensitivity

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

# Display some basic info about the saved files
print("Data processing complete. Filtered files saved successfully!")
