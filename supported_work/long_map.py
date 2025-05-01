import numpy as np
import folium
from folium import plugins

# Read data from a text file
file_path = '76291969.txt'  # Replace with your actual file path
data = np.loadtxt(file_path, skiprows=8)  # Skip first 8 rows

# Extract latitude and longitude (3rd and 4th columns)
lat = data[:, 2]  # 3rd column is latitude
lon = data[:, 3]  # 4th column is longitude

# Define map center (mean of latitudes and longitudes)
center = [np.mean(lat), np.mean(lon)]

# Use Google Satellite Tiles (Requires API Key) or ESRI World Imagery (Free)
esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

m = folium.Map(location=center, zoom_start=15, tiles=esri_tiles, attr="ESRI")  # Use ESRI for free

# Create a Line with Black Color (No height info, just latitude and longitude)
line_segments = []
for i in range(len(lat) - 1):
    segment = [[lat[i], lon[i]], [lat[i+1], lon[i+1]]]
    line_segments.append(folium.PolyLine(segment, color='black', weight=3).add_to(m))

# Add markers at the first and last points with text labels always visible
folium.Marker([lat[0], lon[0]], icon=folium.Icon(color='green')).add_to(m)
folium.Marker([lat[-1], lon[-1]], icon=folium.Icon(color='red')).add_to(m)

# Add text labels directly on the map
folium.map.Marker(
    location=[lat[0], lon[0]],
    popup='Start',
    icon=folium.DivIcon(
        icon_size=(150, 36),
        icon_anchor=(7, 20),
html='<div style="font-size: 12pt; color: white; font-weight: bold;  margin-left: 25px;">Start</div>'
    )
).add_to(m)

folium.map.Marker(
    location=[lat[-1], lon[-1]],
    popup='End',
    icon=folium.DivIcon(
        icon_size=(150, 36),
        icon_anchor=(7, 20),
html='<div style="font-size: 12pt; color: white; font-weight: bold; margin-left: 25px;">End</div>'
    )
).add_to(m)

# Add Scale Control (Similar to Google Maps Distance Scale)
folium.plugins.MeasureControl(primary_length_unit='meters', secondary_length_unit='kilometers').add_to(m)

# Save & Display Map
m.save("sensor_map_with_start_end_labels_visible.html")
m
