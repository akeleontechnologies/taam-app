"""
Service for filtering TAAM data by demographics.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from collections import Counter

from apps.ingest.services import parse_uploaded_file, dataframe_to_records
from apps.charts.taam_service import determine_persona
from apps.charts.constants import PERSONA_PROTOTYPES


def get_filter_options(file_path: str) -> Dict[str, List[str]]:
    """
    Get unique values for filter fields from CSV.
    
    Returns:
        {
            'age_groups': [...],
            'genders': [...],
            'emirates': [...]
        }
    """
    df, _, error = parse_uploaded_file(file_path)
    
    if error or df is None:
        return {'age_groups': [], 'genders': [], 'emirates': []}
    
    # Get unique values (handling different column name variations)
    age_col = None
    gender_col = None
    emirate_col = None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if 'age' in col_lower:  # Match 'age', 'age_group', 'q2_age_group', etc.
            age_col = col
        elif 'gender' in col_lower:  # Match 'gender', 'q3_gender', etc.
            gender_col = col
        elif 'emirate' in col_lower:  # Match 'emirate', 'q1_emirate', etc.
            emirate_col = col
    
    print(f"DEBUG: Found columns - age: {age_col}, gender: {gender_col}, emirate: {emirate_col}")
    
    return {
        'age_groups': sorted([str(x) for x in df[age_col].dropna().unique().tolist()]) if age_col else [],
        'genders': sorted([str(x) for x in df[gender_col].dropna().unique().tolist()]) if gender_col else [],
        'emirates': sorted([str(x) for x in df[emirate_col].dropna().unique().tolist()]) if emirate_col else [],
    }


def get_filtered_distribution(
    file_path: str,
    age_group: Optional[str] = None,
    gender: Optional[str] = None,
    emirate: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get persona distribution with optional demographic filters.
    
    Args:
        file_path: Path to CSV file
        age_group: Filter by age group (e.g., "26-30")
        gender: Filter by gender (e.g., "Female")
        emirate: Filter by emirate (e.g., "Ras Al-Khaimah")
        
    Returns:
        {
            'total_respondents': int,
            'filtered_respondents': int,
            'distribution': [{persona, count, percentage}, ...],
            'filters_applied': {...}
        }
    """
    df, _, error = parse_uploaded_file(file_path)
    
    if error or df is None:
        return {
            'total_respondents': 0,
            'filtered_respondents': 0,
            'distribution': [],
            'filters_applied': {},
            'error': error
        }
    
    total_respondents = len(df)
    
    # Apply filters
    filtered_df = df.copy()
    filters_applied = {}
    
    if age_group:
        age_cols = [col for col in df.columns if 'age' in str(col).lower()]  # Remove 'group' requirement
        if age_cols:
            filtered_df = filtered_df[filtered_df[age_cols[0]] == age_group]
            filters_applied['age_group'] = age_group
            print(f"DEBUG: Filtered by age={age_group}, remaining rows: {len(filtered_df)}")
    
    if gender:
        gender_cols = [col for col in df.columns if 'gender' in str(col).lower()]
        if gender_cols:
            filtered_df = filtered_df[filtered_df[gender_cols[0]] == gender]
            filters_applied['gender'] = gender
            print(f"DEBUG: Filtered by gender={gender}, remaining rows: {len(filtered_df)}")
    
    if emirate:
        emirate_cols = [col for col in df.columns if 'emirate' in str(col).lower()]
        if emirate_cols:
            filtered_df = filtered_df[filtered_df[emirate_cols[0]] == emirate]
            filters_applied['emirate'] = emirate
            print(f"DEBUG: Filtered by emirate={emirate}, remaining rows: {len(filtered_df)}")
    
    # Count personas in filtered data
    records = dataframe_to_records(filtered_df)
    persona_counts = Counter()
    
    for record in records:
        _, persona_name, _, _ = determine_persona(record)
        if persona_name and persona_name != 'Unknown':
            persona_counts[persona_name] += 1
    
    filtered_total = sum(persona_counts.values())
    
    # Build distribution in A..J order
    distribution = []
    persona_codes_order = sorted(PERSONA_PROTOTYPES.keys())
    
    for code in persona_codes_order:
        persona_name = PERSONA_PROTOTYPES[code]['name']
        count = int(persona_counts.get(persona_name, 0))
        percentage = round((count / filtered_total * 100), 2) if filtered_total > 0 else 0.0
        
        distribution.append({
            'persona': persona_name,
            'persona_code': code,
            'count': count,
            'percentage': percentage
        })
    
    return {
        'total_respondents': total_respondents,
        'filtered_respondents': filtered_total,
        'distribution': distribution,
        'filters_applied': filters_applied
    }
