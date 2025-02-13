import json
from langchain.tools import tool
from chatbot.filter import initial_filtering

from pydantic import BaseModel, Field
from typing import Optional


class FilterCriteria(BaseModel):
    """Defines all possible filtering criteria for educational opportunities."""

    university_name: Optional[str] = Field(
        None,
        description="Name of the university. Example options include: "
                    "'University of Westminster', 'University College Birmingham', "
                    "'University of Suffolk', 'University of Worcester'."
    )

    field_type: Optional[str] = Field(
        None,
        description="Field of study or academic discipline. Common fields include: "
                    "'Arts & Humanities', 'Business', 'Computer Science', 'Social Sciences', 'Law', 'Healthcare', "
                    "'Engineering', 'Agriculture & Environmental Science', 'Natural Sciences'"
    )

    degree_level: Optional[str] = Field(
        None,
        description="Degree level or academic qualification type. Supported levels include: "
                    "'Bachelor's', 'Master's', 'Postgraduate Diploma', 'Foundation', 'level 1', 'level 2', 'level 3', 'PhD', 'T-Level', "
                    "'Higher National Certificate', 'Diploma', 'Doctorate'."
    )

    location: Optional[str] = Field(
        None,
        description="City or geographical location of the university. Example locations include: "
                    "'London', 'Birmingham', 'Ipswich', 'Worcester'."
    )

    course_name: Optional[str] = Field(
        None,
        description="Specific course name. Examples include: "
                    "'Construction Management', 'International Business and Management', 'Media and Development MA', "
                    "'Primary Education BA (Hons) with QTS'"
    )


class InitialFilteringToolInput(BaseModel):
    """Defines the input schema for the filtering tool."""

    filters: FilterCriteria = Field(..., description="Filtering criteria in structured format.")
    latest_qualification: Optional[str] = Field(
        None, description="User's latest qualification (O-levels, A-Level, Bachelors, Masters)."
    )


@tool()
def initial_filtering_tool(input_data: InitialFilteringToolInput) -> str:
    """
    Retrieve university courses based on user-defined filters.

    This tool filters university courses using structured criteria provided
    in the `InitialFilteringToolInput` model. It supports multiple filtering
    options, including university name, field type, degree level, location,
    and course name. The user's latest qualification is also considered.

    Args:
        input_data (InitialFilteringToolInput): Structured filtering parameters
        as defined in the Pydantic model.

    Returns:
        str: A comma-separated list of matching university-course pairs, or
        an appropriate message if no matches are found.
    """

    # Only use non-None filters to prevent over-filtering
    filters = {key: value for key, value in input_data.filters.model_dump().items() if value is not None}

    print("Filters received:", filters)

    file_path = "chatbot/data/processed/updated_data.xlsx"
    filtered_df = initial_filtering(file_path, filters)

    if isinstance(filtered_df, str):
        return filtered_df

    if filtered_df.empty:
        return "No matching results found."

    # Ensure multiple universities are included
    university_groups = filtered_df.groupby("university_name")

    courses_and_universities = []
    for university, group in university_groups:
        top_courses = group.head(10)  # Limit results per university
        for _, row in top_courses.iterrows():
            courses_and_universities.append(f"{row['university_name']} - {row['course_or_degree_name']}")

    return ", ".join(courses_and_universities)
