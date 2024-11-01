import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import re
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = "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"

# Initialize LLM and embedding model once
Settings.llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY,temperature=0.5,max_tokens=2000)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Load documents and create index once
documents = SimpleDirectoryReader("media/documents").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(top_k=1,response_mode="tree_summarize")


def index(request):
    if request.method == 'POST':
        chat_query = request.POST.get('query')

        # Prepare and execute the query
        try:
            # Check if the query is in English or German (this could be expanded using a language detection library)
            is_german_query = bool(re.search(r'[äöüßÄÖÜ]', chat_query)) or ('de' in chat_query.lower())

            # Construct the response prompt accordingly
            if is_german_query:
                response_message = (
                    f"Du bist ein Buchhaltungsassistent. Bitte beantworte die folgende Frage genau und ausschließlich auf Basis der Dokumente: {chat_query}"
                )
            else:
                response_message = (
                    f"You are an accounting assistant. Please answer the following question in detail, "
                    f"using only information from the provided documents: {chat_query}"
                )

            # Query the engine
            bot_response = query_engine.query(response_message,)

            # Ensure the response is serializable
            response_text = bot_response.text if hasattr(bot_response, 'text') else str(bot_response)

            print(f"Bot response: {response_text}")
            return JsonResponse({'message': response_text, 'status': 'success'})

        except Exception as e:
            print(f"Error during query processing: {e}")
            return JsonResponse({'message': str(e), 'status': 'error'})

    return render(request, 'chat.html')


def upload(request):
    if request.method == 'POST' and request.FILES.getlist('file'):
        files = request.FILES.getlist('file')
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents')

        # Ensure the directory exists
        os.makedirs(upload_dir, exist_ok=True)

        # Save each file with optimized file handling
        try:
            for file in files:
                file_path = os.path.join(upload_dir, file.name)
                with default_storage.open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            return HttpResponse("Files uploaded successfully!")

        except Exception as e:
            print(f"Error uploading files: {e}")
            return JsonResponse({'message': f"Failed to upload files: {str(e)}", 'status': 'error'})

    return render(request, 'uppload.html')

def Dashboard(request):
    return render(request,'params.html')