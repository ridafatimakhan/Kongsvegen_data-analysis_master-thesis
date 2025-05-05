import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")
file_path = 'H:/Rida/13072021/M16/M160713160519.txt'
output_directory ='H:/Rida/filtered/13072021/M16/M160713160519.txt'
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]
# reads the data file
data_file = pd.read_csv(
    file_path, names=column_names, delimiter=',', header=None, na_values=['', ' '],
    engine='python', usecols=range(17), on_bad_lines='skip'   
)
# replace invalid entries with NaN and convert columns to numeric
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# this is to convert 'time' to seconds and minutes
t_1 = data_file['time'].iloc[0]  # first time value
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001  # convert to seconds
data_file['time_minutes'] = data_file['time_seconds'] / 60  # convert to minutes

# here calculating rolling variance
window_size = 50 
data_file['rolling_variance1'] = data_file['pressure1'].rolling(window=window_size).var()
data_file['rolling_variance2'] = data_file['pressure2'].rolling(window=window_size).var()
k = 1  # Multiplier for sensitivity

rolling_mean1 = data_file['rolling_variance1'].mean() # threshold for pressure1
rolling_std1 = data_file['rolling_variance1'].std()
threshold1 = rolling_mean1 + k * rolling_std1

rolling_mean2 = data_file['rolling_variance2'].mean() # threshold for pressure2
rolling_std2 = data_file['rolling_variance2'].std()
threshold2 = rolling_mean2 + k * rolling_std2

# this line filters the dataset to include only regions with high variance
roi_data1 = data_file[data_file['rolling_variance1'] > threshold1]
roi_data2 = data_file[data_file['rolling_variance2'] > threshold2]

# Function to filter data based on ROI start and end times and save to a specified directory
def save_filtered_data(data_file, roi_data, time_column, output_directory, output_filename):
    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, output_filename) 
    roi_data = roi_data.sort_values(by=time_column) # roi data sorted by time
    start_time = roi_data[time_column].iloc[0]  # this gets start and end times
    end_time = roi_data[time_column].iloc[-1]

    # filters original data within the time range
    filtered_data = data_file[(data_file[time_column] >= start_time) & (data_file[time_column] <= end_time)]
    filtered_data.to_csv(output_file, index=False, sep='\t')  # Save as tab-separated values
    print(f"Filtered data saved to {output_file}")


#saves filtered data for pressure1 and pressure2
save_filtered_data(data_file, roi_data1, 'time', output_directory, 'filtered_pressure1.txt')
save_filtered_data(data_file, roi_data2, 'time', output_directory, 'filtered_pressure2.txt')
print("Data processing complete. Filtered files saved successfully!")

