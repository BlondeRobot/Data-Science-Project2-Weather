# python script to generate synthetic device data can be adapted and re-used to create other synth datasets

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Create device_id from 900001 to 900450
device_id = np.arange(900001, 900451)

# component_1: 70% 1001, 30% 1002
component_1 = np.random.choice([1001, 1002], size=450, p=[0.7, 0.3])

# component_2: random between 2001 or 2002
component_2 = np.random.choice([2001, 2002], size=450)

# component_3: 50% 3001, 30% 3002, 20% 3003
component_3 = np.random.choice([3001, 3002, 3003], size=450, p=[0.5, 0.3, 0.2])

# location_id: random between 1 and 400
location_id = np.random.randint(1, 401, size=450)

# Create DataFrame
device_df = pd.DataFrame({
    'device_id': device_id,
    'component_1': component_1,
    'component_2': component_2,
    'component_3': component_3,
    'location_id': location_id
})

# Save to CSV
device_df.to_csv('device.csv', index=False)