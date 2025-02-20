import re
import pandas as pd


def convert_btec_grade(grade):
    """
    Converts a BTEC grade string into a numeric value for comparison.
    This function tokenizes the input string and assigns each token a weight:
        D* -> 4
        D  -> 3
        M  -> 2
        P  -> 1
    The final score is the sum of these weights.

    For example:
      - "D*D*D*" => 4 + 4 + 4 = 12
      - "DDD"    => 3 + 3 + 3 = 9
      - "D*M P"  => 4 + 2 + 1 = 7  (if tokens are correctly extracted)
    """
    if not grade or not isinstance(grade, str):
        return None

    grade = grade.strip().upper()
    token_weights = {
        "D*": 4,
        "D": 3,
        "M": 2,
        "P": 1,
    }

    # Use regex to extract tokens; note that 'D*' should be matched before 'D'
    pattern = r'(D\*|D|M|P)'
    tokens = re.findall(pattern, grade)
    if not tokens:
        return None

    total_weight = sum(token_weights.get(token, 0) for token in tokens)
    return total_weight


def extract_gcse_grades(text):
    """
    Extracts numeric GCSE grades from a text description.
    For example, from "grade 5, grade 6, grade 7" it will extract [5, 6, 7].
    If no valid grade is found, returns an empty list.
    """
    if not text or not isinstance(text, str):
        return []
    # This regex looks for a digit (or digits) that come after the word "grade" (optional spaces).
    matches = re.findall(r'grade\s*(\d+)', text, flags=re.IGNORECASE)
    return [int(match) for match in matches]


def convert_bachelors_degree_from_gpa(gpa):
    """
    Converts a GPA value into a bachelor's degree classification string.

    Parameters:
        gpa (float or str): The GPA value. It will be converted to float.

    Returns:
        str: A classification such as "first class", "upper second class", etc.
             If the GPA does not meet any threshold, returns None.
    """
    try:
        gpa = float(gpa)
    except (TypeError, ValueError):
        return None

    if gpa >= 3.7:
        return "first class"
    elif gpa >= 3.3:
        return "upper second class"
    elif gpa >= 3.0:
        return "lower second class"
    elif gpa >= 2.5:
        return "third class"
    else:
        return None


def convert_a_level_to_numeric(grade):
    """
    Converts an A-Level grade string (e.g., "A*A*A*", "A*A*A", "AAB") into a numeric value.
    This function breaks down the grade into individual components, assigns a numeric value to each,
    and sums them up.
    """
    if not grade or not isinstance(grade, str):
        return None

    # Define the numeric values for each individual grade component.
    grade_values = {
        "A*": 56,
        "A": 48,
        "B": 40,
        "C": 32,
        "D": 24,
        "E": 16
    }

    # Use regex to find all grade components.
    # The pattern looks for "A*" first (since it has a special character), then A, B, etc.
    pattern = r'(A\*|A|B|C|D|E)'
    matches = re.findall(pattern, grade.upper())

    if not matches:
        return None

    # Sum the numeric values for each grade component.
    numeric_score = sum(grade_values.get(match, 0) for match in matches)
    return numeric_score


def extract_numeric(value):
    """Extracts the first numeric value from a string."""
    if pd.isna(value):
        return None
    match = re.search(r'\d+', str(value))
    return int(match.group()) if match else None


def extract_bachelors_classification(value):
    """
    Extracts a standardized classification from the 'bachelors_degree' column.
    Converts different text formats into:
    - 'First Class'
    - 'Upper Second'
    - 'Lower Second'
    - 'Third Class'
    """

    if pd.isna(value):
        return None  # Return None for missing values

    value = str(value).lower().strip()

    # Define classification mappings
    if "first" in value:
        return "first class"
    elif "upper second" in value or "2:1" in value or "second upper" in value:
        return "upper second class"
    elif "lower second" in value or "2:2" in value or "second lower" in value:
        return "lower second class"
    elif "third" in value or "third class" in value:
        return "third class"
    else:
        return None  # If no known classification is found
