import os
import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from chatbot.agent import setup_agent
from chatbot.analyze_cv import extract_cv_details
from chatbot.memory import memory_storage

st.header("Chat")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:

    temp_dir = "./temp"
    os.makedirs(temp_dir, exist_ok=True)

    file_path = f"./temp/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Submit"):
        details = extract_cv_details(file_path)
        st.session_state.pdf_uploaded = True
        st.session_state.cv_details = details

if getattr(st.session_state, 'pdf_uploaded', False):
    with st.expander("expand"):
        st.write(st.session_state.cv_details)

    for i, msg in enumerate(memory_storage.messages):
        name = "user" if i % 2 == 0 else "assistant"
        st.chat_message(name).markdown(msg.content)

    # Hardcoded welcome message from the assistant after CV submission
    if not getattr(st.session_state, 'welcome_message_sent', False):
        with st.chat_message("assistant"):
            st.markdown("Hello! Welcome to the EOPP Matching App.")
        st.session_state.welcome_message_sent = True

    if user_input := st.chat_input("User Input"):
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Generating Response..."):
            with st.chat_message("assistant"):
                st_callback = StreamlitCallbackHandler(st.container())
                agent_executor = setup_agent()
                response = agent_executor.invoke(
                    {"input": user_input}, callbacks=[st_callback]
                )

                answer = response["output"]
                st.markdown(answer)

    if st.sidebar.button("Clear Chat History"):
        memory_storage.clear()
