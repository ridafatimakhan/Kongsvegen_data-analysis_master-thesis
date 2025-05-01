import numpy as np
import matplotlib.pyplot as plt
import folium
from folium import plugins  # Use plugins directly from folium
import branca.colormap as cm

# Sensor Data (Latitude, Longitude, Height)
data = np.array([
    [78.842877, 12.605902, 171.3213],
    [78.842892, 12.605624, 169.7250],
    [78.842892, 12.605617, 160.1828],
    [78.842889, 12.605625, 159.4150],
    [78.842896, 12.606154, 153.4490],
])

lat, lon, height = data[:, 0], data[:, 1], data[:, 2]
center = [np.mean(lat), np.mean(lon)]

# Use Google Satellite Tiles (Requires API Key) or ESRI World Imagery (Free)
esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

m = folium.Map(location=center, zoom_start=15, tiles=esri_tiles, attr="ESRI")  # Use ESRI for free

# Add Sensor Markers
for i in range(len(lat)):
    folium.Marker([lat[i], lon[i]], popup=f"Height: {height[i]}m").add_to(m)

# Create a Colormap for Line Color
colormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'],
                             vmin=min(height), vmax=max(height),
                             caption="Height (m)")

# Create a Line with Color Based on Height
line_segments = []
for i in range(len(lat) - 1):
    segment = [[lat[i], lon[i]], [lat[i+1], lon[i+1]]]
    color = colormap(height[i])  # Get color based on height
    line_segments.append(folium.PolyLine(segment, color=color, weight=5).add_to(m))

# Add Color Legend
m.add_child(colormap)

# Add Scale Control (Similar to Google Maps Distance Scale)
folium.plugins.MeasureControl(primary_length_unit='meters', secondary_length_unit='kilometers').add_to(m)

# Save & Display Map
m.save("bootlog.html")
m
