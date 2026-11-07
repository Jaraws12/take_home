"""
Data Corruption Injector for NYC 311 Service Requests.
Injects 12 distinct failure modes into standard pandas DataFrames at precise rates.
"""

import pandas as pd
import numpy as np
from datetime import timedelta

class DataCorruptionInjector:
    def __init__(self, seed: int = 42):
        np.random.seed(seed)

    def inject_anomalies(self, df: pd.DataFrame, injection_rate: float = 0.05) -> pd.DataFrame:
        corrupted = df.copy()
        n_rows = len(corrupted)
        n_corrupt = max(1, int(n_rows * injection_rate))
        
        indices = np.random.choice(n_rows, size=n_corrupt, replace=False)
        
        # 1. Renamed or dropped column
        if 'Agency' in corrupted.columns:
            corrupted = corrupted.rename(columns={'Agency': 'Agency_Name_Renamed'})
            
        # 2. Column type change (Numbers as strings)
        corrupted['Incident Zip'] = corrupted['Incident Zip'].astype(str)
        
        # 3. Date format switch partway
        corrupted.iloc[indices[:2], corrupted.columns.get_loc('Created Date')] = '2023/12/31 23:59:59'
        
        # 4. Lat/Lon swapped
        if 'Latitude' in corrupted.columns and 'Longitude' in corrupted.columns:
            swap_idx = indices[2:4]
            tmp = corrupted.loc[swap_idx, 'Latitude'].copy()
            corrupted.loc[swap_idx, 'Latitude'] = corrupted.loc[swap_idx, 'Longitude']
            corrupted.loc[swap_idx, 'Longitude'] = tmp

        # 5. Exact duplicates
        corrupted = pd.concat([corrupted, corrupted.iloc[indices[4:6]]], ignore_index=True)

        # 6. Near duplicates
        near_dup = corrupted.iloc[indices[6:8]].copy()
        near_dup['Created Date'] = pd.to_datetime(near_dup['Created Date']) + timedelta(seconds=5)
        corrupted = pd.concat([corrupted, near_dup], ignore_index=True)

        # 7. Null spike
        corrupted.loc[indices[8:12], 'Borough'] = np.nan

        # 8. Closed date earlier than created date
        if 'Closed Date' in corrupted.columns:
            corrupted.loc[indices[12:15], 'Closed Date'] = pd.to_datetime(corrupted.loc[indices[12:15], 'Created Date']) - timedelta(days=2)

        # 9. ZIP inconsistent with borough
        corrupted.loc[indices[15:17], 'Incident Zip'] = '90210' # Beverly Hills zip in NYC dataset
        corrupted.loc[indices[15:17], 'Borough'] = 'MANHATTAN'

        # 10. Complaint type inconsistent with descriptor
        corrupted.loc[indices[17:19], 'Complaint Type'] = 'Noise - Residential'
        corrupted.loc[indices[17:19], 'Descriptor'] = 'Water Leakage from Ceiling'

        # 11. Resolution description contradicting status
        corrupted.loc[indices[19:21], 'Status'] = 'Closed'
        corrupted.loc[indices[19:21], 'Resolution Description'] = 'The issue is currently open and being actively investigated by officers.'

        # 12. PII Leakage inside free-text
        corrupted.loc[indices[21:23], 'Resolution Description'] = 'Contact technician John Doe at john.doe@nyc.gov or call 555-0199.'

        return corrupted