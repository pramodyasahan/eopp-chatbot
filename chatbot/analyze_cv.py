import os


def extract_cv_details(file_path: str) -> str:
    """
    Extract details from a CV in PDF format.
    """
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser

    loader = PyPDFLoader(file_path)
    cv = loader.load()

    prompt = ChatPromptTemplate.from_template(
        """
        Extract the following details from the CV. If not provided, indicate that the information is not given:

        1. Name (as per passport)
        2. Date of birth
        3. Address (with the country)
        4. Contact number (with country code) - available via WhatsApp
        5. Email ID
        6. Latest qualification (month-year)

        If the qualification is GCSE or O-levels, following results:
        - English
        - Maths
        - Science

        If the qualification is A-Level, full results

        If the qualification is a Bachelor's degree, extract the following:
        1. Stream of study
        2. GPA

        If the qualification is a Master's degree, extract the following:
        1. Stream of study
        2. GPA
        
        Remember, **you must confirm the stream of study** from the latest qualification. If it’s missing or different, 
        ask the user for clarification using the provided options.
        - healthcare
        - computer science
        - business
        - engineering
        - law
        - Arts & Humanities
        - Social Sciences
        - Agriculture
        - Environmental Science
        - Natural Sciences

        7. English language qualifications - IELTS / PTE

        Candidate CV:
        {cv}
        """
    )

    model = ChatOpenAI()
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    output = chain.invoke({"cv": cv})

    os.makedirs("temp", exist_ok=True)
    with open("temp/extracted_details.txt", "w") as file:
        file.write(output)
    print(f"Output from the CV extraction: \n{output}\n\n")
    return output
