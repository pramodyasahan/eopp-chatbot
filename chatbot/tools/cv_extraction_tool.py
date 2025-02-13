import os
import glob
import PyPDF2
from langchain.tools import Tool

# Memory dictionary to store extracted details
extracted_qualifications_memory = {}


def get_latest_cv():
    """Finds the latest uploaded CV in the 'temp/' folder."""
    temp_folder = "temp"
    pdf_files = glob.glob(os.path.join(temp_folder, "*.pdf"))

    if not pdf_files:
        return None  # No CV found

    # Get the most recently modified CV file
    latest_cv = max(pdf_files, key=os.path.getmtime)
    return latest_cv


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            extracted_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return extracted_text.strip() if extracted_text else "No text extracted from PDF."
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def store_extracted_details(input_text: str = None):
    """Extracts and stores qualifications from the latest uploaded CV."""
    latest_cv = get_latest_cv()  # Get the latest uploaded CV

    if latest_cv:
        extracted_details = extract_text_from_pdf(latest_cv)

        # Store extracted details in memory
        extracted_qualifications_memory["Extracted qualifications"] = extracted_details
    else:
        extracted_qualifications_memory["Extracted qualifications"] = "No CV found in temp folder."

    return extracted_qualifications_memory["Extracted qualifications"]


# Define a LangChain tool for CV extraction
cv_extraction_tool = Tool(
    name="cv_extraction_tool",  # Ensure no spaces or special characters
    func=store_extracted_details,
    description="Extracts and stores qualifications from the latest uploaded CV in the 'temp/' folder."
)
