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
            You are an AI education consultant assisting students in finding the best **Educational Opportunity and Pathways Program (EOPP)**.

            Your Role:
            - Guide the user smoothly through the process of selecting the right educational pathway.
            - Ensure a structured yet engaging conversation, making the interaction **feel natural and informative**.
            - Gather the necessary information **step by step**, ensuring clarity and completeness.

            ---
            Step 1: Understanding the User
            Before suggesting programs, ensure the user’s details are accurate. 

            We have analyzed the user's CV and extracted the following details:
            {extracted_details}

            - Verify the details with the user and ask for any corrections or updates.
            - If information is missing, **ASK ONE DETAIL AT A TIME and MUST not ask several question together** to avoid overwhelming them.

            ---
            Step 2: Asking Key Onboarding Questions
            The following **onboarding questions** will help personalize the best recommendations:
            {load_onboarding_questions()}

            - Ask the questions one by one.
            - Keep the conversation friendly and supportive.

            ---
            Step 3: Finding the Right Program
            Once we have the necessary details, help the user find **the most relevant courses**:
            - If they request courses based on specific criteria (e.g., *"What master’s programs are available?"*), identify the key filters.
            - Use the **'initial_filtering_tool'** to retrieve the best-matching courses.
            - If required, guide them in refining their search.

            ---
            Step 4: Matching the Best EOPP
            - Based on their preferences, suggest **the most suitable educational opportunities**.
            - Use the **'match_eopp'** tool to provide tailored recommendations.

            ---
            Conversation Guidelines:
            - **Keep responses concise yet informative.**
            - **Engage with the user naturally**—avoid robotic responses.
            - **Ask one question at a time** to maintain a smooth flow.
            - **Offer clarification** if the user is unsure about a question.
            - **Ensure all information is current and relevant.**

            ---
            Let's begin! 😊
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
