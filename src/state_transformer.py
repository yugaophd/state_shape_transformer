# %%
from shapely.geometry import shape, mapping
from shapely.ops import transform
import geopandas as gpd
import pyproj
from shapely.affinity import translate

#######Change the path to the directory where the source code is stored #######
import os
os.chdir('/Users/yugao/Desktop/projects/state_shape_transformer/src')

# Load the shapefile and filter for {state_name} State
shapefile_path = "../data/external/tl_2024_us_state/tl_2024_us_state.shp"
states = gpd.read_file(shapefile_path)
state_name = 'New York' #'California'
original_state = states[states['NAME'] == state_name] 

# original_bounds: [-125, -114, 32, 43]
original_bounds = original_state.total_bounds
minx_orig, miny_orig, maxx_orig, maxy_orig = original_bounds   

# %%
# shifting

# Step 1: Convert to UTM (Zone 18N)
utm_crs = "EPSG:32618"  # UTM Zone 18N
original_state_utm = original_state.to_crs(utm_crs)

# Step 2: Translate the shape to a new latitude
# Latitude difference in meters: 1 degree latitude ≈ 111,000 meters
original_lat = 42.5  # Approximate center latitude of NY State
new_lat = -55  # Desired latitude (55°S)
lat_shift_meters = (new_lat - original_lat) * 111_000

# Apply the shift in the northing (y-coordinate)
ny_shifted_utm = original_state_utm.copy()
ny_shifted_utm["geometry"] = ny_shifted_utm.geometry.apply(
    lambda geom: translate(geom, xoff=0, yoff=lat_shift_meters)
)

# Step 3: Reproject back to geographic coordinates (EPSG:4326)
shifted_state = ny_shifted_utm.to_crs("EPSG:4326")

# Validate the new bounds
shifted_bounds = shifted_state.total_bounds
print("Shifted Geometry Bounds (degrees):", shifted_state.total_bounds)

minx_shifted, miny_shifted, maxx_shifted, maxy_shifted = shifted_state.total_bounds 


# %%
# Ensure area calculations are performed in an Equal-Area CRS
# Step 1: Reproject to an Equal-Area CRS
equal_area_crs = "EPSG:2163"  # US National Atlas Equal Area projection
original_state_equal_area = original_state.to_crs(equal_area_crs)
shifted_state_equal_area = shifted_state.to_crs(equal_area_crs)

# Step 2: Compute areas in the Equal-Area CRS
original_area = original_state_equal_area.geometry.area.sum()  # Area in square meters
shifted_area = shifted_state_equal_area.geometry.area.sum()  # Area in square meters

# Step 3: Compare areas
print(f"Original Area: {original_area:.2f} square meters")
print(f"Shifted Area: {shifted_area:.2f} square meters")

# Verify area consistency within a tolerance
tolerance = 0.01  # 1% tolerance
if abs((shifted_area - original_area) / original_area) < tolerance:
    print("Areas match within the acceptable tolerance.")
else:
    print("Area mismatch detected! Check the shifting process.")


# %%
# Plot the original and shifted shapes side by side
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig, axes = plt.subplots(1, 2, figsize=(16, 8), subplot_kw={'projection': ccrs.Orthographic(-90, 0)})

# Plot original State
axes[0].set_extent([minx_orig, maxx_orig, miny_orig, maxy_orig])  # Bounding box for original NY
axes[0].add_feature(cfeature.COASTLINE)
axes[0].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
original_state.plot(ax=axes[0], color='blue', transform=ccrs.PlateCarree())
axes[0].set_title(f"Original {state_name} State")

# Plot shifted State
# axes[1].set_extent([minx_orig, maxx_orig, miny_shifted, maxy_shifted])
axes[1].set_extent([minx_shifted,  maxx_shifted, miny_shifted, maxy_shifted])  # Bounding box for shifted NY
axes[1].add_feature(cfeature.COASTLINE)
axes[1].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
shifted_state.plot(ax=axes[1], color='red', transform=ccrs.PlateCarree())
axes[1].set_title(f"{state_name} State at Latitude 55°S")

plt.tight_layout()
# plt.show()
plt.savefig(f'../img/shifted_{state_name}_state.png')
# %%
