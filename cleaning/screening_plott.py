import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")
input_file_path = 'H:/Rida/Dataset/13072021/M21/M210713161036.txt' # here define the path to the data file
output_directory = 'H:/Rida/new_data/13072021/M21/M210713161036.txt' # define the desired output directory
# here define column names for the dataset (first 17 columns)
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]
# read the data into a DataFrame 
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

# replacing invalid entries with NaN and convert columns to numeric
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# here convert 'time' to seconds and minutes based on the first timestamp
t_1 = data_file['time'].iloc[0]  # First time value
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001  # Convert to seconds
data_file['time_minutes'] = data_file['time_seconds'] / 60  # Convert to minutes

# calculate the rolling variance
window_size = 50  
data_file['rolling_variance1'] = data_file['pressure1'].rolling(window=window_size).var()
data_file['rolling_variance2'] = data_file['pressure2'].rolling(window=window_size).var()
k = 2  #multiplier for sensitivity

# threshold for pressure1 and pressure2
rolling_mean1 = data_file['rolling_variance1'].mean()
rolling_std1 = data_file['rolling_variance1'].std()
threshold1 = rolling_mean1 + k * rolling_std1

rolling_mean2 = data_file['rolling_variance2'].mean()
rolling_std2 = data_file['rolling_variance2'].std()
threshold2 = rolling_mean2 + k * rolling_std2

# here filtering the dataset to include only regions with high variance
roi_data1 = data_file[data_file['rolling_variance1'] > threshold1]
roi_data2 = data_file[data_file['rolling_variance2'] > threshold2]

# here function is defined to filter data based on ROI start and end times and save to a specified directory
def save_filtered_data(data_file, roi_data, time_column, output_directory, output_filename):
    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, output_filename)
    roi_data = roi_data.sort_values(by=time_column) # Sort ROI data by time

    # Get start and end times
    start_time = roi_data[time_column].iloc[0]
    end_time = roi_data[time_column].iloc[-1]
    filtered_data = data_file[(data_file[time_column] >= start_time) & (data_file[time_column] <= end_time)]
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
    delimiter='\t',  
    names=filtered_column_names,  
    header=0,  
    usecols=['time', 'pressure1', 'pressure2'],  
    na_values=['', ' '],  
    engine='python'
)

# reset time to start from zero in the filtered data
filtered_t0 = filtered_data['time'].iloc[0]
filtered_data['time_seconds'] = (filtered_data['time'] - filtered_t0) * 0.001
filtered_data['time_minutes'] = filtered_data['time_seconds'] / 60

# plots Pressure1 and Pressure2 over time
plt.figure(figsize=(12, 6))
plt.plot(filtered_data['time_seconds'], filtered_data['pressure1'], label='Filtered Pressure 1', color='blue')
plt.plot(filtered_data['time_seconds'], filtered_data['pressure2'], label='Filtered Pressure 2', color='orange')

# add labels, legend, and title
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
plt.show()

# Check if the plot has values less than 5 minutes
if filtered_data['time_minutes'].max() < 5:
    print("The plot has no values beyond 5 minutes. It is considered useless.")
else:
    print("The plot contains sufficient data for analysis.")

print("Data processing and visualization complete.")



