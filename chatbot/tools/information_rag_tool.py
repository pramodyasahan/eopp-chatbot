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

from langchain.agents import tool
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


@tool
def query_data(input_string: str):
    """Use this tool to query knowledge base to answer questions about courses."""
    chroma_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    model = ChatOpenAI(model_name="gpt-4o-mini", streaming=True)

    chroma_db = Chroma(
        persist_directory="../chroma_db",
        embedding_function=chroma_embeddings,
        collection_name="spec",
    )
    retriever = chroma_db.as_retriever(search_kwargs={'k': 4})

    template = """You are given a question and some extracted parts from several documentation that can be used to answer the question.
    Give complete detailed answer.

    ==========
    Question: {question}
    =========
    {context}
    =========
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
    )

    answer = chain.invoke(input_string)
    return (answer)
