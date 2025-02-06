import json
from langchain.tools import tool
from chatbot.filter import initial_filtering


@tool()
def initial_filtering_tool(filters_json: str) -> str:
    """
    Initial Filtering Tool

    Filters courses based on user criteria or returns universities offering a specific course.

    Allowed Filters:
    - University Name: university college birmingham, university of westminster, university of suffolk, university of west london, university of worcester.
    - Field Type: healthcare, computer science, business, engineering, law, Arts & Humanities, Education, Social Sciences, Agriculture & Environmental Science, Natural Sciences.
    - Degree Level: bachelor's, master's, foundation, phd.
    - Location: birmingham, ipswich, westminster, suffolk, london.
    - Course Name: Returns universities offering the specified course.

    Usage Example:
    {
        "university name": null,
        "field type": "engineering",
        "location": "london",
        "degree program type": "bachelor's"
    }

    Response: A comma-separated list of matching courses/universities or an appropriate message.
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
