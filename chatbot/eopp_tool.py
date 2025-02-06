import json
from langchain.tools import tool
from chatbot.filter import initial_filtering

# Define allowed categories for filtering
ALLOWED_UNIVERSITIES = {
    "university college birmingham",
    "university of westminster",
    "university of suffolk",
    "university of west london",
    "university of worcester"
}

ALLOWED_FIELD_TYPES = {
    "healthcare",
    "computer science",
    "business",
    "engineering",
    "law",
    "Arts & Humanities",
    "Education",
    "Social Sciences",
    "Agriculture & Environmental Science",
    "Natural Sciences"
}

ALLOWED_LOCATIONS = {
    "birmingham",
    "ipswich",
    "westminster",
    "suffolk",
    "london",
    "central london"
}

ALLOWED_DEGREE_TYPES = {
    "bachelor's",
    "master's",
    "foundation",
    "phd",
    "level 1",
    "level 2",
    "level 3",
    "a level"
}


@tool()
def initial_filtering_tool(filters_json: str) -> str:
    """
    Initial Filtering Tool

    This tool filters **courses based on user input criteria** OR returns **universities offering a specific course**.

    ---
    Allowed Filtering Criteria:
    - University Name: MUST be one of the following:
      {allowed_universities}
    - Field Type: MUST be one of the following:
      {allowed_field_types}
    - Degree Level: MUST be one of the following:
      {allowed_degree_types}
    - Location: MUST be one of the following:
      {allowed_locations}
    - Course Name: If the user asks for a specific course, the tool will return the universities that offer it.

    ---
    Example Usage:
    ```
    {
        "university name": "university of westminster",
        "field type": "computer science",
        "location": "london",
        "degree program type": "master's"
    }
    ```

    OR to find the university that offers a specific course:
    ```
    {
        "course name" -> "university name"
    }
    ```

    Response: A comma-separated list of matching courses or universities.

    ---
    """
    try:
        filters = json.loads(filters_json)
        print("Filters received:", filters)
    except Exception as e:
        return f"Error parsing filters JSON: {e}"

    file_path = "chatbot/data/processed/updated_data.xlsx"
    filtered_df = initial_filtering(file_path, filters)

    if isinstance(filtered_df, str):
        return filtered_df

    if filtered_df.empty:
        return "No matching results found."

    courses_and_universities = [
        f"{row['university_name']} - {row['course_or_degree_name']}"
        for _, row in filtered_df.iterrows()
    ]

    # Join the results into a comma-separated string
    return ", ".join(courses_and_universities)
