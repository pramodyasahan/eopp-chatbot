import os
import gdown
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Google Drive file ID (Extracted from share link)
FILE_ID = "1Dc00KHaD4b_RmcCxeEbXmNLP5d7yTEPF"

# Ensure destination includes the filename
DESTINATION_FOLDER = "chatbot/chroma_db"
DESTINATION_FILE = os.path.join(DESTINATION_FOLDER, "chroma.sqlite3")


def download_from_gdrive(file_id, destination):
    """Download a file from Google Drive and save it."""
    if not os.path.exists(destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        gdown.download(f"https://drive.google.com/uc?id={file_id}", destination, quiet=False)
        st.success(f"✅ File downloaded successfully to {destination}")
    else:
        st.info("ℹ️ File already exists, skipping download.")


def main():
    """Main Streamlit App"""
    # Fix SQLite issue with Streamlit
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

    st.set_page_config(page_title="Demo", page_icon=":memo:", layout="wide")

    # Ensure the file is downloaded
    download_from_gdrive(FILE_ID, DESTINATION_FILE)

    pg = st.navigation(
        [
            st.Page("pages/page1.py", title="Introduction"),
            st.Page("pages/page2.py", title="Chatbot")
        ]
    )
    pg.run()


if __name__ == "__main__":
    main()
