import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pyproj import Transformer



# Load the data file
input_file = 'H:/Rida/Dataset/18072021/18072021/M24/Raw/M24-0718173840.txt'  # Replace with your actual file path
with open(input_file, "r") as file:
    lines = file.readlines()

gps_data = {}
current_gps_key = None


for line in lines:
    if not line.strip():
        continue
    
    parts = line.split(",")
    timestamp = parts[0]
    extra_data = parts[19:]
    
    gps_match = re.search(r"(\$G\w+)", ",".join(extra_data))
    
    if gps_match:
        current_gps_key = timestamp  # Store timestamp for this GPS entry
        gps_data[current_gps_key] = ",".join(extra_data)  # Initialize entry
    elif current_gps_key:
        gps_data[current_gps_key] += "," + ",".join(extra_data)  # Append to last GPS entry

# Function to extract latitude and longitude
def extract_lat_lon(gps_string):
    lat_match = re.search(r"(\d{0,4}\.\d+),([NS])", gps_string)
    
    if lat_match:
        lat_value = lat_match.group(1)
        direction = lat_match.group(2)
        
        # Add missing prefix "7850" based on the length of the matched latitude value
        if len(lat_value) == 6 and str(lat_value[0])=='.':  # Case: .57316
            lat_value1 = f"7850{lat_value}"
        elif len(lat_value) == 7 and str(lat_value[0:2])=='0.':  # Case: 0.57316
            lat_value1 = f"785{lat_value}"
        elif len(lat_value) == 8 and str(lat_value[0:3])=='50.':  # Case: 50.57316
            lat_value1 = f"78{lat_value}"
        elif len(lat_value) == 9 and str(lat_value[0:4])=='850.': # Case: 850.57316
            lat_value1 = f"7{lat_value}"
        elif len(lat_value) == 10 and str(lat_value[0:5])=='7850.':  # Case: 7850.57316
            lat_value1 = lat_value
        else:
            lat_value1 = 'nan'

        print(str(lat_value[0:4]))
        print(len(lat_value))
        
        lat_match = f"{lat_value1},{direction}"
    else:
        lat_match = None

    # Match longitude in the format 01260.57316 or .57316
    lon_match = re.search(r"(\d{0,5}\.\d+),([EW])", gps_string)
    if lon_match:
        lon_value = lon_match.group(1)
        direction = lon_match.group(2)
        
        # Add missing prefix "012" based on the length of the matched longitude value
        if len(lon_value) == 8 and str(lon_value[2])=='.':  # Case: .57316
            lon_value1 = f"012{lon_value}"
        elif len(lon_value) == 9 and str(lon_value[3])=='.':  # Case: 0.57316
            lon_value1 = f"01{lon_value}"
        elif len(lon_value) == 10 and str(lon_value[4])=='.':  # Case: 50.57316
            lon_value1 = f"0{lon_value}"
        elif len(lon_value) == 9 and str(lon_value[5])=='.': # Case: 850.57316
            lon_value1 = lon_value
        else:
            lon_value1 = 'nan'

        
        lon_match = f"{lon_value1},{direction}"
    else:
        lon_match = None

    lat = lat_match if lat_match else np.nan
    lon = lon_match if lon_match else np.nan

    return lat, lon

def ddm_to_dd(ddm: float) -> float:
    """
    Convert Degrees and Decimal Minutes (DDM) to Decimal Degrees (DD).
    :param ddm: Latitude or Longitude in DDM format (DDDMM.MMMM).
    :return: Decimal degrees as a float.
    """
    degrees = int(ddm // 100)  # Extract degrees
    minutes = ddm % 100  # Extract minutes
    decimal_degrees = degrees + (minutes / 60)
    
    return decimal_degrees

# Output final structured GPS data with lat/lon extraction
print("Final GPS Data with Latitude & Longitude:")
data = {'Timestamp': [], 'Latitude': [], 'Longitude': []}
for timestamp, gps in gps_data.items():
    lat, lon = extract_lat_lon(gps)
    if isinstance(lat, str) and lat.strip():
        try:
            numeric_value_lat = float(re.sub(r'[^\d.]', '', lat))  # Remove anything that's not a digit or a dot
        except:
            numeric_value_lat = np.nan
    else:
        numeric_value_lat = np.nan

    if isinstance(lon, str) and lon.strip():
        try:
            numeric_value_lon = float(re.sub(r'[^\d.]', '', lon))  # Remove anything that's not a digit or a dot
        except:
            numeric_value_lon = np.nan
    else:
        numeric_value_lon = np.nan    
    
    print(f"{timestamp}: | Lat: {numeric_value_lat}, Lon: {numeric_value_lon}")
    # Create a DataFrame from the extracted data
    # Create a DataFrame from the extracted data
   
    if np.isnan(numeric_value_lat) and np.isnan(numeric_value_lon):
        continue
    else:
        data['Timestamp'].append(timestamp)
        data['Latitude'].append(numeric_value_lat)
        data['Longitude'].append(numeric_value_lon)

df = pd.DataFrame(data)
print(df)
# Fill NaN values in the DataFrame
df.fillna(method='ffill', inplace=True)  # Forward fill
df.fillna(method='bfill', inplace=True)  # Backward fill
# Smooth latitude and longitude data using a rolling mean
df['Latitude'] = df['Latitude'].rolling(window=5, center=True).median()
df['Longitude'] = df['Longitude'].rolling(window=5, center=True).median()
df.dropna(inplace=True)  # Drop NaN values
df.reset_index(drop=True, inplace=True)  # Reset the index
print(df)

# Correct for very small values that came with filling NaNs
#df = df[(df['Latitude'] >= 100) & (df['Longitude'] >= 100)]

# Define transformation from ED50 (EPSG:4230) to WGS84 (EPSG:4326)
#transformer = Transformer.from_crs("EPSG:4230", "EPSG:4326", always_xy=True)

# Convert (longitude, latitude)
#df['Longitude'], df['Latitude'] = transformer.transform(df['Longitude'], df['Latitude'])

#plt.scatter(df['Latitude'], df['Longitude'])
#plt.show()

# Align start point with the first latitude and longitude values in the data
# This can be done, as the first GPS point was waited to happen before starting the data collection

lat_values = df['Latitude'].values
lon_values = df['Longitude'].values


# Convert the latitudes and longitudes to decimal degrees
latitudes = [ddm_to_dd(lat) for lat in lat_values]
longitudes = [ddm_to_dd(lon) for lon in lon_values]

df['Latitude'] = latitudes
df['Longitude'] = longitudes

#print(df)

ground_truth = pd.read_csv('H:/Rida/Converted_dgps_T3/long_profile/18072021/76291991.txt', sep='\s+',skiprows=10 , header=None)
ground_truth_lat = ground_truth[2].values
ground_truth_lon = ground_truth[3].values


# Convert the latitudes and longitudes to decimal degrees
ground_truth_latitudes = ground_truth_lat #[convert_to_decimal(lat) for lat in ground_truth_lat]
ground_truth_longitudes = ground_truth_lon #[convert_to_decimal(lon) for lon in ground_truth_lon]

# Create a plot with a polar projection (North Polar)
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': ccrs.NorthPolarStereo()})

# Add coastlines for context
ax.coastlines(resolution='110m')

# Plot the latitude and longitude points
# Add gridlines and labels for better readability
gridlines = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gridlines.top_labels = False
gridlines.right_labels = False

# Set the extent of the plot (adjust as needed for your data)
ax.set_extent([12, 13, 79, 78], crs=ccrs.PlateCarree())
ax.scatter(longitudes, latitudes, color='red', s=50, marker='o', transform=ccrs.PlateCarree(), label="Drifter GPS")
ax.plot(ground_truth_longitudes, ground_truth_latitudes, color='black' , transform=ccrs.PlateCarree(), label="ORiginal track")
ax.legend()
ax.xlabel = 'Longitude'    #s=50, marker='o'
ax.ylabel = 'Latitude'

# Set title and show the plot
ax.set_title('Latitude and Longitude in Polar Region')
plt.show()
