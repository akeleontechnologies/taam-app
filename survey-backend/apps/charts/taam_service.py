"""
TAAM Service - Handles TAAM survey data parsing and analysis.
Implements the exact logic from the PDF specification.
"""
from __future__ import annotations
import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

from .constants import (
    PERSONA_PROTOTYPES,
    AXES,
    AXIS_WEIGHTS,
    IMPORTANCE_SCALE,
    FREQUENCY_SCALE,
    PAY_MORE_SCALE,
    LAUNCH_BEHAVIOR_SCALE,
    INFLUENCER_SCALE,
    INCOME_REACTION_SCALE,
)

# ---------------- Utilities ----------------

def round_to_quarter(value: float) -> float:
    """Round a value to the nearest 0.25."""
    return round(float(value) * 4) / 4.0


def normalize_text(text: Any) -> str:
    """Normalize text for scale and anchor matching."""
    if text is None:
        return ""
    if isinstance(text, (int, float)):
        return str(text).strip().lower()
    return str(text).strip().lower()


def _persona_name_by_code(code: str) -> Optional[str]:
    code = (code or "").strip().upper()
    return PERSONA_PROTOTYPES.get(code, {}).get("name")


def _code_by_persona_name(name: str) -> Optional[str]:
    n = normalize_text(name)
    for code, data in PERSONA_PROTOTYPES.items():
        if normalize_text(data["name"]) == n:
            return code
    return None


def _q20_to_code(raw: Any) -> Optional[str]:
    """
    Robustly parse Q20 "persona anchor" into a persona code (A..J).
    Accepts:
      - Letter codes: "A", "b", etc.
      - Exact persona names: "Seamless Shoppers"
      - Full anchor sentences: "... (Seamless Shoppers)"
    """
    if raw is None:
        return None
    s = normalize_text(raw)

    # 1) Single-letter code A..J
    if len(s) == 1 and s.isalpha():
        code = s.upper()
        if code in PERSONA_PROTOTYPES:
            return code

    # 2) Parenthetical "(Persona Name)" inside anchors
    #    e.g. "I ... experiences. (Seamless Shoppers)"
    m = re.search(r"\(([^)]+)\)", s)
    if m:
        name_inside = m.group(1).strip()
        code = _code_by_persona_name(name_inside)
        if code:
            return code

    # 3) Direct persona name anywhere in the string
    for code, data in PERSONA_PROTOTYPES.items():
        if normalize_text(data["name"]) in s:
            return code

    # 4) As a last resort, try exact code keywords like " (A) " etc.
    m2 = re.search(r"\b([a-j])\b", s)
    if m2:
        code = m2.group(1).upper()
        if code in PERSONA_PROTOTYPES:
            return code

    return None


# ---------------- Scale mapping ----------------

def map_answer_to_scale(question_key: str, answer: Any) -> Optional[float]:
    """
    Map a survey answer to the 1-5 numeric scale.
    """
    # Numeric already?
    if isinstance(answer, (int, float)):
        val = float(answer)
        return val if 1.0 <= val <= 5.0 else None

    answer_text = normalize_text(answer)

    if question_key in ['q8', 'q10', 'q12', 'q14', 'q16', 'q18']:
        scale = IMPORTANCE_SCALE
    elif question_key in ['q9', 'q17', 'q19']:
        scale = FREQUENCY_SCALE
    elif question_key == 'q11':
        scale = PAY_MORE_SCALE
    elif question_key == 'q22':
        scale = LAUNCH_BEHAVIOR_SCALE
    elif question_key == 'q23':
        scale = INFLUENCER_SCALE
    elif question_key == 'q21':
        scale = INCOME_REACTION_SCALE
    else:
        # Attempt numeric fallback
        try:
            val = float(answer_text)
            return val if 1.0 <= val <= 5.0 else None
        except (ValueError, TypeError):
            return None

    # Exact match
    if answer_text in scale:
        return float(scale[answer_text])

    # Loose contains match (helps with slight variations)
    for key, value in scale.items():
        if key in answer_text or answer_text in key:
            return float(value)

    # Numeric fallback
    try:
        val = float(answer_text)
        return val if 1.0 <= val <= 5.0 else None
    except (ValueError, TypeError):
        return None


# ---------------- Axis computation ----------------

def compute_axis_score(row_data: Dict[str, Any], axis_name: str) -> Optional[float]:
    """
    Compute a single axis score for a respondent.
    Returns a value in [1..5] rounded to 0.25, or None if insufficient data.
    """
    if axis_name not in AXIS_WEIGHTS:
        return None

    weights = AXIS_WEIGHTS[axis_name]  # e.g., {'Q8':0.6, 'Q9':0.4}
    weighted_sum = 0.0
    total_weight = 0.0

    for q_key_raw, w in weights.items():
        q_key = q_key_raw.lower()  # 'Q8' -> 'q8'
        if q_key in row_data:
            v = map_answer_to_scale(q_key, row_data[q_key])
            if v is not None:
                weighted_sum += v * w
                total_weight += w

    if total_weight == 0:
        return None

    score = weighted_sum / total_weight
    return round_to_quarter(score)


def compute_all_axes(row_data: Dict[str, Any]) -> Dict[str, float]:
    """Compute all six axis scores for a respondent."""
    out: Dict[str, float] = {}
    for axis in AXES:
        val = compute_axis_score(row_data, axis)
        if val is not None:
            out[axis] = val
    return out


# ---------------- Persona helpers ----------------

def get_persona_vector(persona_or_q20: str) -> Optional[List[float]]:
    """
    Resolve a persona code/name/anchor to the canonical vector.
    Accepts: code ('A'), name ('Seamless Shoppers'), or an anchor sentence.
    """
    code = _q20_to_code(persona_or_q20)
    if code and code in PERSONA_PROTOTYPES:
        return PERSONA_PROTOTYPES[code]['vector']
    return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Cosine similarity between two vectors."""
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    na = np.linalg.norm(v1)
    nb = np.linalg.norm(v2)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(v1, v2) / (na * nb))


def find_closest_persona(axis_scores: Dict[str, float]) -> Tuple[str, str, float]:
    """
    Find the closest persona prototype to computed axis scores.
    Returns (persona_code, persona_name, similarity_score).
    """
    user_vec = [axis_scores.get(axis, 0.0) for axis in AXES]
    best_code, best_name, best_sim = '', '', -1.0
    for code, proto in PERSONA_PROTOTYPES.items():
        sim = cosine_similarity(user_vec, proto['vector'])
        if sim > best_sim:
            best_sim = sim
            best_code = code
            best_name = proto['name']
    return best_code, best_name, best_sim


# ---------------- Public API ----------------

def determine_persona(row_data: Dict[str, Any]) -> Tuple[str, str, Dict[str, float], bool]:
    """
    Determine a respondent's persona.
    Returns:
      (persona_code, persona_name, axis_scores, is_from_q20)
    """
    # 1) Use Q20 anchor if present
    q20_raw = row_data.get('q20')
    code_from_q20 = _q20_to_code(q20_raw) if q20_raw else None
    if code_from_q20:
        vec = PERSONA_PROTOTYPES[code_from_q20]['vector']
        axis_scores = {AXES[i]: vec[i] for i in range(len(AXES))}
        return code_from_q20, PERSONA_PROTOTYPES[code_from_q20]['name'], axis_scores, True

    # 2) Compute axes and map by cosine similarity
    axis_scores = compute_all_axes(row_data)
    if len(axis_scores) < 4:
        return '', 'Unknown', axis_scores, False

    code, name, _ = find_closest_persona(axis_scores)
    return code, name, axis_scores, False


def create_radar_data(axis_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Create radar chart data in the format expected by the frontend.
    """
    out: List[Dict[str, Any]] = []
    for axis in AXES:
        val = float(axis_scores.get(axis, 0.0))
        out.append({
            'axis': axis,
            'value': val,
            'percent': round((val / 5.0) * 100.0, 1),
        })
    return out


def get_canonical_radar_data(persona_code: str) -> List[Dict[str, Any]]:
    """
    Get the canonical radar data for a persona (A..J).
    """
    code = (persona_code or "").strip().upper()
    if code not in PERSONA_PROTOTYPES:
        return []
    vec = PERSONA_PROTOTYPES[code]['vector']
    return create_radar_data({AXES[i]: vec[i] for i in range(len(AXES))})
