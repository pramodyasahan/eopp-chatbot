import pandas as pd
import os
import time
import logging
import ast
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Input and output file paths
input_file = "../data/4uni.xlsx"
output_file = "../data/processed/updated_data.xlsx"


df = pd.read_excel(input_file)


# Initialize OpenAI ChatGPT model
llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)


# Define a function to classify courses in batches
def classify_courses(course_names, degree_names):
    """Uses GPT to determine the general field of study for a batch of course names."""
    if not course_names:
        return []

    prompt = f"""
    You are an expert in academic course classification. Your task is to categorize each course into one of the following broad academic fields:

    - Computer Science
    - Business
    - Law
    - Healthcare
    - Engineering
    - Arts & Humanities
    - Social Sciences
    - Natural Sciences
    - Education
    - Agriculture & Environmental Science
    - Mathematics & Statistics

    If a course does not match any of the above categories, assign the most relevant field based on the degree name.

    Now classify the following courses with their corresponding degree programs:
    {list(zip(course_names, degree_names))}

    Provide the output as a **Python list of strings**, one category for each input course.
    """

    logging.info(f"Sending batch of {len(course_names)} courses to OpenAI...")
    try:
        response = llm([HumanMessage(content=prompt)])
        raw_response = response.content.strip()
        logging.info(f"Raw response: {raw_response}")

        # Extract only the list part of the response
        list_start = raw_response.find("[")
        list_end = raw_response.rfind("]") + 1
        clean_response = raw_response[list_start:list_end]

        # Safely evaluate the extracted list
        parsed_response = ast.literal_eval(clean_response)

        # Ensure the response is always a **flat list** (not a list of tuples)
        if isinstance(parsed_response, list):
            if all(isinstance(item, tuple) for item in parsed_response):
                parsed_response = [item[1] for item in parsed_response]  # Extract categories from tuples
            return parsed_response
        else:
            return ["Unknown"] * len(course_names)  # Default case
    except Exception as e:
        logging.error(f"Error in classification: {e}")
        return ["Unknown"] * len(course_names)


batch_size = 20
courses = df["course_or_degree_name"].dropna().tolist()
degree_names = df["degree_program"].dropna().tolist()
classified_fields = []

for i in range(0, len(courses), batch_size):
    batch_courses = courses[i: i + batch_size]
    batch_degrees = degree_names[i: i + batch_size] if len(degree_names) > i else ["Unknown"] * len(batch_courses)
    classified_fields.extend(classify_courses(batch_courses, batch_degrees))
    time.sleep(1)  # Prevent rate limits

# Ensure the field_name column is correctly added
df["field_name"] = "Unknown"
df.loc[df["course_or_degree_name"].notna(), "field_name"] = classified_fields

# Save the updated file
df.to_excel(output_file, index=False)
logging.info(f"Updated dataset with field_name column saved to {output_file}")
