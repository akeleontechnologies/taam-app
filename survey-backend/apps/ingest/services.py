"""
File Parsing Service - Handles CSV/XLSX file uploads and parsing with pandas.
"""
import os
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from apps.charts.constants import COLUMN_MAPPINGS, CORE_TAAM_QUESTIONS, MIN_TAAM_QUESTIONS


def normalize_column_name(col: str) -> str:
    """
    Normalize a column name to standard format.
    
    Args:
        col: Original column name
        
    Returns:
        Normalized column name (lowercase, underscores)
    """
    return str(col).lower().strip().replace(' ', '_').replace('-', '_')


def map_column_to_standard(col: str) -> Optional[str]:
    """
    Map a column name to its standard TAAM question key.
    
    Args:
        col: Original column name
        
    Returns:
        Standard key (e.g., 'q8', 'q20') or None
    """
    normalized = normalize_column_name(col)
    
    # Check exact match first
    for standard_key, variations in COLUMN_MAPPINGS.items():
        if normalized in [v.lower() for v in variations]:
            return standard_key
    
    # Check if column contains the key
    for standard_key, variations in COLUMN_MAPPINGS.items():
        for variation in variations:
            if variation.lower() in normalized or normalized in variation.lower():
                return standard_key
    
    return None


def detect_file_type(uploaded_file: UploadedFile) -> str:
    """
    Detect if file is CSV or XLSX.
    
    Args:
        uploaded_file: Django uploaded file object
        
    Returns:
        'csv' or 'xlsx'
    """
    filename = uploaded_file.name.lower()
    if filename.endswith('.csv'):
        return 'csv'
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        return 'xlsx'
    
    # Try by MIME type
    mime = uploaded_file.content_type.lower() if uploaded_file.content_type else ''
    if 'csv' in mime:
        return 'csv'
    elif 'spreadsheet' in mime or 'excel' in mime:
        return 'xlsx'
    
    # Default to CSV
    return 'csv'


def parse_uploaded_file(file_path: str) -> Tuple[pd.DataFrame, List[str], Optional[str]]:
    """
    Parse a CSV or XLSX file using pandas.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (dataframe, original_headers, error_message)
    """
    try:
        # Detect file type
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            return None, [], "Unsupported file type. Please upload CSV or XLSX."
        
        # Store original headers
        original_headers = df.columns.tolist()
        
        # Standardize column names
        column_mapping = {}
        for col in df.columns:
            standard_key = map_column_to_standard(col)
            if standard_key:
                column_mapping[col] = standard_key
            else:
                # Keep original but normalized
                column_mapping[col] = normalize_column_name(col)
        
        df = df.rename(columns=column_mapping)
        
        # Drop completely empty rows
        df = df.dropna(how='all')
        
        return df, original_headers, None
        
    except Exception as e:
        return None, [], f"Error parsing file: {str(e)}"


def is_taam_dataset(df: pd.DataFrame) -> bool:
    """
    Detect if a dataframe contains TAAM survey data.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        True if appears to be TAAM data
    """
    columns = set([col.lower() for col in df.columns])
    
    # Count how many core TAAM questions are present
    taam_question_count = sum(1 for q in CORE_TAAM_QUESTIONS if q in columns)
    
    return taam_question_count >= MIN_TAAM_QUESTIONS


def get_dataframe_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profile a dataframe to understand its structure.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Dictionary with profiling information
    """
    profile = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': {},
        'is_taam': is_taam_dataset(df),
    }
    
    for col in df.columns:
        col_data = {
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'unique_count': int(df[col].nunique()),
            'has_numbers': pd.api.types.is_numeric_dtype(df[col]),
        }
        
        # Sample values (first few non-null)
        sample_values = df[col].dropna().head(5).tolist()
        col_data['samples'] = sample_values
        
        profile['columns'][col] = col_data
    
    return profile


def save_uploaded_file(uploaded_file: UploadedFile, owner_id) -> str:
    """
    Save an uploaded file to the media directory.
    
    Args:
        uploaded_file: Django uploaded file
        owner_id: ID of the user uploading
        
    Returns:
        Path to saved file
    """
    # Create directory structure: media/uploads/{user_id}/
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(owner_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    import uuid
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    return file_path


def dataframe_to_records(df: pd.DataFrame, max_records: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Convert dataframe to list of dictionaries.
    
    Args:
        df: Pandas DataFrame
        max_records: Maximum number of records to return (None for all)
        
    Returns:
        List of dictionaries (one per row)
    """
    if max_records:
        df = df.head(max_records)
    
    # Convert to dict, handling NaN values
    records = df.replace({pd.NA: None, pd.NaT: None}).to_dict(orient='records')
    
    # Convert any remaining NaN to None
    import math
    for record in records:
        for key, value in record.items():
            if isinstance(value, float) and math.isnan(value):
                record[key] = None
    
    return records
