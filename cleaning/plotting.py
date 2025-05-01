import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the filtered pressure file
file_path_pressure = 'H:/Rida/filtered/13072021/M16/M160713160519.txt/filtered_pressure1.txt'
# Save the plot to a specific directory
output_dir = 'H:/Rida/filtered/13072021/M16/M160713160519.txt'  
output_file = f'{output_dir}/filtered_pressure_plot.png' 
# Define column names for the dataset
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz',
    'time_seconds', 'time_minutes', 'rolling_variance1', 'rolling_variance2'
]

# Read the data into a DataFrame
data_file = pd.read_csv(
    file_path_pressure,
    delimiter='\t',  # Use tab as the delimiter
    names=column_names,  # Assign column names
    header=0,  # Use the first row as the header
    usecols=['time', 'pressure1', 'pressure2'],  # Load only necessary columns
    na_values=['', ' '],  # Treat empty strings as NaN
    engine='python'
)

# Convert 'time' to seconds and minutes based on the first timestamp
t_1 = data_file['time'].iloc[0]  # First time value
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001  # Convert to seconds
data_file['time_minutes'] = data_file['time_seconds'] / 60  # Convert to minutes

# Plot Pressure1 and Pressure2 over time
plt.figure(figsize=(12, 6))
plt.plot(data_file['time_minutes'], data_file['pressure1'], label='Filtered Pressure 1', color='blue')
plt.plot(data_file['time_minutes'], data_file['pressure2'], label='Filtered Pressure 2', color='green')

# Add labels, legend, and title
plt.xlabel('Time (minutes)')
plt.ylabel('Pressure')
plt.title('Filtered Pressure 1 and Pressure 2 Over Time')
plt.legend()

 

# Ensure the directory exists
import os
os.makedirs(output_dir, exist_ok=True)

# Save the plot
plt.savefig(output_file, dpi=300, bbox_inches='tight')  # dpi controls resolution, bbox_inches adjusts spacing
print(f"Plot saved to: {output_file}")

# Display the plot
plt.show()