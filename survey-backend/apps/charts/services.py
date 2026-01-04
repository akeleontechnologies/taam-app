"""
Chart Generation Service - Creates chart specifications from parsed data.
Handles TAAM radar charts, distributions, heatmaps, and generic charts.
"""
from __future__ import annotations
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

from apps.charts.constants import PERSONA_PROTOTYPES, AXES
from apps.charts.taam_service import (
    determine_persona,           # -> Tuple[str|None, str|None, Dict[str,float], bool]
    create_radar_data,           # -> List[Dict[str, Any]] (axis/value/percent)
    get_canonical_radar_data,    # -> List[Dict[str, Any]]
)
from apps.ingest.services import dataframe_to_records


# ---------- Helpers ----------

PERSONA_CODES_ORDER: List[str] = sorted(PERSONA_PROTOTYPES.keys())  # ["A","B",...,"J"]

def _persona_name_from_code(code: str) -> str:
    return PERSONA_PROTOTYPES[code]["name"]

def _is_valid_persona(name: Optional[str]) -> bool:
    return bool(name) and name != "Unknown"


# ---------- Stats Generators ----------

def generate_taam_persona_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate persona distribution chart data from TAAM responses.

    Returns:
        {
          'distribution': [{'persona': str, 'persona_code': str, 'count': int, 'percent': float}, ...],
          'total_respondents': int
        }
    """
    records = dataframe_to_records(df)
    persona_counts: Counter[str] = Counter()

    for record in records:
        persona_code, persona_name, _, _ = determine_persona(record)
        if _is_valid_persona(persona_name):
            persona_counts[persona_name] += 1

    total = sum(persona_counts.values())
    distribution: List[Dict[str, Any]] = []

    # Emit in A..J order for stable charts
    for code in PERSONA_CODES_ORDER:
        persona_name = _persona_name_from_code(code)
        count = int(persona_counts.get(persona_name, 0))
        percent = round((count / total * 100), 2) if total > 0 else 0.0
        distribution.append({
            'persona': persona_name,
            'persona_code': code,
            'count': count,
            'percent': percent,
        })

    return {
        'distribution': distribution,
        'total_respondents': total,
    }


def generate_taam_heatmap(df: pd.DataFrame, use_canonical: bool = False) -> Dict[str, Dict[str, float]]:
    """
    Generate heatmap data showing average axis scores per persona.

    Returns:
        { persona_name: { axis: value, ... }, ... }
    """
    if use_canonical:
        # Exactly the PDF vectors
        return {
            PERSONA_PROTOTYPES[code]['name']: {
                AXES[i]: PERSONA_PROTOTYPES[code]['vector'][i] for i in range(len(AXES))
            }
            for code in PERSONA_CODES_ORDER
        }

    # Observed: compute from individual respondents
    records = dataframe_to_records(df)
    persona_axes: Dict[str, List[Dict[str, float]]] = {}

    for record in records:
        persona_code, persona_name, axis_scores, _ = determine_persona(record)
        if _is_valid_persona(persona_name) and axis_scores:
            persona_axes.setdefault(persona_name, []).append(axis_scores)

    heatmap: Dict[str, Dict[str, float]] = {}
    for persona_name, axes_list in persona_axes.items():
        if not axes_list:
            continue  # no data for this persona
        avg_axes: Dict[str, float] = {}
        for axis in AXES:
            vals = [a[axis] for a in axes_list if axis in a]
            if vals:
                avg_axes[axis] = round(sum(vals) / len(vals), 2)
        if avg_axes:
            heatmap[persona_name] = avg_axes

    return heatmap


def generate_taam_chart_specs(df: pd.DataFrame, dataset_id: Any, owner_id: Any) -> List[Dict[str, Any]]:
    """
    Generate ONLY summary TAAM chart specifications for a dataset:
      - Persona distribution (A..J order)
      - Canonical heatmap
      - Observed heatmap
      
    Individual respondent charts are generated on-demand via the respondent_service.
    """
    chart_specs: List[Dict[str, Any]] = []
    records = dataframe_to_records(df)

    # Track distribution and which persona codes appear
    persona_counts: Counter[str] = Counter()
    personas_found_codes: set[str] = set()

    # Count personas (no longer creating individual chart objects)
    for idx, record in enumerate(records):
        persona_code, persona_name, axis_scores, is_from_q20 = determine_persona(record)

        if not _is_valid_persona(persona_name):
            continue

        persona_counts[persona_name] += 1
        if persona_code:
            personas_found_codes.add(persona_code)

    # 1) Summary distribution (A..J order)
    total = sum(persona_counts.values())
    distribution = []
    for code in PERSONA_CODES_ORDER:
        name = _persona_name_from_code(code)
        count = int(persona_counts.get(name, 0))
        percent = round((count / total * 100), 2) if total > 0 else 0.0
        distribution.append({'persona': name, 'persona_code': code, 'count': count, 'percent': percent})

    chart_specs.append({
        'owner_id': owner_id,
        'dataset_id': dataset_id,
        'chart_type': 'persona_distribution',
        'is_canonical': False,
        'chart_config': {
            'title': 'Persona Distribution - All Respondents',
            'data': distribution,
            'value_field': 'count',
            'category_field': 'persona',
            'order': PERSONA_CODES_ORDER,
        },
        'derived_metrics': {
            'total_respondents': total,
            'persona_distribution': {d['persona']: {'count': d['count'], 'percentage': d['percent']} for d in distribution},
            'unique_personas_found': len(personas_found_codes),
        }
    })

    # 2) Canonical heatmap
    canonical_heatmap = generate_taam_heatmap(df, use_canonical=True)
    chart_specs.append({
        'owner_id': owner_id,
        'dataset_id': dataset_id,
        'chart_type': 'heatmap_canonical',
        'is_canonical': True,
        'chart_config': {
            'title': 'TAAM Persona Profiles (Canonical)',
            'data': canonical_heatmap,
            'axes': AXES,
            'order': PERSONA_CODES_ORDER,
        },
        'derived_metrics': {'heatmap_type': 'canonical'}
    })

    return chart_specs


# ---------- Generic (Non-TAAM) ----------

def infer_generic_chart_type(df: pd.DataFrame) -> str:
    """
    Infer an appropriate chart type for non-TAAM data (heuristics only).
    """
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    num_numeric = len(numeric_cols)
    num_categorical = len(categorical_cols)

    if num_numeric >= 2:
        return 'scatter'   # relationships
    if num_numeric >= 1 and num_categorical >= 1:
        return 'bar'       # category vs value
    if num_categorical >= 1:
        # Pie only if first categorical has few unique values
        first_cat = categorical_cols[0]
        if df[first_cat].nunique(dropna=True) <= 10:
            return 'pie'
        return 'bar'
    return 'bar'


def generate_generic_chart_specs(df: pd.DataFrame, dataset_id: Any, owner_id: Any) -> List[Dict[str, Any]]:
    """
    Generate chart specifications for non-TAAM datasets (one suggested spec).
    """
    chart_type = infer_generic_chart_type(df)

    chart_specs = [{
        'owner_id': owner_id,
        'dataset_id': dataset_id,
        'chart_type': chart_type,
        'is_canonical': False,
        'chart_config': {
            'title': 'Data Visualization',
            'suggested_type': chart_type,
            'columns': df.columns.tolist(),
            'row_count': int(len(df)),
        },
        'derived_metrics': {
            'profiling': {
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            }
        }
    }]

    return chart_specs
