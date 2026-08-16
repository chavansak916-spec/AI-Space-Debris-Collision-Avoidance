import pandas as pd
import numpy as np


# STEP 1 - Read Member 2 data
data = pd.read_csv("positions.csv")


# STEP 2 - Show objects
objects = data["object"].unique()

print("Objects found:")
print(objects)


# STEP 3 - Get satellite data
satellite = data[
    data["object"] == "ISS (ZARYA)"
]


# STEP 4 - Select one debris
debris_id = 33757

debris = data[
    data["id"] == debris_id
]


# STEP 5 - Match satellite and debris by time
combined = pd.merge(
    satellite,
    debris,
    on="minutes",
    suffixes=("_satellite", "_debris")
)


# STEP 6 - Get satellite positions
satellite_positions = combined[
    [
        "x_km_satellite",
        "y_km_satellite",
        "z_km_satellite"
    ]
].to_numpy()


# STEP 7 - Get debris positions
debris_positions = combined[
    [
        "x_km_debris",
        "y_km_debris",
        "z_km_debris"
    ]
].to_numpy()


# STEP 8 - Calculate position difference
difference = (
    satellite_positions -
    debris_positions
)


# STEP 9 - Calculate distance
distances = np.linalg.norm(
    difference,
    axis=1
)


# STEP 10 - Find closest approach
closest_index = np.argmin(distances)

minimum_distance = distances[
    closest_index
]


# STEP 11 - Find time
closest_time = combined.iloc[
    closest_index
]["minutes"]


# STEP 12 - Risk level
if minimum_distance < 10:

    risk = "HIGH"

elif minimum_distance < 50:

    risk = "MEDIUM"

else:

    risk = "LOW"


# STEP 13 - Display result
print("\n================================")
print("   COLLISION DETECTION RESULT")
print("================================")

print("Satellite: ISS (ZARYA)")
print("Debris ID:", debris_id)

print(
    f"Closest approach time: "
    f"{closest_time:.2f} minutes"
)

print(
    f"Minimum distance: "
    f"{minimum_distance:.3f} km"
)

print("Risk level:", risk)

print("================================")