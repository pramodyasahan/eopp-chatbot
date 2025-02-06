import os
import json
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from chatbot.memory import agent_memory
from chatbot.eopp_tool import initial_filtering_tool
from chatbot.tools.information_rag_tool import query_data

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

tools = [query_data, initial_filtering_tool]


def load_onboarding_questions() -> str:
    """Load onboarding questions from a text file."""
    questions_file = os.path.join("docs", "questions.txt")
    if not os.path.exists(questions_file):
        raise FileNotFoundError(f"{questions_file} not found.")
    with open(questions_file, 'r', encoding='utf-8') as file:
        onboarding_questions = file.read().strip()
    return onboarding_questions


def setup_agent() -> AgentExecutor:
    """Set up the main agent with all required tools and prompt."""
    # Read the previously extracted CV details from file (if available)
    extracted_details_path = os.path.join("temp", "extracted_details.txt")
    if os.path.exists(extracted_details_path):
        with open(extracted_details_path, "r", encoding="utf-8") as file:
            extracted_details = file.read().strip()
    else:
        extracted_details = "No extracted details available."

    # Build the prompt template including onboarding questions and extracted CV details
    prompt = PromptTemplate(
        input_variables=["agent_scratchpad", "chat_history", "input"],
        template=(
            f"""
            You are an AI education consultant helping students find the best **Educational Opportunity and Pathways Program (EOPP)**.

            Your Responsibilities:
            - Gather required information from the user.
            - Here are the required onboarding questions:
            {load_onboarding_questions()}  

            We have already analyzed the user's CV and found:
            {extracted_details}

            Please verify with the user if the above details are correct.
            Ask for any missing or updated information one detail at a time.

            If a user asks for courses based on specific criteria, such as master's degree programs, please extract the necessary filters (for example, set "degree program type" to "master's") and call the 'initial_filtering_tool' accordingly.

            Retrieve Course-Related Information:
            - Use the 'initial_filtering_tool' to filter courses based on key parameters like university name, field type, location, and degree program type.
            - For example, if a user asks: "Can you give me the related master's degree with their university?" you should interpret that as a request for courses with "degree program type": "master's".

            Match the Best EOPP:
            - Use the 'match_eopp' tool to suggest the most suitable educational opportunities.

            ---
            Important Rules for Engagement:
            - Be concise and structured.
            - Ask for missing information one at a time.
            - Provide the most relevant and up-to-date information.

            Let's get started!
            """
            """
            Chat History:
            {chat_history}

            User Input: {input}
            {agent_scratchpad}
            """
        ),
    )

    # Set up the language model (using GPT-4o in this example)
    agent_llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

    # Create the agent using the tool-calling agent builder
    agent = create_tool_calling_agent(agent_llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=agent_memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    return agent_executor


if __name__ == "__main__":
    # To test the agent locally:
    agent_executor = setup_agent()
    # Example of running the agent with a sample input:
    response = agent_executor.run("Hello, I'd like to find engineering courses for a bachelor's degree.")
    print(response)
