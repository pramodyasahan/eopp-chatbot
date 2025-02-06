from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

memory_storage = StreamlitChatMessageHistory(key="chat_messages")

agent_memory = ConversationBufferMemory(memory_key="chat_history", human_prefix="user", chat_memory=memory_storage)
