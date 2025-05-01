import numpy as np
import folium
from folium import plugins  # Use plugins directly from folium
import branca.colormap as cm

# Sensor Data (Latitude, Longitude, Height)
data = np.array([
    [78.842906865, 12.605622357, 171.3213],
    [78.843369506, 12.604075537, 169.7250],
    [78.844456107, 12.600022306, 160.1828],
    [78.844974718, 12.597279470, 159.4150],
    [78.846111572, 12.593647543, 153.4490],
    [78.846665800, 12.591295073, 151.7903],
    [78.846665921, 12.591248070, 155.3220],
    [78.847072116, 12.588701342, 157.1121],
])

lat, lon, height = data[:, 0], data[:, 1], data[:, 2]
center = [np.mean(lat), np.mean(lon)]

# Use ESRI World Imagery
esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
m = folium.Map(location=center, zoom_start=15, tiles=esri_tiles, attr="ESRI")

# Create a Colormap for Line Color
colormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'],
                             vmin=min(height), vmax=max(height),
                             caption="Height (m)")

# Linear interpolation function
def interpolate_points(p1, p2, h1, h2, num_points=50):
    """Generates interpolated points between two lat/lon positions."""
    lat_interp = np.linspace(p1[0], p2[0], num_points)
    lon_interp = np.linspace(p1[1], p2[1], num_points)
    height_interp = np.linspace(h1, h2, num_points)
    return np.column_stack((lat_interp, lon_interp, height_interp))

# Interpolate and add the polyline segments
for i in range(len(lat) - 1):
    interpolated_points = interpolate_points(
        (lat[i], lon[i]), (lat[i+1], lon[i+1]), height[i], height[i+1]
    )

    segment_coords = interpolated_points[:, :2].tolist()
    segment_colors = [colormap(h) for h in interpolated_points[:, 2]]

    for j in range(len(segment_coords) - 1):
        folium.PolyLine([segment_coords[j], segment_coords[j + 1]], 
                        color=segment_colors[j], weight=5).add_to(m)

# Add Color Legend
m.add_child(colormap)

# Add Scale Control
folium.plugins.MeasureControl(primary_length_unit='meters', secondary_length_unit='kilometers').add_to(m)

# Save & Display Map
m.save("sensor_map_with_interpolation.html")
m
