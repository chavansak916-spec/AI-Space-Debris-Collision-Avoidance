# ============================================================
# SPACE DEBRIS COLLISION DETECTION SYSTEM
# Collision Detection + Closest Approach + Relative Velocity
# + Risk Assessment + Warning
# ============================================================

import pandas as pd
import numpy as np


# ============================================================
# STEP 1 - FILE NAMES
# ============================================================

POSITION_FILE = "positions.csv"
JSON_FILE = "positions.json"
REFERENCE_FILE = "collision_results.csv"


# ============================================================
# STEP 2 - RISK ASSESSMENT
# Everything is inside collision.py
# No separate risk_assessment.py is needed
# ============================================================

def assess_risk(distance_km):

    # These are simple prototype thresholds

    if distance_km < 10:
        return "HIGH"

    elif distance_km < 50:
        return "MEDIUM"

    else:
        return "LOW"


# ============================================================
# STEP 3 - WARNING MESSAGE
# ============================================================

def display_warning(risk_level, distance_km):

    print()
    print("=" * 60)
    print("                RISK ASSESSMENT")
    print("=" * 60)

    print(f"Minimum distance : {distance_km:.3f} km")
    print(f"Risk level       : {risk_level}")

    print()

    if risk_level == "HIGH":

        print("WARNING: HIGH COLLISION RISK!")
        print("Immediate further analysis is required.")

    elif risk_level == "MEDIUM":

        print("CAUTION: MEDIUM COLLISION RISK.")
        print("Continue monitoring the object.")

    else:

        print("STATUS: LOW COLLISION RISK.")
        print("No immediate prototype warning.")

    print("=" * 60)


# ============================================================
# STEP 4 - START PROGRAM
# ============================================================

print()
print("=" * 60)
print("       SPACE DEBRIS COLLISION DETECTION")
print("=" * 60)


# ============================================================
# STEP 5 - LOAD positions.csv
# ============================================================

print("\nLoading positions.csv...")

try:

    data = pd.read_csv(POSITION_FILE)

except FileNotFoundError:

    print()
    print("ERROR: positions.csv was not found.")
    print("Make sure positions.csv is in the same folder as collision.py.")

    exit()


print("positions.csv loaded successfully.")

print(
    "Total position records:",
    len(data)
)


# ============================================================
# STEP 6 - CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [

    "object",
    "id",
    "minutes",

    "x_km",
    "y_km",
    "z_km",

    "vx_km_s",
    "vy_km_s",
    "vz_km_s"

]


missing_columns = []


for column in required_columns:

    if column not in data.columns:

        missing_columns.append(column)


if missing_columns:

    print()
    print("ERROR: Some required columns are missing.")

    print(
        "Missing columns:",
        missing_columns
    )

    exit()


print("All required columns are available.")


# ============================================================
# STEP 7 - LOAD positions.json
# ============================================================

print("\nLoading positions.json...")

try:

    json_data = pd.read_json(
        JSON_FILE
    )

    print(
        "positions.json loaded successfully."
    )

    print(
        "JSON records:",
        len(json_data)
    )

except FileNotFoundError:

    print(
        "WARNING: positions.json was not found."
    )

    json_data = None


# ============================================================
# STEP 8 - LOAD collision_results.csv
# ============================================================

print("\nLoading collision_results.csv...")

try:

    reference_data = pd.read_csv(
        REFERENCE_FILE
    )

    print(
        "collision_results.csv loaded successfully."
    )

    print(
        "Reference records:",
        len(reference_data)
    )

except FileNotFoundError:

    print(
        "WARNING: collision_results.csv was not found."
    )

    reference_data = None


# ============================================================
# STEP 9 - FIND THE SATELLITE
# ============================================================

SATELLITE_NAME = "ISS (ZARYA)"


satellite_data = data[

    data["object"]
    ==
    SATELLITE_NAME

].copy()


if satellite_data.empty:

    print()
    print(
        "ERROR: ISS (ZARYA) was not found in positions.csv"
    )

    exit()


print()
print("Satellite found:")

print(
    SATELLITE_NAME
)


# ============================================================
# STEP 10 - FIND DEBRIS
# ============================================================

DEBRIS_NAME = "COSMOS 2251 DEB"


all_debris_data = data[

    data["object"]
    ==
    DEBRIS_NAME

].copy()


if all_debris_data.empty:

    print()
    print(
        "ERROR: COSMOS 2251 DEB data was not found."
    )

    exit()


debris_ids = sorted(

    all_debris_data[
        "id"
    ].unique()

)


print()
print("Debris IDs found:")


for debris_id in debris_ids:

    print(
        f"- {debris_id}"
    )


# ============================================================
# STEP 11 - COLLISION CALCULATION FUNCTION
# ============================================================

def calculate_collision(
    satellite,
    debris
):

    # --------------------------------------------------------
    # Match satellite and debris at the same time
    # --------------------------------------------------------

    merged = pd.merge(

        satellite,

        debris,

        on="minutes",

        suffixes=(
            "_satellite",
            "_debris"
        )

    )


    if merged.empty:

        return None


    # --------------------------------------------------------
    # Get satellite X Y Z
    # --------------------------------------------------------

    satellite_positions = merged[

        [
            "x_km_satellite",
            "y_km_satellite",
            "z_km_satellite"
        ]

    ].to_numpy(
        dtype=float
    )


    # --------------------------------------------------------
    # Get debris X Y Z
    # --------------------------------------------------------

    debris_positions = merged[

        [
            "x_km_debris",
            "y_km_debris",
            "z_km_debris"
        ]

    ].to_numpy(
        dtype=float
    )


    # --------------------------------------------------------
    # Position difference
    # --------------------------------------------------------

    difference = (

        satellite_positions
        -
        debris_positions

    )


    # --------------------------------------------------------
    # Calculate 3D distance
    #
    # d = sqrt(dx^2 + dy^2 + dz^2)
    # --------------------------------------------------------

    distances = np.linalg.norm(

        difference,

        axis=1

    )


    # --------------------------------------------------------
    # Find closest approach
    # --------------------------------------------------------

    closest_index = int(

        np.argmin(
            distances
        )

    )


    minimum_distance = float(

        distances[
            closest_index
        ]

    )


    closest_time = float(

        merged.iloc[
            closest_index
        ]["minutes"]

    )


    # --------------------------------------------------------
    # Satellite velocity
    # --------------------------------------------------------

    satellite_velocity = merged.iloc[
        closest_index
    ][

        [
            "vx_km_s_satellite",
            "vy_km_s_satellite",
            "vz_km_s_satellite"
        ]

    ].to_numpy(
        dtype=float
    )


    # --------------------------------------------------------
    # Debris velocity
    # --------------------------------------------------------

    debris_velocity = merged.iloc[
        closest_index
    ][

        [
            "vx_km_s_debris",
            "vy_km_s_debris",
            "vz_km_s_debris"
        ]

    ].to_numpy(
        dtype=float
    )


    # --------------------------------------------------------
    # Relative velocity
    # --------------------------------------------------------

    velocity_difference = (

        satellite_velocity
        -
        debris_velocity

    )


    relative_velocity = float(

        np.linalg.norm(
            velocity_difference
        )

    )


    # --------------------------------------------------------
    # Risk assessment
    # --------------------------------------------------------

    risk_level = assess_risk(

        minimum_distance

    )


    # --------------------------------------------------------
    # Return the result
    # --------------------------------------------------------

    return {

        "time":
            closest_time,

        "distance":
            minimum_distance,

        "relative_velocity":
            relative_velocity,

        "risk":
            risk_level

    }


# ============================================================
# STEP 12 - CHECK ALL DEBRIS OBJECTS
# ============================================================

results = []


print()
print("=" * 60)
print("             CHECKING DEBRIS OBJECTS")
print("=" * 60)


for debris_id in debris_ids:

    print()
    print(
        f"Checking debris ID: {debris_id}"
    )


    current_debris = all_debris_data[

        all_debris_data["id"]
        ==
        debris_id

    ].copy()


    result = calculate_collision(

        satellite_data,

        current_debris

    )


    if result is None:

        print(
            "No matching time points found."
        )

        continue


    # Store debris ID

    result[
        "debris_id"
    ] = debris_id


    results.append(
        result
    )


    # --------------------------------------------------------
    # Display each debris result
    # --------------------------------------------------------

    print(
        f"Closest time       : "
        f"{result['time']:.2f} minutes"
    )

    print(
        f"Minimum distance   : "
        f"{result['distance']:.3f} km"
    )

    print(
        f"Relative velocity  : "
        f"{result['relative_velocity']:.3f} km/s"
    )

    print(
        f"Risk level         : "
        f"{result['risk']}"
    )


# ============================================================
# STEP 13 - MAKE SURE RESULTS EXIST
# ============================================================

if len(results) == 0:

    print()
    print(
        "ERROR: No collision results were generated."
    )

    exit()


# ============================================================
# STEP 14 - FIND OVERALL CLOSEST OBJECT
# ============================================================

closest_result = min(

    results,

    key=lambda result:
        result[
            "distance"
        ]

)


# ============================================================
# STEP 15 - FINAL RESULT
# ============================================================

print()
print()
print("=" * 60)
print("                 FINAL RESULT")
print("=" * 60)


print(
    f"Satellite          : "
    f"{SATELLITE_NAME}"
)


print(
    f"Closest debris ID  : "
    f"{closest_result['debris_id']}"
)


print(
    f"Closest time       : "
    f"{closest_result['time']:.2f} minutes"
)


print(
    f"Minimum distance   : "
    f"{closest_result['distance']:.3f} km"
)


print(
    f"Relative velocity  : "
    f"{closest_result['relative_velocity']:.3f} km/s"
)


print(
    f"Risk level         : "
    f"{closest_result['risk']}"
)


# ============================================================
# STEP 16 - DISPLAY RISK WARNING
# ============================================================

display_warning(

    closest_result[
        "risk"
    ],

    closest_result[
        "distance"
    ]

)


# ============================================================
# STEP 17 - SAVE FINAL RESULTS
# ============================================================

final_results = pd.DataFrame(

    results

)


final_results = final_results[

    [
        "debris_id",
        "time",
        "distance",
        "relative_velocity",
        "risk"
    ]

]


final_results.to_csv(

    "final_collision_results.csv",

    index=False

)


print()
print(
    "Results saved successfully."
)

print(
    "Created file: final_collision_results.csv"
)


# ============================================================
# STEP 18 - END
# ============================================================

print()
print("=" * 60)
print("       COLLISION DETECTION COMPLETE")
print("=" * 60)