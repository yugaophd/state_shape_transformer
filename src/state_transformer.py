# %%
from shapely.geometry import shape, mapping
from shapely.ops import transform
import geopandas as gpd
import pyproj
from shapely.affinity import translate
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#######Change the path to the directory where the source code is stored #######
import os
os.chdir('/Users/yugao/Desktop/projects/state_shape_transformer/src')
# get user home directory
home = os.path.expanduser("~")
# os.chdir(home+'/Python/state_shape_transformer/src')

# %%
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

# %% 
# plot in m east and north
fig, ax = plt.subplots()
original_state_utm.plot(ax=ax)
plt.xlabel('Easting (m)')
plt.ylabel('Northing (m)')
plt.title(f"{state_name} State in UTM")
plt.show()

# %%
# Step 2: Translate the shape to a new latitude
# Latitude difference in meters: 1 degree latitude ≈ 111,000 meters
original_lat = 42.5  # Approximate center latitude of NY State
new_lat = -55  # Desired latitude (55°S)
lat_shift_meters = (new_lat - original_lat) * 111_000

# Apply the shift in the northing (y-coordinate)
shifted_state = original_state_utm.copy()
shifted_state["geometry"] = shifted_state.geometry.apply(
    lambda geom: translate(geom, xoff=0, yoff=lat_shift_meters)
)

# Step 3: Reproject back to geographic coordinates (EPSG:4326)
# shifted_state = shifted_state.to_crs("EPSG:4326")

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

# Create two subplots for original and shifted states
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Plot original state outline
original_state.boundary.plot(ax=axes[0], color='blue')
axes[0].set_title(f"Original {state_name} State")
axes[0].set_xlabel("degree east")
axes[0].set_ylabel("degree north")

# Plot shifted state outline
shifted_state.boundary.plot(ax=axes[1], color='red')
axes[1].set_title(f"{state_name} State at Latitude 55°S")
axes[1].set_xlabel("East (m)")
axes[1].set_ylabel("North (m)")

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig(f'../img/shifted_{state_name}_state.png')

# %%
