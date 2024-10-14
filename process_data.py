import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
# file_path = 'M24-0721154941.txt'
# file_path = 'M24-0718153650.txt'
file_path = 'M24-0721132106.txt'

# Define column names for the dataset (first 17 columns)
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# Read the data into a DataFrame (only the first 17 columns)
try:
    # Check if the file has enough columns by reading the first line
    with open(file_path, 'r') as f:
        first_line = f.readline()
        num_columns = len(first_line.split(','))

    # Ensure that only the first 17 columns are used
    use_columns = min(num_columns, 17)  # Limit to 17 columns

    # Read the CSV file with dynamic usecols
    data_file = pd.read_csv(
        file_path,
        names=column_names[:use_columns],  # Match column names to available columns
        delimiter=',',
        header=None,
        na_values=['', ' '],  # Treat empty strings as NaN
        engine='python',
        usecols=range(use_columns),  # Use only the first 17 columns
        on_bad_lines='skip'  # Skip lines with too many fields
    )

    # Display the first few rows to verify the data
    print("Initial DataFrame:")
    print(data_file.head())

except Exception as e:
    print(f"Error reading the file: {e}")

# Check for missing values
print("\nMissing Values in Each Column:")
print(data_file.isnull().sum())

# Fill missing values with the string "NaN"
df_filled = data_file.fillna("NaN")  # Replace NaNs with the string "NaN"

# Convert the 'time' column from sample index (frequency-based) to minutes
# Assuming 'time' is in terms of 100 Hz, convert to seconds and then to minutes
frequency = 100  # 100 Hz
data_file['time_minutes'] = data_file['time'] / (frequency * 60)

# Verify the new time column
print("\nTime in Minutes:")
print(data_file[['time', 'time_minutes']].head())

# Calculate the rolling variance of 'pressure1' and 'pressure2' with a window size of 5
data_file['pressure1_variance'] = data_file['pressure1'].rolling(window=5).var()
data_file['pressure2_variance'] = data_file['pressure2'].rolling(window=5).var()

# Display the variance of pressure1 and pressure2
print("\nPressure1 and Pressure2 Variances:")
print(data_file[['time_minutes', 'pressure1_variance', 'pressure2_variance']].head())

# Create a figure with two subplots (one on top of the other)
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(12, 10))

# Plot 1: Variance of Pressure 1 over Time (in Minutes)
ax1.plot(data_file['time_minutes'], data_file['pressure1_variance'], label='Pressure 1 Variance', color='green')
ax1.set_title('Variance of Pressure 1 Over Time (in Minutes)')
ax1.set_xlabel('Time (Minutes)')
ax1.set_ylabel('Variance of Pressure 1 (hPa²)')
ax1.legend()
ax1.grid()

# Plot 2: Variance of Pressure 2 over Time (in Minutes)
ax2.plot(data_file['time_minutes'], data_file['pressure2_variance'], label='Pressure 2 Variance', color='blue')
ax2.set_title('Variance of Pressure 2 Over Time (in Minutes)')
ax2.set_xlabel('Time (Minutes)')
ax2.set_ylabel('Variance of Pressure 2 (hPa²)')
ax2.legend()
ax2.grid()

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()

