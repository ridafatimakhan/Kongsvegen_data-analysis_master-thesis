import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
file_path = 'H:/Rida/18072021/18072021/M08/raw/M08-0718144907.txt'
output_directory = 'H:/Rida/'

# Update column names to include GPS columns (assumed as latitude and longitude)
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz',
    'latitude', 'longitude'  # New columns
]

# Read the data into a DataFrame (including GPS)
data_file = pd.read_csv(
    file_path,
    names=column_names,
    delimiter=',',
    header=None,
    na_values=['', ' '],
    engine='python',
    usecols=range(len(column_names)),  # Adjust for 19 columns now
    on_bad_lines='skip'
)

# Replace invalid entries with NaN and convert columns to numeric
data_file.replace('�', pd.NA, inplace=True)
for col in column_names:
    if col != 'time':
        data_file[col] = pd.to_numeric(data_file[col], errors='coerce')

# Convert 'time' to seconds and minutes
t_1 = data_file['time'].iloc[0]
data_file['time_seconds'] = (data_file['time'] - t_1) * 0.001
data_file['time_minutes'] = data_file['time_seconds'] / 60

# Calculate rolling variance
window_size = 50
data_file['rolling_variance1'] = data_file['pressure1'].rolling(window=window_size).var()
data_file['rolling_variance2'] = data_file['pressure2'].rolling(window=window_size).var()

# Compute thresholds
k = 1
threshold1 = data_file['rolling_variance1'].mean() + k * data_file['rolling_variance1'].std()
threshold2 = data_file['rolling_variance2'].mean() + k * data_file['rolling_variance2'].std()

# Filter ROI
roi_data1 = data_file[data_file['rolling_variance1'] > threshold1]
roi_data2 = data_file[data_file['rolling_variance2'] > threshold2]

# Function to filter and save data
def save_filtered_data(data_file, roi_data, time_column, output_directory, output_filename):
    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, output_filename)
    roi_data = roi_data.sort_values(by=time_column)
    start_time = roi_data[time_column].iloc[0]
    end_time = roi_data[time_column].iloc[-1]
    filtered_data = data_file[(data_file[time_column] >= start_time) & (data_file[time_column] <= end_time)]
    filtered_data.to_csv(output_file, index=False, sep='\t')
    print(f"Filtered data saved to {output_file}")

# Save filtered files
#save_filtered_data(data_file, roi_data1, 'time', output_directory, 'filtered_pressure1.txt')
#save_filtered_data(data_file, roi_data2, 'time', output_directory, 'filtered_pressure2.txt')

print("Data processing complete. Filtered files saved successfully!")

# ==========================
# 🗺️ Plot GPS: Latitude vs Longitude with time as color
# ==========================
# Drop rows where GPS or time data is missing
gps_data = data_file.dropna(subset=['latitude', 'longitude', 'time_minutes'])

# Plotting
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    gps_data['longitude'], 
    gps_data['latitude'], 
    c=gps_data['time_minutes'], 
    cmap='viridis', 
    s=10
)
plt.colorbar(scatter, label='Time (minutes)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('GPS Track Colored by Time (minutes)')
plt.grid(True)
plt.tight_layout()
plt.show()
