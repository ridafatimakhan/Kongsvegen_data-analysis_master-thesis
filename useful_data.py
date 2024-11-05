import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configure seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the cleaned data file
cleaned_file_path = 'H:/Rida/clean_data/21072021/M24/clean data/M24-0721154941.txt.csv'

# Read the cleaned data into a DataFrame
try:
    data_file = pd.read_csv(cleaned_file_path)
    print("Cleaned DataFrame loaded successfully:")
    print(data_file.head())
except Exception as e:
    print(f"Error reading the cleaned file: {e}")

# Function to remove outliers based on IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    # Define the limits for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    # Filter the DataFrame
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Remove outliers for pressure1 and pressure2
data_file_cleaned = remove_outliers(data_file, 'pressure1')
data_file_cleaned = remove_outliers(data_file_cleaned, 'pressure2')

# Verify the removal of outliers
print("\nData after outlier removal:")
print(data_file_cleaned.head())

# Plotting the cleaned pressure data over time
plt.figure(figsize=(10, 6))

# Plot pressure1
sns.lineplot(data=data_file_cleaned, x='time_minutes', y='pressure1', label='Pressure 1', color='green')

# Plot pressure2
sns.lineplot(data=data_file_cleaned, x='time_minutes', y='pressure2', label='Pressure 2', color='blue')

# Add labels and title
plt.title('Useful Pressure over Time (20 Minutes)')
plt.xlabel('Time (minutes)')
plt.ylabel('Pressure [mbar]')
plt.legend()
plt.tight_layout()

# Define the output directory and file name for the cleaned data
output_cleaned_dir = 'H:/Rida/useful_data/21072021/M24'
output_cleaned_file = 'M24-0721154941.txt.csv'

# Create the output directory if it doesn't exist
os.makedirs(output_cleaned_dir, exist_ok=True)

# Define the plot file path within the output directory
plot_file_path = os.path.join(output_cleaned_dir, 'M24-0721154941.txt.png')

# Save the plot to the specified directory
plt.savefig(plot_file_path)

# Display the plot
plt.show()

print(f"Plot saved to: {plot_file_path}")

# Create a new DataFrame that contains the first 17 columns along with the cleaned pressure data
data_file_first_17 = data_file_cleaned.copy()  # Make a copy of the cleaned data
data_file_first_17 = data_file_first_17.loc[:, data_file.columns[:17]]  # Retain the first 17 columns

# Save the cleaned DataFrame (including first 17 columns) to a CSV file
output_cleaned_file_path = os.path.join(output_cleaned_dir, output_cleaned_file)
data_file_first_17.to_csv(output_cleaned_file_path, index=False)

print(f"Cleaned data with the first 17 columns saved to: {output_cleaned_file_path}")
