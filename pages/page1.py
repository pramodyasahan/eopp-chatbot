import streamlit as st

st.title("EOPP Matching App ")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("### Explore Your Opportunities")
    st.image("./images/loading_image.jpg")  # Replace with the path to your logo

with col2:
    st.markdown("##")
    st.markdown("### 2024/10/16")
    st.markdown(
        """
        Demo 1

        CV  Uploading, Parsing and Initial Question-Answer Workflow for Information Extraction
        """
    )
