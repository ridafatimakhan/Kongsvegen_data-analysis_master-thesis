import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# Configure seaborn for better aesthetics
sns.set(style="darkgrid")

# Define the path to the data file
# file_path = './21072021/M24-0721132106.txt'
# file_path = 'H:/Rida/21072021/21072021/M24/raw/M24-0721154941.txt'
# file_path = 'H:/Rida/21072021/21072021/M24/w_M24-0721132106.txt', operands coming
# file_path = 'H:/Rida/18072021/18072021/M03/M030718173700.txt'
# file_path = 'H:/Rida/18072021/18072021/M10/M100718173756.txt'
# file_path = 'H:/Rida/18072021/18072021/M14/eaw/M14-1231174018.txt'
file_path = 'H:/Rida/18072021/18072021/M23/Raw/M23-0718173731.txt'

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
    
    # Fill missing values with the string "NaN" if desired (optional)
    # df_filled = data_file.fillna("NaN")  # Uncomment if you want to replace NaNs with "NaN"
    
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
else:
    print("Data processing aborted due to previous errors.")
