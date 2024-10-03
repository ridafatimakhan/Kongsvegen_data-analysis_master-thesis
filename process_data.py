import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# here configuring seaborn for better aesthetics
sns.set(style="darkgrid")

# here is defining the path to data file
# file_path = 'M24-0721154941.txt'  
file_path = 'M24-0718153650.txt'

#Here, I am defining the column names. first 17 are taken from the header file,
# 18, 19 is long, and lat, rest 11 are assumed
column_names = [
    'time', 'pressure1', 'temp1', 'pressure2', 'temp2',
    'accx', 'accy', 'accz',
    'gyx', 'gyy', 'gyz',
    'magx', 'magy', 'magz',
    'hgax', 'hgay', 'hgaz',
    'gps1', 'gps2', 'gps3', 'gps4', 'gps5',
    'gps6', 'gps7', 'gps8', 'gps9', 'gps10',
    'gps11', 'gps12', 'gps13'
]

# reading the data into a DataFrame.
import pandas as pd

try:
    # Check if the file has enough columns by reading the first few lines
    with open(file_path, 'r') as f:
        first_line = f.readline()
        num_columns = len(first_line.split(','))

    # Adjust usecols based on the number of columns in the file
    if num_columns >= 30:
        use_columns = range(30)
    else:
        use_columns = range(num_columns)  # Use only available columns

    # Read the CSV file with dynamic usecols
    data_file = pd.read_csv(
        file_path,
        names=column_names[:num_columns],  # Match column names to the available columns
        delimiter=',',
        header=None,
        na_values=['', ' '],  # Treat empty strings as NaN
        engine='python',
        usecols=use_columns,  # Dynamically choose columns based on the file
        on_bad_lines='skip'  # Skip lines with too many fields
    )
    
    # Display the first few rows to verify the data
    print("Initial DataFrame:")
    print(data_file.head())
    
    # Perform the next steps (e.g., creating new columns) only if data_file exists
    data_file['latitude'] = data_file['gps1'] / 1_000_000
    data_file['longitude'] = data_file['gps2'] / 1_000_000

except Exception as e:
    print(f"Error reading the file: {e}")



# Check the data type of 'time' column
# print("\nData Types Before Conversion:")
# print(data_file.dtypes)

# Scale GPS coordinates
data_file['latitude'] =  data_file['gps1'] / 1_000_000
data_file['longitude'] =  data_file['gps2'] / 1_000_000

# Display scaled GPS coordinates
print("\nScaled GPS Coordinates:")
print( data_file[['gps1', 'latitude', 'gps2', 'longitude']].head())

# Check for missing values
print("\nMissing Values in Each Column:")
print(data_file.isnull().sum())

# Fill missing values with the string "NaN"
df_filled = data_file.fillna("NaN")  # Replace NaNs with the string "NaN"

# Verify filling
print("\nDataFrame After Filling Missing Values:")
print(df_filled.head())

# Plot Pressure Over Time
plt.figure(figsize=(12, 6))
plt.plot(df_filled['time'], df_filled['pressure1'], label='Pressure 1', color='blue')
plt.plot(df_filled['time'], df_filled['pressure2'], label='Pressure 2', color='orange')
plt.title('Pressure Over Time')
plt.xlabel('Time')
plt.ylabel('Pressure (hPa)')
plt.legend()
plt.grid()
plt.show()


