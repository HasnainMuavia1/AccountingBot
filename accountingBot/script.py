from groq import Groq as Groq2
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq


GROQ_API_KEY = "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"
client = Groq2(api_key=GROQ_API_KEY)
# Initialize LLM and embedding model once

Settings.llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY, temperature=0.5, max_tokens=2000)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Load documents and create index once
documents = SimpleDirectoryReader("media/documents").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(top_k=1, response_mode="tree_summarize",streaming=True)
streaming_response = query_engine.query(
    "how to extract data in the format of dataev",
)
res = streaming_response.print_response_stream()
