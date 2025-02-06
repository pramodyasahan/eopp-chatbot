import os
import logging
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def create_chroma_vectorstore_from_folders(base_folder_path, collection_name="document_collection"):
    """
    Create a Chroma vector store from text files in specified folder and its subfolders.

    Args:
        base_folder_path (str): Path to the base folder containing subfolders with text files
        collection_name (str, optional): Name of the Chroma collection. Defaults to "document_collection"

    Returns:
        Chroma: A Chroma vector store with embedded documents
    """
    logging.info(f"Starting vector store creation for folder: {base_folder_path}")

    if not os.path.exists(base_folder_path):
        logging.error(f"Folder path {base_folder_path} does not exist.")
        raise ValueError(f"Folder path {base_folder_path} does not exist.")

    embeddings = OpenAIEmbeddings()
    documents = []

    # Walk through all subdirectories and files
    for subdir, _, files in os.walk(base_folder_path):
        logging.info(f"Scanning folder: {subdir}")
        for filename in files:
            if filename.endswith('.txt'):
                file_path = os.path.join(subdir, filename)
                try:
                    logging.info(f"Loading file: {file_path}")
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                except Exception as e:
                    logging.error(f"Error loading {filename}: {e}")

    if not documents:
        logging.warning("No text documents found in the specified folder.")
        raise ValueError("No text documents found in the specified folder.")

    logging.info("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(documents)

    logging.info("Creating Chroma vector store...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory="../chroma_db"
    )

    logging.info("Vector store creation complete.")
    return vectorstore


def main():
    dataset_base_path = "../../dataset"
    logging.info("Starting the process...")
    create_chroma_vectorstore_from_folders(dataset_base_path)
    logging.info("Process completed successfully.")


if __name__ == "__main__":
    main()
