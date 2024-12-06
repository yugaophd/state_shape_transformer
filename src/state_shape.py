# %%
from shapely.geometry import shape, mapping
from shapely.ops import transform
import geopandas as gpd
import pyproj

# Load the shapefile and filter for New York State
shapefile_path = "../data/external/tl_2024_us_state/tl_2024_us_state.shp"
states = gpd.read_file(shapefile_path)
ny_state = states[states['NAME'] == 'New York']

# Reproject to EPSG:4326 (if not already)
ny_state = ny_state.to_crs(epsg=4326)

# Function to shift latitude by a specified degree amount
def shift_latitude(geometry, shift_degrees):
    # Transformer to shift latitude
    def lat_shift(x, y, z=None):
        return x, y + shift_degrees

    return transform(lat_shift, geometry)

# Shift the geometry's latitude by -100° (from ~45°N to ~55°S)
shift_degrees = -100  # Adjust as needed
ny_shifted_geom = ny_state.geometry.apply(lambda geom: shift_latitude(geom, shift_degrees))

# Create a new GeoDataFrame with the shifted geometry
ny_shifted_geo = gpd.GeoDataFrame(ny_state, geometry=ny_shifted_geom, crs=ny_state.crs)

# Validate the new bounds
print("Shifted Geometry Bounds (degrees):", ny_shifted_geo.total_bounds)

# Plot the original and shifted shapes side by side
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig, axes = plt.subplots(1, 2, figsize=(16, 8), subplot_kw={'projection': ccrs.PlateCarree()})

# Plot original New York State
axes[0].set_extent([-80, -70, 40, 50])  # Bounding box for original NY
axes[0].add_feature(cfeature.COASTLINE)
axes[0].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
ny_state.plot(ax=axes[0], color='blue', transform=ccrs.PlateCarree())
axes[0].set_title("Original New York State")

# Plot shifted New York State
axes[1].set_extent([-80, -70, -60, -54])  # Bounding box for shifted NY
axes[1].add_feature(cfeature.COASTLINE)
axes[1].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
ny_shifted_geo.plot(ax=axes[1], color='red', transform=ccrs.PlateCarree())
axes[1].set_title("New York State at Latitude 55°S")

plt.tight_layout()
plt.show()

# %%
