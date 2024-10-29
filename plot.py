import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import os

# Configure seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
file_path = 'H:/Rida/18072021/18072021/M23/Raw/M23-0718153648.txt'

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
    frequency = 50  # 50 Hz
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

    # Filter the data to only include the first 20 minutes
    data_file_20min = data_file[data_file['time_minutes'] <= 20]

    # Verify the filtered data
    print("Filtered DataFrame (first 20 minutes):")
    print(data_file_20min.head())

    # Check if there are any valid values in 'pressure1' and 'pressure2' for the filtered data
    if data_file_20min['pressure1'].notnull().sum() > 0 and data_file_20min['pressure2'].notnull().sum() > 0:
        # Plot the data for pressure1 and pressure2 over time in minutes
        plt.figure(figsize=(10, 6))
        
        # Plot pressure1
        sns.lineplot(data=data_file_20min, x='time_minutes', y='pressure1', label='Pressure 1', color='green')
        
        # Plot pressure2
        sns.lineplot(data=data_file_20min, x='time_minutes', y='pressure2', label='Pressure 2', color='blue')
        
        # Add labels and title
        plt.title('Pressure over Time (20 Minutes)')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Pressure [mbar]')
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        print("No valid data to plot for 'pressure1' and 'pressure2' in the first 20 minutes.")
 # Define the output directory and file name
    output_dir = 'H:/Rida/clean_data/18072021/M23/clean data'
    output_file = 'M23-0718153648.txt.csv'

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the full path for the output file
    output_file_path = os.path.join(output_dir, output_file)

    # Save the filtered DataFrame to a CSV file
    data_file_20min.to_csv(output_file_path, index=False)

    print(f"Filtered data saved to: {output_file_path}")