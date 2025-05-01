import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Seaborn style
sns.set(style="whitegrid")

# Define the file path
file_path = 'H:/Rida/Svalbard_data/outlier_removed/21.07.2021/M24/M24-0721154941/filtered_pressure_cleaned.txt'

# Load the data
sensor_data_file = pd.read_csv(
    file_path,
    delimiter=',',
    na_values=['', ' '],
    engine='python',
    on_bad_lines='skip',
    encoding='ISO-8859-1'
)

# Ensure 'time' column is numeric, drop any rows where 'time' is unreadable
sensor_data_file['time'] = pd.to_numeric(sensor_data_file['time'], errors='coerce')
sensor_data_file = sensor_data_file.dropna(subset=['time'])

# Calculate correlation
correlation = sensor_data_file['pressure1'].corr(sensor_data_file['pressure2'])

# Print the correlation value
print(f'Correlation between Pressure 1 and Pressure 2: {correlation:.3f}')

# Interpretation
if correlation > 0.9:
    interpretation = "Very strong agreement between the sensors."
elif correlation > 0.7:
    interpretation = "Strong agreement between the sensors."
elif correlation > 0.4:
    interpretation = "Moderate agreement between the sensors."
elif correlation > 0.1:
    interpretation = "Weak agreement between the sensors."
else:
    interpretation = "No meaningful agreement detected between the sensors."

print(f'Interpretation: {interpretation}')

#  Scatter Plot with Regression Line
plt.figure(figsize=(8, 6))
sns.regplot(
    x=sensor_data_file['pressure1'],
    y=sensor_data_file['pressure2'],
    scatter_kws={'alpha': 0.5},  # Transparency for better visibility
    line_kws={'color': 'red'},   # Regression line color
)
plt.title(f'Pressure1 vs Pressure2 (Correlation: {correlation:.3f})', fontsize=14)
plt.xlabel('Pressure 1', fontsize=12)
plt.ylabel('Pressure 2', fontsize=12)
plt.grid(True)
plt.show()

# Heatmap of Correlation
plt.figure(figsize=(5, 4))
sns.heatmap(sensor_data_file[['pressure1', 'pressure2']].corr(), annot=True, cmap='coolwarm', fmt=".3f", linewidths=0.5)
plt.title("Correlation Heatmap")
plt.show()
