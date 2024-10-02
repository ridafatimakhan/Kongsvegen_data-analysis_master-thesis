import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# here configuring seaborn for better aesthetics
sns.set(style="darkgrid")

# here is defining the path to data file
file_path = 'M24-0721154941.txt'  

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
# only using the first 30 columns, because: Error reading the file: Expected 30 fields in line 93, saw 31
try:
    data_file = pd.read_csv(
        file_path,
        names=column_names,
        delimiter=',',
        header=None,
        na_values=['', ' '],  # Treat empty strings as NaN
        engine='python',
        usecols=range(30),  # Only use the first 30 columns
        on_bad_lines='skip'  # Skip lines with too many fields
    )
    # Display the first few rows to verify the data
    print("Initial DataFrame:")
    print(data_file.head())
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


