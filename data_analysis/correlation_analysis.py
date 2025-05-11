import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from glob import glob

root_directory = "H:/Rida/Kongsvegen_data/outlier_removed/"
# Find all 'filtered_pressure_cleaned.txt' files across subdirectories
file_paths = glob(os.path.join(root_directory, "**", "filtered_pressure_cleaned.txt"), recursive=True)
correlation_data = [] # List to store correlation data
# Iterate through all files and compute correlation
for file_path in file_paths:
    try:
        sensor_data = pd.read_csv(
            file_path,
            delimiter=',',
            na_values=['', ' '],
            engine='python',
            on_bad_lines='skip',
            encoding='ISO-8859-1'
        )

        sensor_data['time'] = pd.to_numeric(sensor_data['time'], errors='coerce')
        sensor_data = sensor_data.dropna(subset=['time'])

        correlation = sensor_data['pressure1'].corr(sensor_data['pressure2']) # Calculate correlation between pressure1 and pressure2

        # Extract sensor folder name and date folder
        parts = file_path.split(os.sep)
        date_folder = parts[-4]  # Extract the date folder (e.g., "13072021")
        sensor_folder = parts[-3]  # Extract the sensor name (e.g., "M21")
        measurement_index = len([entry for entry in correlation_data if entry['date_folder'] == date_folder and entry['sensor_folder'] == sensor_folder]) + 1

        # Create a unique identifier for each sensor occurrence
        date_sensor_measurement = f"{date_folder}_{sensor_folder}_M{measurement_index}"

        # Store data
        correlation_data.append({
            'date_folder': date_folder,
            'sensor_folder': sensor_folder,
            'date_sensor_measurement': date_sensor_measurement,  # Unique label for each measurement
            'correlation': correlation
        })
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Convert list to DataFrame
correlation_df = pd.DataFrame(correlation_data)

# Sort by date folder and sensor name
correlation_df = correlation_df.sort_values(by=['date_folder', 'sensor_folder'])

# Set figure size dynamically based on the number of unique entries
fig, ax = plt.subplots(figsize=(len(correlation_df['date_sensor_measurement'].unique()) * 0.5, 6))

# Create a box plot with grey shading
sns.boxplot(
    data=correlation_df,
    x='date_folder',
    y='correlation',
    color='grey'
)

# Label axes
plt.xlabel("Data samples", fontsize=12)
plt.ylabel("Pearson Coefficient", fontsize=12)
plt.ylim(0,1.2)
#plt.title("Distribution of Correlation between Pressure 1 and Pressure 2", fontsize=14)

# Rotate x-axis labels at 45-degree angle for better visibility
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)  # Increase y-axis tick font size
# Get current y-ticks and exclude the last one
yticks = plt.gca().get_yticks()
plt.gca().set_yticks(yticks[:-1])
plt.tight_layout()
plt.show()
