import pandas as pd
import numpy as np
import sys
from scipy.spatial import KDTree

# Define file paths (Corrected assignments - single line)
loc_file = 'synth_data/location.csv'
weather_file1 = 'meteo_data/weather_20230501_20240430.csv'
weather_file2 = 'meteo_data/weather_20240501_20250428.csv'
output_file = 'meteo_data/historical_weather_load.csv'

# Define number of metadata lines to read and data lines to skip
metadata_rows = 400 # Number of rows containing location metadata
skip_rows_weather = metadata_rows + 2 # Skip metadata + blank line + header

# No distance threshold needed now, map all records to nearest neighbor

print(f"Reading location data from {loc_file}...")
try:
    df_loc = pd.read_csv(loc_file)
except FileNotFoundError:
    print(f"Error: Location file not found at {loc_file}")
    sys.exit(1)
except Exception as e:
    print(f"Error reading location file {loc_file}: {e}")
    sys.exit(1)

# Prepare location data for KDTree (Corrected column list - single line)
loc_coords = df_loc[['lat', 'long']].values
loc_ids = df_loc['location_id'].values

print("Building KDTree for location coordinates...")
loc_kdtree = KDTree(loc_coords)
print(f"Location data loaded and KDTree built. Shape: {df_loc.shape}")

def process_weather_file(filepath, metadata_rows, skip_rows_weather, loc_kdtree, loc_ids):
    """Reads metadata, weather data, maps coordinates using nearest neighbor (no threshold), and selects columns."""
    print(f"Processing file: {filepath}")

    try:
        # 1. Read metadata to get internal location_id -> lat/lon mapping
        print("  Reading metadata...")
        df_meta = pd.read_csv(filepath, nrows=metadata_rows)
        # Corrected column check (single line)
        if 'location_id' not in df_meta.columns or 'latitude' not in df_meta.columns or 'longitude' not in df_meta.columns:
             # Corrected print statement (single line)
             print(f"  Error: Metadata in {filepath} missing required columns (location_id, latitude, longitude).")
             return None
        # Corrected column selection and index setting (single line)
        df_meta = df_meta[['location_id', 'latitude', 'longitude']].drop_duplicates('location_id').set_index('location_id')
        print(f"  Metadata read. Shape: {df_meta.shape}")

        # 2. Read weather data
        print(f"  Reading weather data (skipping {skip_rows_weather} rows)...")
        df_weather = pd.read_csv(filepath, skiprows=skip_rows_weather)
        # Corrected column check and rename (single line)
        if 'location_id' in df_weather.columns:
            df_weather.rename(columns={'location_id': 'internal_location_id'}, inplace=True)
        else:
            # Corrected print statement (single line)
            print(f"  Error: Weather data section in {filepath} missing 'location_id' column.")
            return None
        print(f"  Weather data read. Shape: {df_weather.shape}")

        # 3. Merge weather data with metadata to add lat/lon
        print("  Merging weather data with metadata coordinates...")
        # Corrected merge call (single line)
        df_weather = df_weather.merge(df_meta, left_on='internal_location_id', right_index=True, how='left')

        # Drop rows where metadata merge failed (shouldn't happen if files are consistent)
        # Corrected dropna call (single line)
        df_weather.dropna(subset=['latitude', 'longitude'], inplace=True)
        if df_weather.empty:
            print("  Warning: No weather records remained after merging with metadata.")
            return None

        # Check if essential columns exist after merge
        # Corrected column list (single line)
        required_weather_cols = [
            'latitude', 'longitude', 'time',
            'shortwave_radiation_sum (MJ/m²)', 'temperature_2m_max (°C)',
            'precipitation_sum (mm)', 'relative_humidity_2m_mean (%)',
            'temperature_2m_mean (°C)', 'temperature_2m_min (°C)'
        ]
        missing_cols = [col for col in required_weather_cols if col not in df_weather.columns]
        if missing_cols:
            # Corrected print statement (single line)
            print(f"  Error: Missing required columns after merging metadata: {missing_cols}")
            return None # Return None to indicate failure

        # 4. Find nearest neighbor using KDTree
        print("  Mapping weather data to final location IDs using nearest neighbor...")
        # Corrected column selection (single line)
        weather_coords = df_weather[['latitude', 'longitude']].values
        # Query for the index of the nearest neighbor
        distances, indices = loc_kdtree.query(weather_coords, k=1)

        # Assign the location_id of the nearest neighbor directly
        # Corrected assignment (single line)
        df_weather['location_id'] = loc_ids[indices].astype(int)
        # We can optionally keep the distance if needed for analysis, but it's not used for filtering
        # df_weather['distance'] = distances

        # 5. Select and return final columns (No filtering step needed now)
        # Corrected column list (single line)
        output_columns = [
            'location_id', 'time',
            'shortwave_radiation_sum (MJ/m²)', 'temperature_2m_max (°C)',
            'precipitation_sum (mm)', 'relative_humidity_2m_mean (%)',
            'temperature_2m_mean (°C)', 'temperature_2m_min (°C)'
        ]

        # Check if all output columns are present before selecting
        missing_output_cols = [col for col in output_columns if col not in df_weather.columns]
        if missing_output_cols:
            # Corrected print statement (single line)
            print(f"  Error: Missing final output columns: {missing_output_cols}")
            return None

        # Corrected return statement (single line)
        return df_weather[output_columns].copy()

    except FileNotFoundError:
        print(f"Error: Weather file not found at {filepath}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: Weather file {filepath} is empty or contains no data after skipping rows.")
        return None
    except Exception as e:
        print(f"An error occurred while processing {filepath}: {e}")
        # import traceback
        # traceback.print_exc()
        return None


# Process both weather files
# Corrected function calls (single line)
df_processed1 = process_weather_file(weather_file1, metadata_rows, skip_rows_weather, loc_kdtree, loc_ids)
df_processed2 = process_weather_file(weather_file2, metadata_rows, skip_rows_weather, loc_kdtree, loc_ids)

# Combine results if both processed successfully
valid_dfs = []
if df_processed1 is not None and not df_processed1.empty:
    valid_dfs.append(df_processed1)
else:
    # Corrected print statement (single line)
    print(f"Warning: Processing failed or resulted in empty data for {weather_file1}")

if df_processed2 is not None and not df_processed2.empty:
    valid_dfs.append(df_processed2)
else:
    # Corrected print statement (single line)
    print(f"Warning: Processing failed or resulted in empty data for {weather_file2}")

if not valid_dfs:
    # Corrected print statement (single line)
    print("Script failed: No data could be processed successfully from either weather file.")
    sys.exit(1)

print("Concatenating processed weather data...")
df_final = pd.concat(valid_dfs, ignore_index=True)
print(f"Combined processed data shape: {df_final.shape}")

if df_final.empty:
    # Corrected print statement (single line)
    print("Error: Final combined data frame is empty after concatenation.")
    sys.exit(1)

print("Generating sequential measurement_id...")
# Add measurement_id (starting from 1)
# Corrected insert call (single line)
df_final.insert(0, 'measurement_id', range(1, len(df_final) + 1))

print(f"Final data shape: {df_final.shape}")

print(f"Saving final data to {output_file}...")
try:
    # Corrected to_csv call (single line)
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    print("Script finished successfully.")
except Exception as e:
    print(f"Error saving final data to {output_file}: {e}")
    sys.exit(1)