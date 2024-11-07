import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import re
from .models import ChatSession, Accounting, Params, ChatHistory, Taxes
from groq import Groq as Groq2

# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = "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"
client = Groq2(api_key=GROQ_API_KEY)
# Initialize LLM and embedding model once
Settings.llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY, temperature=0.5, max_tokens=2000)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Load documents and create index once
documents = SimpleDirectoryReader("media/documents").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(top_k=1, response_mode="tree_summarize")


def generate_prompt(chat_query):
    # Determine if the query is in German
    is_german_query = bool(re.search(r'[äöüßÄÖÜ]', chat_query)) or ('de' in chat_query.lower())

    # Construct the response message
    if is_german_query:
        response_message = (
            f"Du bist ein Buchhaltungsassistent. Wenn die Anfrage nur ein Gruß wie 'Hallo' ist, antworte freundlich, aber gib keine zusätzlichen Informationen. "
            f"Falls eine kurze Antwort gewünscht ist, gib eine prägnante Antwort basierend auf den Dokumentinhalten. "
            f"Für alle anderen Fragen beantworte die folgende Frage in einem klaren und strukturierten Format: "
            f"Verwende '###' nur für Überschriften, nummerierte Schritte (z.B., '1.', '2.') nur für Anweisungen, und '-' für zusätzliche Details oder optionale Informationen. "
            f"Verwende keine zusätzlichen Symbole oder Formatierungen, die nicht ausdrücklich gewünscht sind. {chat_query}"
        )
    else:
        response_message = (
            f"You are an accounting assistant. If the query is just a greeting like 'hello,' respond politely but do not provide additional information. "
            f"If a brief answer is requested, provide a concise response based on document content. "
            f"For all other queries, answer the following question in a clear and structured format: "
            f"Use '###' only for headings, numbered steps (e.g., '1.', '2.') only for instructions, and '-' for any additional details or optional information. "
            f"Avoid extra symbols or formatting beyond what is specified. {chat_query}"
        )

    # Query the engine
    bot_response = query_engine.query(response_message)
    response_text = bot_response.text if hasattr(bot_response, 'text') else str(bot_response)
    return response_text


def index(request, session_id=None):
    if request.method == 'POST':
        chat_query = request.POST.get('query')

        # Check if session_id exists; if not, create one
        if session_id is None:
            # Generate a new UUID for the session
            session_id = uuid.uuid4()
            # Return new session_id in the response
            response_text = generate_prompt(chat_query)
            generate_session_id(chat_query, session_id)
            save_chat_history_in_database(session_id, chat_query, response_text)
            return JsonResponse({'new_session_id': str(session_id), 'message': response_text, 'status': 'success'})

        # Process the query with the existing session_id
        try:
            response_text = generate_prompt(chat_query)
            save_chat_history_in_database(session_id, chat_query, response_text)
            return JsonResponse({'message': response_text, 'status': 'success'})

        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 'error'})

    # Render the chat page with the session_id (if any)
    return render(request, 'chat.html', {'session_id': session_id})


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
    return render(request, 'params.html')


def generate_session_id(user_chat, session_id):
    # Create a new chat session with a unique title
    try:
        title = generate_title_of_the_chat(user_chat)  # Replace with your method of generating unique titles
        ChatSession.objects.create(message_title=title, session_id=session_id)
    except Exception as e:
        return JsonResponse({'message': str(e), 'status': 'error'})


def save_chat_history_in_database(session_id, message_user, message_bot):
    try:
        # Retrieve the ChatSession instance using the session_id
        session = ChatSession.objects.get(session_id=session_id)

        # Create the ChatHistory entry
        ChatHistory.objects.create(
            session=session,  # Passing the actual ChatSession instance
            message_user=message_user,
            message_bot=message_bot
        )
        print('Saved successfully')
    except ChatSession.DoesNotExist:
        # Handle case where the session does not exist
        return JsonResponse({'message': 'Session does not exist', 'status': 'error'})
    except Exception as e:
        return JsonResponse({'message': str(e), 'status': 'error'})


def generate_title_of_the_chat(user_chat):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Given a user message or chat history, create a brief and descriptive 2-3 word title "
                           "summarizing the main topic or intent. Titles should be concise, capturing the essence of "
                           "the conversation."
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": f"{user_chat}",
            }
        ],
        model="llama3-8b-8192",
        temperature=0.3,
        max_tokens=50,
        top_p=1,
        stop=None,

        stream=False,
    )
    return chat_completion.choices[0].message.content
