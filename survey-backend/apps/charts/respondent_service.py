"""
Service for generating individual respondent charts on-demand from CSV files.
This avoids storing 1000+ chart objects in the database.
"""
from typing import List, Dict, Any, Optional
import pandas as pd

from apps.ingest.services import parse_uploaded_file, dataframe_to_records
from apps.charts.taam_service import determine_persona, create_radar_data, get_canonical_radar_data
from apps.charts.constants import AXES


def get_respondent_charts_paginated(
    file_path: str,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    Generate respondent charts on-demand from CSV file with pagination.
    
    Args:
        file_path: Path to the uploaded CSV/XLSX file
        page: Page number (1-indexed)
        page_size: Number of charts per page
        
    Returns:
        {
            'results': [chart_data, ...],
            'count': total_count,
            'next': has_next_page,
            'previous': has_previous_page,
            'page': current_page,
            'total_pages': total_pages
        }
    """
    # Parse file
    df, _, error = parse_uploaded_file(file_path)
    
    if error or df is None:
        return {
            'results': [],
            'count': 0,
            'next': False,
            'previous': False,
            'page': page,
            'total_pages': 0,
            'error': error
        }
    
    # Convert to records
    records = dataframe_to_records(df)
    total_count = len(records)
    total_pages = (total_count + page_size - 1) // page_size
    
    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_count)
    
    # Generate charts for this page
    chart_results = []
    for idx in range(start_idx, end_idx):
        record = records[idx]
        persona_code, persona_name, axis_scores, is_from_q20 = determine_persona(record)
        
        canonical_radar = get_canonical_radar_data(persona_code) if persona_code else None
        user_radar = create_radar_data(axis_scores) if axis_scores else None
        
        chart_results.append({
            'uid': f'respondent-{idx}',  # Virtual UID
            'chart_type': 'taam_radar',
            'is_canonical': False,
            'chart_config': {
                'title': f'Respondent {idx + 1} - {persona_name}',
                'respondent_index': idx,
                'persona_code': persona_code,
                'persona_name': persona_name,
                'user_data': user_radar,
                'canonical_data': canonical_radar,
                'axes': AXES,
                'domain': [0, 5],
                'axis_scores': axis_scores,
            },
            'derived_metrics': {
                'respondent_index': idx,
                'persona_code': persona_code,
                'persona_name': persona_name,
                'is_from_q20': bool(is_from_q20),
                'axis_scores': axis_scores,
                'survey_answers': record,  # Include all raw survey answers
            }
        })
    
    return {
        'results': chart_results,
        'count': total_count,
        'next': page < total_pages,
        'previous': page > 1,
        'page': page,
        'total_pages': total_pages,
    }


def get_single_respondent_chart(file_path: str, respondent_index: int) -> Optional[Dict[str, Any]]:
    """
    Get a single respondent chart by index.
    
    Args:
        file_path: Path to the uploaded CSV/XLSX file
        respondent_index: 0-based index of the respondent
        
    Returns:
        Chart data dict or None if not found
    """
    df, _, error = parse_uploaded_file(file_path)
    
    if error or df is None or respondent_index >= len(df):
        return None
    
    records = dataframe_to_records(df)
    record = records[respondent_index]
    
    persona_code, persona_name, axis_scores, is_from_q20 = determine_persona(record)
    canonical_radar = get_canonical_radar_data(persona_code) if persona_code else None
    user_radar = create_radar_data(axis_scores) if axis_scores else None
    
    return {
        'uid': f'respondent-{respondent_index}',
        'chart_type': 'taam_radar',
        'is_canonical': False,
        'chart_config': {
            'title': f'Respondent {respondent_index + 1} - {persona_name}',
            'respondent_index': respondent_index,
            'persona_code': persona_code,
            'persona_name': persona_name,
            'user_data': user_radar,
            'canonical_data': canonical_radar,
            'axes': AXES,
            'domain': [0, 5],
            'axis_scores': axis_scores,
        },
        'derived_metrics': {
            'respondent_index': respondent_index,
            'persona_code': persona_code,
            'persona_name': persona_name,
            'is_from_q20': bool(is_from_q20),
            'axis_scores': axis_scores,
            'survey_answers': record,
        }
    }
