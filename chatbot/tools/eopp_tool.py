from langchain.tools import tool
from chatbot.filter import initial_filtering
from pydantic import BaseModel, Field
from typing import Optional, List


class FilterCriteria(BaseModel):
    """Defines all possible filtering criteria for educational opportunities."""

    university_name: Optional[str] = Field(
        None,
        description="Name of the university. Example options include: "
                    "university of westminster, university college birmingham, "
                    "university of suffolk, university of worcester"
    )

    latest_qualification: Optional[str] = Field(
        None,
        description="Applicant's latest academic qualification. Supported values include: This is always mandatory"
                    "a_levels, gcse, o_level, btec, ib, cache, hnd, hnc, nvq, bachelor's, master's, phd, "
                    "foundation, t_level, higher_national_certificate, diploma"
    )

    field_type: Optional[str] = Field(
        None,
        description="Field of study or academic discipline. Common fields include: This is always mandatory"
                    "arts and humanities, business, computer science, social sciences, law, healthcare, "
                    "engineering, agriculture and environmental science, natural_sciences"
    )
    degree_program: Optional[str] = Field(
        None,
        description="Degree level or academic qualification type. Supported levels include: "
                    "bachelor's, master's, postgraduate_diploma, foundation, level_1, level_2, level_3, phd, t_level, "
                    "higher_national_certificate, diploma, doctorate"
    )
    location: Optional[str] = Field(
        None,
        description="City or geographical location of the university. Example locations include: "
                    "london, birmingham, ipswich, worcester"
    )
    course_name: Optional[str] = Field(
        None,
        description="Specific course name. Examples include: "
                    "construction_management, international_business_and_management, media_and_development_ma, "
                    "primary_education_ba_hons_with_qts"
    )

    gpa: Optional[float] = Field(
        None,
        description="GPA achieved by the user as example 2.5, 3, 3.3, 3.4, 3.6, 3.9"
    )

    ielts: Optional[float] = Field(
        None,
        description="Overall IELTS score of the applicant."
    )

    ielts_individual_component: Optional[float] = Field(
        None,
        description="Individual IELTS component scores average."
    )

    btec_diploma: Optional[str] = Field(
        None,
        description="Details or classification of the BTEC Diploma achieved."
    )
    btec_extended_diploma: Optional[str] = Field(
        None,
        description="Details or classification of the BTEC Extended Diploma achieved."
    )
    gcse_overall: Optional[str] = Field(
        None,
        description="Overall GCSE grade or score, if applicable."
    )
    mandatory_subject_of_gcse: Optional[List[str]] = Field(
        None,
        description="List of mandatory subjects in GCSE that the applicant has taken."
    )
    a_levels_overall: Optional[str] = Field(
        None,
        description="Overall A-Levels grade or score."
    )
    mandatory_subject_of_a_levels: Optional[List[str]] = Field(
        None,
        description="List of mandatory subjects in A-Levels."
    )


class InitialFilteringToolInput(BaseModel):
    """Defines the input schema for the filtering tool."""

    filters: FilterCriteria = Field(..., description="Filtering criteria in a JSON structured format.")


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
    print(f"Initial Filter Input: \n{input_data}\n")
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
