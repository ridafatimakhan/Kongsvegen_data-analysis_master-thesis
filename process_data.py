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

# Plot Temperature Over Time
plt.figure(figsize=(12, 6))
plt.plot(df_filled['time'], df_filled['temp1'], label='Temp 1', color='orange', marker='o')
plt.plot(df_filled['time'], df_filled['temp2'], label='Temp 2', color='blue', marker='o')
plt.title('Temperature Over Time')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.grid()
plt.show()

# Plot Acceleration Over Time
plt.figure(figsize=(12, 6))
plt.plot(df_filled['time'], df_filled['accx'], label='Acc X', color='red', marker='o')
plt.plot(df_filled['time'], df_filled['accy'], label='Acc Y', color='green', marker='o')
plt.plot(df_filled['time'], df_filled['accz'], label='Acc Z', color='purple', marker='o')
plt.title('Acceleration Over Time')
plt.xlabel('Time')
plt.ylabel('Acceleration (m/s²)')
plt.legend()
plt.grid()
plt.show()

# Plot Movement Path (Latitude vs. Longitude)
plt.figure(figsize=(12, 8))
plt.plot(df_filled['longitude'], df_filled['latitude'], color='teal', marker='o')
plt.title('Movement Path (Latitude vs. Longitude)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid()
plt.axis('equal')  # Equal scaling for both axes
plt.show()

# Plot Pressure Over Time
plt.figure(figsize=(12, 6))
plt.plot(df_filled['time'], df_filled['pressure1'], label='Pressure 1', color='blue', marker='o')
plt.plot(df_filled['time'], df_filled['pressure2'], label='Pressure 2', color='orange', marker='o')
plt.title('Pressure Over Time')
plt.xlabel('Time')
plt.ylabel('Pressure (hPa)')
plt.legend()
plt.grid()
plt.show()

# Plot Magnetometer Data
plt.figure(figsize=(12, 6))
plt.plot(df_filled['time'], df_filled['magx'], label='Mag X', color='red', marker='o')
plt.plot(df_filled['time'], df_filled['magy'], label='Mag Y', color='green', marker='o')
plt.plot(df_filled['time'], df_filled['magz'], label='Mag Z', color='purple', marker='o')
plt.title('Magnetometer Data Over Time')
plt.xlabel('Time')
plt.ylabel('Magnetic Field (uT)')
plt.legend()
plt.grid()
plt.show()
