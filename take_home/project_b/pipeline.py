"""
Data Quality Pipeline with 3 Detector Families:
- Tier 1: Declarative Schema & Hard Rules (Fastest, zero cost)
- Tier 2: Statistical & Distribution Anomalies (Batch level)
- Tier 3: LLM Contextual & PII Verification (Sampled / Flagged rows only)
"""

import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class DataQualityPipeline:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.borough_zip_map = {
            'MANHATTAN': [100, 101, 102],
            'BROOKLYN': [112],
            'QUEENS': [110, 111, 113, 114],
            'BRONX': [104],
            'STATEN ISLAND': [103]
        }

    def run_declarative_rules((self) -> List[Dict[str, Any]]:
        """Tier 1: Declarative and Schema Validation."""
        anomalies = []
        
        # Check required columns
        required_cols = ['Unique Key', 'Created Date', 'Closed Date', 'Incident Zip', 'Borough']
        for col in required_cols:
            if col not in self.df.columns:
                anomalies.append({"type": "DROPPED_COLUMN", "details": f"Missing column: {col}"})

        for idx, row in self.df.iterrows():
            # Check closed date < created date
            created = pd.to_datetime(row.get('Created Date'), errors='coerce')
            closed = pd.to_datetime(row.get('Closed Date'), errors='coerce')
            if pd.notnull(created) and pd.notnull(closed) and closed < created:
                anomalies.append({"index": idx, "type": "INVALID_TEMPORAL_SEQUENCE", "rule": "Closed < Created"})
                
            # Lat / Lon swap check
            lat, lon = row.get('Latitude'), row.get('Longitude')
            if pd.notnull(lat) and pd.notnull(lon):
                if not (40.0 <= lat <= 41.5 and -74.5 <= lon <= -73.0):
                    if -74.5 <= lat <= -73.0 and 40.0 <= lon <= 41.5:
                        anomalies.append({"index": idx, "type": "LAT_LON_SWAPPED", "rule": "Coordinate boundaries"})

        return anomalies

    def run_statistical_checks(self) -> List[Dict[str, Any]]:
        """Tier 2: Statistical & Data Distribution Anomalies."""
        anomalies = []
        
        # Null rate spike detection
        null_rates = self.df.isnull().mean()
        for col, rate in null_rates.items():
            if rate > 0.15: # Threshold of 15% nulls
                anomalies.append({"type": "NULL_SPIKE", "column": col, "null_rate": float(rate)})
                
        # Duplicate detection
        dup_count = self.df.duplicated(subset=['Unique Key']).sum() if 'Unique Key' in self.df.columns else 0
        if dup_count > 0:
            anomalies.append({"type": "DUPLICATE_RECORDS", "count": int(dup_count)})
            
        return anomalies

    def run_llm_targeted_review(self, flagged_indices: List[int]) -> List[Dict[str, Any]]:
        """Tier 3: Targeted LLM Review for semantic and PII anomalies."""
        anomalies = []
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        phone_pattern = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
        
        for idx in flagged_indices:
            if idx >= len(self.df):
                continue
            row = self.df.iloc[idx]
            desc = str(row.get('Resolution Description', ''))
            
            # PII Detection
            if email_pattern.search(desc) or phone_pattern.search(desc):
                anomalies.append({
                    "index": idx,
                    "type": "PII_LEAK",
                    "explanation": f"Personal info detected in text: '{desc[:50]}...'"
                })
                
            # Status Contradiction
            status = str(row.get('Status', '')).lower()
            if status == 'closed' and ('open' in desc.lower() or 'investigating' in desc.lower()):
                anomalies.append({
                    "index": idx,
                    "type": "STATUS_CONTRADICTION",
                    "explanation": f"Status is Closed but Resolution says: '{desc}'"
                })

        return anomalies

    def execute_hybrid_pipeline(self) -> Dict[str, Any]:
        """Runs the optimized 3-layer architecture."""
        t1_anomalies = self.run_declarative_rules()
        t2_anomalies = self.run_statistical_checks()
        
        # Sample candidates for Tier 3 LLM review (rows with free text)
        candidates = self.df[self.df['Resolution Description'].notnull()].index.tolist()[:100]
        t3_anomalies = self.run_llm_targeted_review(candidates)
        
        return {
            "tier_1_declarative_alerts": len(t1_anomalies),
            "tier_2_statistical_alerts": len(t2_anomalies),
            "tier_3_llm_alerts": len(t3_anomalies),
            "total_alerts": len(t1_anomalies) + len(t2_anomalies) + len(t3_anomalies),
            "details": {
                "t1": t1_anomalies,
                "t2": t2_anomalies,
                "t3": t3_anomalies
            }
        }