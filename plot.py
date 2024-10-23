import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from scipy import stats

# Configure seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
# file_path = 'H:/Rida/15072021/15072021/M22/other/M220715162024.txt'
# file_path = 'H:/Rida/18072021/18072021/M24/Raw/M24-0718173840.txt'
file_path = 'H:/Rida/13072021/13072021/M13/other/M130713081527.txt'



# Define column names for the dataset (first 17 columns)
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz'
]

# Initialize data_file as None
data_file = None

# Read the data into a DataFrame (only the first 17 columns)
try:
    # Open the file with 'utf-8' encoding, replacing invalid bytes
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        # Read the entire content
        file_content = f.read()
    
    # Use StringIO to simulate a file-like object for pandas
    data_io = StringIO(file_content)
    
    # Read the CSV data
    data_file = pd.read_csv(
        data_io,
        names=column_names,  # Assign column names
        delimiter=',',
        header=None,
        na_values=['', ' '],  # Treat empty strings as NaN
        engine='python',
        usecols=range(17),  # Use only the first 17 columns
        on_bad_lines='skip'  # Skip lines with too many fields
    )
    
    # Replace the placeholder character '�' with NaN
    data_file.replace('�', pd.NA, inplace=True)
    
    # Convert all columns except 'time' to numeric, coercing errors to NaN
    for col in column_names:
        if col != 'time':
            data_file[col] = pd.to_numeric(data_file[col], errors='coerce')
    
    # Display the first few rows to verify the data
    print("Initial DataFrame:")
    print(data_file.head())

except Exception as e:
    print(f"Error reading the file: {e}")

# Proceed only if data_file was successfully read
if data_file is not None:
    # Check for missing values
    print("\nMissing Values in Each Column:")
    print(data_file.isnull().sum())
    
    # Convert the 'time' column from sample index (frequency-based) to minutes
    frequency = 100  # 100 Hz
    first_time_stamp = data_file['time'].iloc[0]  # Get the first time stamp
    data_file['time_minutes'] = (data_file['time'] - first_time_stamp) / frequency / 60  # Adjust to start from the first timestamp
    
    # Verify the new time column
    print("\nTime in Minutes:")
    print(data_file[['time', 'time_minutes']].head())

    # Calculate a rolling variance for pressure1 (you can adjust the window size)
    rolling_variance = data_file['pressure1'].rolling(window=10).var()  # Adjust window size as needed
    data_file['rolling_variance'] = rolling_variance

    # Find the index of the maximum rolling variance
    max_variance_index = data_file['rolling_variance'].idxmax()
    
    # Get the corresponding timestamp
    max_variance_time_stamp = data_file['time'].iloc[max_variance_index]
    max_variance_time_minutes = data_file['time_minutes'].iloc[max_variance_index]

    print(f"\nTimestamp of Maximum Variance in Pressure 1: {max_variance_time_stamp}")
    print(f"Maximum Variance Time (in minutes): {max_variance_time_minutes}")

# Check if there are any valid values in 'pressure1' and 'pressure2'
if data_file['pressure1'].notnull().sum() > 0 and data_file['pressure2'].notnull().sum() > 0:
    # Plot the data for pressure1 and pressure2 over time in minutes
    plt.figure(figsize=(10, 6))
    
    # Plot pressure1
    sns.lineplot(data=data_file, x='time_minutes', y='pressure1', label='Pressure 1', color='blue')
    
    # Plot pressure2
    sns.lineplot(data=data_file, x='time_minutes', y='pressure2', label='Pressure 2', color='green')
    
    # Add labels and title
    plt.title('Pressure over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Pressure [mbar]')
    # plt.xlim (-1,20)
    # plt.ylim (980,1010)
    # Display the plot
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No valid data to plot for 'pressure1' and 'pressure2'.")
