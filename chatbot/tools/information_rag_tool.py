import os
from langchain.agents import tool
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@tool
def query_data(input_string: str):
    """Use this tool to query the knowledge base to answer questions about courses."""

    chroma_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    model = ChatOpenAI(model="gpt-4o-mini", streaming=True)

    DB_FOLDER = "chatbot/chroma_db"

    # Load ChromaDB
    chroma_db = Chroma(
        persist_directory=DB_FOLDER,
        embedding_function=chroma_embeddings,
        collection_name="document_collection",
    )

    # FIX: Use `similarity_top_k` instead of `search_type`
    retriever = chroma_db.as_retriever(search_kwargs={'k': 15})  # Removed `search_type='mmr'`

    # FIX: Use `.invoke()` instead of `get_relevant_documents()`
    docs = retriever.invoke(input_string)

    print(f"Retrieved Documents: {[doc.page_content for doc in docs]}")

    if not docs:
        print("⚠️ No relevant documents found. Expanding search scope...")
        return "I couldn't find specific entry requirements for this course. Would you like me to check a similar program or an official university source?"

    # Convert docs list into a single formatted string
    docs_string = "\n\n".join([doc.page_content for doc in docs])

    # Improved structured response prompt
    template = """
    You are answering a user query based on retrieved documentation excerpts.
    Use only the provided context to generate a precise, factual, and well-structured response.
    Do not include any assumptions or extra information beyond what is given.

    - If the provided context does not contain enough information to answer the question, state:  
      "I could not find specific entry requirements for this course. However, I can check similar programs or direct you to an official university source."

    - Keep the response formal, clear, and concise.
    - Do not include any emojis, personal opinions, or speculative content.

    ==========
    Question: {question}
    ==========
    Context:
    {context}
    ==========
    Provide a factual and precise response:
    """

    prompt = ChatPromptTemplate.from_template(template)

    # Debug prompt formatting
    formatted_prompt = prompt.format(context=docs_string, question=input_string)
    print(f"Formatted Prompt:\n{formatted_prompt}")

    # Chain execution with properly formatted context
    chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}  # Ensure proper passthrough
            | prompt
            | model
            | StrOutputParser()
    )

    # Invoke the chain with properly formatted data
    answer = chain.invoke({"context": docs_string, "question": input_string})

    print(f"Answer: {answer}")
    return answer
