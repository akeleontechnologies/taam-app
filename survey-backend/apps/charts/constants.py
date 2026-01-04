"""
TAAM (The Art & Allure of Markets) Constants and Configuration
PDF-exact persona vectors + deterministic axis rules + robust scale/column mappings.
"""

# ========= GENERAL =========
ROUND_TO_QUARTER: bool = True  # Round final axis scores to nearest 0.25

def _norm(s):
    """Normalize text for robust matching across variants."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return str(s).strip().lower()
    return str(s).strip().lower()

def round_to_quarter(x: float) -> float:
    """Nearest 0.25 if ROUND_TO_QUARTER is True."""
    if x is None:
        return None
    if not ROUND_TO_QUARTER:
        return float(x)
    return round(float(x) * 4) / 4.0


# ========= AXES (order matters and must match radar plotting) =========
# Order for radar chart (clockwise from top): Price, Quality, Ingredients, Social Pressure, Brand Image, Convenience
AXES = [
    'Price',
    'Quality',
    'Ingredients',
    'Social Pressure',
    'Brand Image',
    'Convenience',
]


# ========= PERSONA PROTOTYPES (PDF-Exact) =========
# Axis order: Price, Quality, Ingredients, Social Pressure, Brand Image, Convenience
PERSONA_PROTOTYPES = {
    'A': {'name': 'Seamless Shoppers',     'vector': [2.5, 3.25, 3.25, 2.5, 2.5, 5.0]},
    'B': {'name': 'Value Hunters',         'vector': [5.0, 1.5, 2.0, 1.0, 2.5, 2.5]},
    'C': {'name': 'Aspirational Splurgers','vector': [5.0, 2.5, 2.5, 5.0, 5.0, 1.0]},
    'D': {'name': 'Obligati',              'vector': [4.0, 3.5, 2.5, 5.0, 3.5, 2.5]},
    'E': {'name': 'Luxe Enthusiasts',      'vector': [2.5, 5.0, 5.0, 1.0, 4.0, 2.0]},
    'F': {'name': 'Dependables',           'vector': [4.0, 2.5, 1.0, 4.0, 5.0, 2.5]},
    'G': {'name': 'Sprezzatura',           'vector': [5.0, 3.0, 2.0, 3.25, 2.5, 2.5]},
    'H': {'name': 'Ascent Beautifiers',    'vector': [5.0, 5.0, 4.0, 2.0, 1.5, 3.25]},
    'I': {'name': 'Refined Connoisseurs',  'vector': [2.5, 5.0, 5.0, 1.0, 3.25, 2.0]},
    'J': {'name': 'Exotica Seekers',       'vector': [2.5, 2.0, 5.0, 1.0, 1.0, 1.0]},
}

PERSONA_CODES_ORDER = ['A','B','C','D','E','F','G','H','I','J']
PERSONA_LETTER_BY_NAME = {v['name']: k for k, v in PERSONA_PROTOTYPES.items()}
PERSONA_NAME_BY_LETTER = {k: v['name'] for k, v in PERSONA_PROTOTYPES.items()}


# ========= QUESTION → AXIS WEIGHTS =========
AXIS_WEIGHTS = {
    'Price':           {'Q8': 0.60, 'Q9': 0.40},
    'Convenience':     {'Q18': 0.60, 'Q19': 0.40},
    'Quality':         {'Q10': 0.70, 'Q11': 0.30},
    'Ingredients':     {'Q12': 0.40, 'Q13': 0.60},
    'Social Pressure': {'Q14': 0.50, 'Q15': 0.30, 'Q23': 0.20},
    'Brand Image':     {'Q16': 0.50, 'Q17': 0.30, 'Q22': 0.20},
}


# ========= SCALE MAPPINGS (robust; keys are lowercased) =========
# Importance: Q8, Q10, Q12, Q14, Q16, Q18
IMPORTANCE_SCALE = {
    'not at all': 1, 'not at all important': 1,
    'slightly': 2, 'slightly important': 2,
    'moderately': 3, 'moderately important': 3, 'neutral': 3, 'very much': 4,
    'very': 4, 'very important': 4,
    'completely': 5, 'extremely important': 5,
    # accept 1..5 if numeric strings
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
}

# Frequency: Q9, Q17, Q19
FREQUENCY_SCALE = {
    'never': 1, 'rarely': 2, 'sometimes': 3, 'often': 4, 'always': 5,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,   # numeric acceptance
}

# Q11 (willingness to pay more) — canonical labels + safe fallbacks
PAY_MORE_SCALE = {
    'no, never': 1,
    'no, not often': 2,
    'neutral': 3,
    'yes, sometimes': 4,
    'yes, always': 5,
    # permissive synonyms (do not replace the canonical ones in your UI)
    'never': 1, 'rarely': 2, 'sometimes': 4, 'often': 4, 'always': 5,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
}

# Q22 (reaction to launches)
LAUNCH_BEHAVIOR_SCALE = {
    'i rarely pay attention to new launches.': 1,
    'rarely': 1,
    'i only buy if the product is aligned with my preferences and budget.': 2,
    'only if aligned': 2,
    'i wait for reviews before making a purchase.': 3,
    'wait for reviews': 3,
    'i get excited and want to try them immediately.': 5,
    'try immediately': 5,
    '1': 1, '2': 2, '3': 3, '5': 5,
}

# Q23 (influencer likelihood) — your file often uses numeric 1–5
INFLUENCER_SCALE = {
    'not likely': 1, 'slightly likely': 2, 'moderately likely': 3, 'very likely': 4, 'extremely likely': 5,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
}

# Q21 (income reaction) — tie-breaker only
INCOME_REACTION_SCALE = {
    'save most': 1, 'save': 1,
    'slight increase': 3,
    'spend more luxury': 5, 'spend luxury': 5,
    '1': 1, '3': 3, '5': 5,
}

def map_scale(value, scale):
    """Map any raw response to a numeric value using the provided scale."""
    if value is None:
        return None
    key = _norm(value)
    return scale.get(key)


# ========= COLUMN NAME MAPPINGS (fuzzy & includes real headers from your CSV) =========
COLUMN_MAPPINGS = {
    # Questions
    'q8':  ['Q8','q8','Question 8','question_8','price_importance','Q8_Price Importance'],
    'q9':  ['Q9','q9','Question 9','question_9','discount_seeking','Q9_Seek Discounts'],
    'q10': ['Q10','q10','Question 10','question_10','quality_importance','Q10_Quality Influence'],
    'q11': ['Q11','q11','Question 11','question_11','pay_more','Q11_Pay More For Quality'],
    'q12': ['Q12','q12','Question 12','question_12','ingredients_attention','Q12_Ingredient Attention'],
    'q13': ['Q13','q13','Question 13','question_13','specific_ingredients','Q13_Drawn To Specific Ingredients'],
    'q14': ['Q14','q14','Question 14','question_14','recommendations','Q14_Social Recommendation Effect'],
    'q15': ['Q15','q15','Question 15','question_15','social_expectations','Q15_Align With Expectations'],
    'q16': ['Q16','q16','Question 16','question_16','brand_importance','Q16_Brand Image Importance'],
    'q17': ['Q17','q17','Question 17','question_17','brand_loyalty','Q17_Prefer Trusted Brands'],
    'q18': ['Q18','q18','Question 18','question_18','convenience_importance','Q18_Convenience Importance'],
    'q19': ['Q19','q19','Question 19','question_19','online_preference','Q19_Prefer Online Shopping'],
    'q20': ['Q20','q20','Question 20','question_20','persona','persona_anchor','shopping_style','Q20_Shopping Style Persona Anchor'],
    'q21': ['Q21','q21','Question 21','question_21','income_reaction','Q21_Reaction To Income Increase'],
    'q22': ['Q22','q22','Question 22','question_22','new_launches','Q22_Reaction To New Launches'],
    'q23': ['Q23','q23','Question 23','question_23','influencer','Q23_Influencer Purchase Likelihood'],

    # Demographics (add the ones seen in your file)
    'emirate': ['Emirate','emirate','location','region','Q1_Emirate'],
    'gender':  ['Gender','gender','sex','Q3_Gender'],
    'age':     ['Age','age','age_group','Q2_Age Group'],
    # If you also need income/frequency/etc. for dashboards, add those here similarly.
}


# ========= TAAM DETECTION =========
# Minimum TAAM questions required to treat dataset as TAAM
MIN_TAAM_QUESTIONS = 8

# Core questions. Including q11 strengthens detection for real TAAM files.
CORE_TAAM_QUESTIONS = ['q8','q9','q10','q11','q12','q13','q14','q16','q18','q19']
