import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")

input_file_path = 'H:/Rida/new/13072021/M18/M180713151102/filtered_pressure1.txt'
output_directory = 'H:/Rida/new/outlier_removed/M18/M180713151102'
os.makedirs(output_directory, exist_ok=True)

# here define column names for the dataset
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz',
    'time_seconds', 'time_minutes', 'rolling_variance1', 'rolling_variance2'
]

# reads the data into a DataFrame
data_file = pd.read_csv(
    input_file_path,
    delimiter='\t',  
    names= column_names,  
    header=0,  
    usecols=range(17), 
    # usecols=['time', 'pressure1', 'pressure2'],  # Load only necessary columns
    na_values=['', ' '],  
    engine='python'
)

# Convert 'time' to seconds and minutes based on the first timestamp
t_1 = data_file['time'].iloc[0]  # First time value
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001  # Convert to seconds
data_file['time_minutes'] = data_file['time_seconds'] / 60  # Convert to minutes


# function defined to remove outliers for 'pressure1' and 'pressure2' (IQR method)
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.10)
    Q3 = df[column].quantile(0.90)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# applying the function
data_file_cleaned = remove_outliers(data_file, 'pressure1')
data_file_cleaned = remove_outliers(data_file_cleaned, 'pressure2')

# save the cleaned data to a new file
output_file_path = os.path.join(output_directory, 'filtered_pressure_cleaned.txt')
data_file_cleaned.to_csv(output_file_path, index=False, sep=',', header=True)

plt.figure(figsize=(10, 6))
plt.plot(data_file_cleaned['time_minutes'], data_file_cleaned['pressure1'], label='Pressure1', color='blue')
plt.plot(data_file_cleaned['time_minutes'], data_file_cleaned['pressure2'], label='Pressure2', color='orange')
plt.xlabel('Time (minutes)', fontsize=20)
plt.ylabel('Pressure (hPa)', fontsize=20)
plt.ylim(985, 1027)  # Adjust y-axis limits as needed
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(fontsize=18)
plt.grid(True)

plot_file_path = os.path.join(output_directory, 'pressure_plot_cleaned.png')
plt.savefig(plot_file_path)
plt.show()

print(f"Cleaned data saved to: {output_file_path}")
print(f"Plot saved to: {plot_file_path}")