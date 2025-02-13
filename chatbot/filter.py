import pandas as pd


def initial_filtering(file_path, filters):
    """
    Performs an initial filtering of the courses based on key parameters.
    Supports:
    - Finding universities based on a specific degree program.
    - Standard filtering using university name, field type, location, and degree program type.
    - Handles cases where a country name (e.g., "UK") is provided instead of a specific city.
    """

    # Load the Excel file
    df = pd.read_excel(file_path, sheet_name="Sheet1")

    # Normalize dataset column values (convert to lowercase for case-insensitive matching)
    for col in ["university_name", "field_name", "location", "degree_program", "course_or_degree_name", "country"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    print("Initial course count:", df.shape[0])

    # Alias check: If "course name" is provided, map it to "course_or_degree_name"
    if "course name" in filters:
        filters["course_or_degree_name"] = filters.pop("course name")

    # Check if the user query is **only** asking for universities offering a specific course
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
    if filters.get("university name"):
        df = df[df["university_name"] == filters["university name"].strip().lower()]
        print("After university name filter:", df.shape[0])

    if filters.get("field type"):
        df = df[df["field_name"] == filters["field type"].strip().lower()]
        print("After field type filter:", df.shape[0])

    if filters.get("location"):
        location_filter = filters["location"].strip().lower()

        # Skip location filtering if the user provided "UK"
        if location_filter != "uk":
            df = df[df["location"] == location_filter]
            print("After location filter:", df.shape[0])

    if filters.get("degree program type"):
        df = df[df["degree_program"] == filters["degree program type"].strip().lower()]
        print("After degree program type filter:", df.shape[0])

    # Return results
    if not df.empty and "course_or_degree_name" in df.columns:
        return df[["university_name", "course_or_degree_name"]]
    else:
        return "No matching results found."
