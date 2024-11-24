from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq  # Hypothetical import for Groq model

# Load documents
documents = SimpleDirectoryReader(r"D:\accountingBot\media\documents").load_data()
# Set the embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Set the language model to Groq
Settings.llm = Groq(model="llama3-70b-8192",api_key= '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', request_timeout=360.0)  # Replace "groq_model_name" with the specific model name for Groq

# Create the index from documents
index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine()
response = query_engine.query("what is data center")
print(response)