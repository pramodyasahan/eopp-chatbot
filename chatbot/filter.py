import pandas as pd
from typing import List, Optional
from chatbot.utils.filtering_helpers import extract_numeric, convert_btec_grade, extract_gcse_grades, \
    convert_a_level_to_numeric, convert_bachelors_degree_from_gpa, extract_bachelors_classification


def determine_eligibility(latest_qualification: str, requires_gcse: bool = False) -> List[str]:
    """
    Determines eligible course categories based on the latest qualification.

    :param latest_qualification: The latest qualification of the applicant.
    :param requires_gcse: Boolean indicating if GCSE results are required.
    :return: List of eligible course categories.
    """
    latest_qualification = latest_qualification.lower()

    if latest_qualification in [
        "a-level", "gcse", "o-level", "btec", "ib", "cache", "hnd", "hnc", "nvq"
    ]:
        return ["Foundation", "International Year"]

    elif latest_qualification == "a-level" and any(qualification in latest_qualification for qualification in [
        "gcse", "o-level", "btec", "ib", "cache", "hnd", "hnc", "nvq"
    ]):
        return ["Foundation", "International Year", "International Year One", "Bachelor's", "Master's"]

    elif latest_qualification == "bachelor's":
        return ["Master's", "PhD"] if requires_gcse else ["Master's"]

    elif latest_qualification in ["master's", "bachelor's"]:
        return ["PhD"]

    return []


def filter_courses_by_eligibility(file_path: str, latest_qualification: str, requires_gcse: bool = False) -> pd.DataFrame:
    """
    Filters courses based on the latest qualification and additional criteria.

    :param file_path: Path to the dataset.
    :param latest_qualification: The user's latest qualification.
    :param requires_gcse: Boolean indicating if GCSE results are required.
    :param additional_filters: Additional filtering criteria.
    :return: Filtered list of eligible courses as a DataFrame.
    """
    # Load the dataset
    df = pd.read_excel(file_path, sheet_name="Sheet1")

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Normalize 'degree_program' values for comparison
    df["degree_program"] = df["degree_program"].astype(str).str.lower()

    # Get eligible course categories
    eligible_courses = determine_eligibility(latest_qualification, requires_gcse)

    # Filter the dataset based on eligibility
    df_filtered = df[df["degree_program"].isin([course.lower() for course in eligible_courses])]
    return df_filtered


def initial_filtering(file_path, filters):
    """
    Performs an initial filtering of the courses based on key parameters.
    Supports:
    - Finding universities based on a specific degree program.
    - Standard filtering using university name, field type, location, and degree program type.
    - Handles cases where a country name (e.g., "UK") is provided instead of a specific city.
    - Additional filtering for IELTS overall score and IELTS individual band scores.
    """

    # Load the Excel file
    if filters.get("latest_qualification"):
        df = filter_courses_by_eligibility(file_path, filters.get('latest_qualification', ''),
                                           filters.get('requires_gcse', False))
        print(f"After applying initial filtering, {len(df)} courses were filtered.")
    else:
        df = pd.read_excel(file_path, sheet_name="Sheet1")

    # Normalize dataset column values (convert to lowercase for case-insensitive matching)
    column_list = [
        "university_name", "field_name", "location", "degree_program", "course_or_degree_name", "country",
        "ielts", "ielts_individual_component", "ucas_tariff", "btec_diploma", "btec_extended_diploma",
        "gcse_overall", "mandatory_subject_of_gcse", "a_levels_overall", "a_levels_mandatory_minimum_grades",
        "mandatory_subject_of_a_levels", "t_level_numeric", "bachelors_degree_gpa"
    ]
    for col in column_list:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    print("Initial course count:", df.shape[0])

    # Alias check: If "course name" is provided, map it to "course_or_degree_name"
    if "course_name" in filters:
        filters["course_or_degree_name"] = filters.pop("course_name")

    # Check if the user query is only asking for universities offering a specific course
    if filters.get("course_or_degree_name") and not any(
            key in filters for key in ["university name", "field type", "location", "degree program type"]
    ):
        course_filter = filters["course_or_degree_name"].strip().lower()
        df_filtered = df[df["course_or_degree_name"].notna() & df["course_or_degree_name"].str.contains(
            course_filter, case=False, na=False, regex=False)]
        print("After filtering by course name:", df_filtered.shape[0])

        # Return only unique universities that offer this course
        if not df_filtered.empty:
            return df_filtered[["university_name"]].drop_duplicates()

        return "No universities found for this course."

    # Apply standard filtering (when multiple filters are used)
    if filters.get("university_name"):
        df = df[df["university_name"] == filters["university_name"].strip().lower()]
        print("After university name filter:", df.shape[0])

    if filters.get("field_type"):
        df = df[df["field_name"] == filters["field_type"].strip().lower()]
        print("After field type filter:", df.shape[0])

    if filters.get("location"):
        location_filter = filters["location"].strip().lower()

        # Skip location filtering if the user provided "UK"
        if location_filter != "uk":
            df = df[df["location"] == location_filter]
            print("After location filter:", df.shape[0])

    if filters.get("degree_program"):
        df = df[df["degree_program"] == filters["degree_program"].strip().lower()]
        print("After degree program type filter:", df.shape[0])

    # Apply IELTS filtering
    if "ielts" in filters:
        user_ielts = float(filters["ielts"])
        df["ielts"] = pd.to_numeric(df["ielts"], errors='coerce')
        df = df[(df["ielts"].isna()) | (df["ielts"] <= user_ielts)]
        print("After IELTS filter:", df.shape[0])

    # Apply IELTS Individual Component filtering
    if "ielts_individual_component" in filters:
        user_ielts_component = float(filters["ielts_individual_component"])
        df["ielts_individual_component"] = pd.to_numeric(df["ielts_individual_component"], errors='coerce')
        df = df[(df["ielts_individual_component"].isna()) | (df["ielts_individual_component"] <= user_ielts_component)]
        print("After IELTS Individual Component filter:", df.shape[0])

    # Apply UCAS Tariff filtering
    if "ucas_tariff" in filters:
        user_ucas = int(filters["ucas_tariff"])
        df["ucas_tariff_numeric"] = df["ucas_tariff"].apply(extract_numeric)
        df = df[(df["ucas_tariff_numeric"].isna()) | (df["ucas_tariff_numeric"] <= user_ucas)]
        print("After UCAS Tariff filter:", df.shape[0])

    # Apply A-Levels filtering using the improved conversion function
    if "a_levels_overall" in filters:
        # Convert the user's A-Level grade to its numeric value
        user_grade = filters["a_levels_overall"]
        user_a_level = convert_a_level_to_numeric(user_grade.upper())

        if user_a_level is not None:
            # Ensure that each A-Level value in the DataFrame is treated as a string before conversion.
            df["a_levels_numeric"] = df["a_levels_overall"].astype(str).apply(
                lambda x: convert_a_level_to_numeric(x.upper()))
            df = df[(df["a_levels_numeric"].isna()) | (df["a_levels_numeric"] <= user_a_level)]
            print("After A-Levels filter:", df.shape[0])
        else:
            print("Invalid user A-Level grade provided:", user_grade)

    if "btec_diploma" in filters:
        user_btec = convert_btec_grade(filters["btec_diploma"].upper())
        df["btec_diploma_numeric"] = df["btec_diploma"].apply(lambda x: convert_btec_grade(str(x).upper()))
        df = df[(df["btec_diploma_numeric"].isna()) | (df["btec_diploma_numeric"] <= user_btec)]
        print("After BTEC Diploma filter:", df.shape[0])

    if "btec_extended_diploma" in filters:
        user_extended_btec = convert_btec_grade(filters["btec_extended_diploma"].upper())
        df["btec_extended_diploma_numeric"] = df["btec_extended_diploma"].apply(
            lambda x: convert_btec_grade(str(x).upper()))
        df = df[
            (df["btec_extended_diploma_numeric"].isna()) | (df["btec_extended_diploma_numeric"] <= user_extended_btec)]
        print("After BTEC Extended Diploma filter:", df.shape[0])

    if "gcse_overall" in filters:
        user_gcse_grades = extract_gcse_grades(filters["gcse_overall"])
        # For each course, extract the list of GCSE grades
        df["gcse_grades"] = df["gcse_overall"].apply(extract_gcse_grades)
        # Example logic: only keep courses where every GCSE grade is at least 4
        df = df[df["gcse_grades"].apply(lambda grades: all(g >= 4 for g in grades))]
        print("After GCSE Overall filter:", df.shape[0])

    if "mandatory_subject_of_gcse" in filters:
        required_subjects = set(filters["mandatory_subject_of_gcse"].lower().split(", "))
        df = df[df["mandatory_subject_of_gcse"].apply(
            lambda x: required_subjects.issubset(set(str(x).lower().split(", ")))
        )]
        print("After Mandatory GCSE Subject filter:", df.shape[0])

    if "gpa" in filters:
        # Convert user's GPA into a classification string
        user_bachelor_class = convert_bachelors_degree_from_gpa(filters["gpa"])
        print("User classification:", user_bachelor_class)

        # Define classification ranking
        classification_ranking = {
            "first class": 1,
            "upper second class": 2,
            "lower second class": 3,
            "third class": 4,
            None: 5
        }

        # Get user's classification rank
        user_rank = classification_ranking.get(user_bachelor_class, float("inf"))

        # Extract and standardize classification from dataset
        df["bachelors_class_extracted"] = df["bachelors_degree"].apply(extract_bachelors_classification)

        # Apply filtering: Keep courses where the requirement is equal to or lower than the user's rank
        df = df[
            df["bachelors_class_extracted"].isna() |  # Include courses with no specific requirement
            (df["bachelors_class_extracted"].apply(lambda x: classification_ranking.get(x, float("inf"))) >= user_rank)
            ]

        print("After Bachelor's Degree filter:", df.shape[0])

    # Return results
    if not df.empty and "course_or_degree_name" in df.columns:
        return df[["university_name", "course_or_degree_name"]]
    else:
        return "No matching results found."
