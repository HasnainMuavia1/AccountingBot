import json
import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import re
from langdetect import detect
from .models import ChatSession, Params, ChatHistory
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
    # Detect the language of the query
    try:
        detected_language = detect(chat_query)
    except Exception as e:
        detected_language = "en"  # Default to English in case of error

    # Construct the response message based on the detected language
    if detected_language == 'de':
        response_message = (
            f"Du bist ein Buchhaltungsassistent. Befolge die folgenden Regeln, um Anfragen passend zu beantworten:\n"
            f"1. **Falls die Anfrage ein einfacher Gruß ist (z.B. 'Hallo'):** Antworte höflich, ohne zusätzliche Informationen oder Details hinzuzufügen.\n"
            f"2. **Falls eine kurze Antwort angefragt wird:** Gib eine prägnante Antwort, die sich direkt auf die Inhalte des Dokuments bezieht.\n"
            f"3. **Für alle anderen Anfragen:** Strukturiere die Antwort klar und verständlich:\n"
            f"   - Verwende '###' nur für Hauptüberschriften.\n"
            f"   - Verwende '**' nur für Zwischenüberschriften.\n"
            f"   - Nutze nummerierte Schritte (z.B. '1.', '2.') nur für klar definierte Anweisungen.\n"
            f"   - Verwende '-' für zusätzliche Details oder optionale Informationen.\n"
            f"   - Vermeide jegliche Symbole oder Formatierungen, die nicht ausdrücklich angefragt wurden.\n\n"
            f"Hier ist die Antwort auf die Anfrage: {chat_query}\n"
            f"**Antwort nur auf Deutsch, keine andere Sprache verwenden.**"
        )
    else:
        response_message = (
            f"You are an accounting assistant. Follow these rules to respond appropriately:\n"
            f"1. **If the query is a simple greeting (e.g., 'hello'):** Respond politely without adding extra information or details.\n"
            f"2. **If a brief response is requested:** Provide a concise answer directly based on the document content.\n"
            f"3. **For all other queries:** Structure the response in a clear and readable format:\n"
            f"   - Use '###' only for main headings.\n"
            f"   - Use '**' only for subheadings.\n"
            f"   - Use numbered steps (e.g., '1.', '2.') only for specific instructions.\n"
            f"   - Use '-' for any additional details or optional information.\n"
            f"   - Avoid any extra symbols or formatting that hasn’t been explicitly requested.\n\n"
            f"Here is the response to the query: {chat_query}\n"
            f"**Reply only in English, do not use other languages.**"
        )

    # Query the engine
    bot_response = query_engine.query(response_message)
    response_text = bot_response.text if hasattr(bot_response, 'text') else str(bot_response)
    return response_text


def index(request, session_id=None):
    if request.method == 'POST':
        chat_query = request.POST.get('query')

        # For new chats (no session_id)
        if session_id is None:
            session_id = uuid.uuid4()
            response_text = generate_prompt(chat_query)
            generate_session_id(chat_query, session_id)
            save_chat_history_in_database(session_id, chat_query, response_text)
            return JsonResponse({
                'new_session_id': str(session_id),
                'message': response_text,
                'status': 'success'
            })

        # For existing chats
        try:
            response_text = generate_prompt(chat_query)
            save_chat_history_in_database(session_id, chat_query, response_text)
            return JsonResponse({
                'message': response_text,
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({
                'message': str(e),
                'status': 'error'
            })

    # GET request with session_id (loading specific chat)
    elif request.method == 'GET' and session_id:
        chat_messages = specific_chat_history_object(session_id)
        if chat_messages == 'failed':
            return JsonResponse({'error': 'Chat not found'}, status=404)

        return render(request, 'chat.html', {
            'session_id': session_id,
            'chat_messages': json.dumps(chat_messages),
            'sidebar_chats': ChatSession.objects.all().order_by('-created_at')
        })

    # Initial page load
    return render(request, 'chat.html', {
        'sidebar_chats': ChatSession.objects.all().order_by('-created_at')
    })


def new_session(request):
    return render(request, 'chat.html', {
        'sidebar_chats': ChatSession.objects.all().order_by('-created_at')
    })


def specific_chat_history_object(session_id):
    try:
        chat_history = ChatHistory.objects.filter(session__session_id=session_id)
        chat_messages = list(chat_history.values('message_user', 'message_bot'))
        return chat_messages
    except Exception as e:
        return 'failed'


def chat_history_all_objects(request, session_id):
    try:
        chat_history = ChatHistory.objects.filter(session__session_id=session_id)
        chat_messages = list(chat_history.values('message_user', 'message_bot'))
        return JsonResponse(chat_messages, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
    return render(request, 'params.html', {'obj': Params.objects.first()})


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
    # Define the message prompt more explicitly to guide concise title generation.
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "Given a user message or chat history, create a brief and descriptive 2-3 word title "
                    "summarizing the main topic or intent. Keep the title concise and meaningful, capturing "
                    "the core theme or purpose of the conversation. "
                    "If the user message is unclear or includes mistakes, still generate a 2-3 word title that reflects"
                    "the best interpretation of the topic. If the message is purely a greeting, such as 'Hello' or "
                    "'Hi,'"
                    "respond with 'Greeting' as the title."
                )
            },
            {
                "role": "user",
                "content": f"{user_chat}",
            }
        ],
        model="llama3-8b-8192",
        temperature=0.3,
        max_tokens=10,
        top_p=1,
        stop=None,
        stream=False,
    )

    # Get and clean the generated title.
    title = chat_completion.choices[0].message.content.strip()

    # Validate and ensure the title is concise and avoids greeting or overly long responses.
    if len(title.split()) > 3:
        title = ' '.join(title.split()[:3])  # Limit to 2-3 words if the generated title is too long

    # Handle titles that might be inappropriate or if only a greeting was detected.
    if "greeting" in title.lower() or title.lower() in ["hello", "hi", "greetings"]:
        title = "Greeting"

    return title


def Rename(request, session_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        try:
            obj = ChatSession.objects.get(session_id=session_id)
            obj.message_title = title
            obj.save()
            return JsonResponse({'message': 'success'})
        except Exception as e:
            return JsonResponse({'message': str(e)})


def delete(request, session_id):
    if request.method == 'GET':
        try:
            obj = ChatSession.objects.get(session_id=session_id)
            obj.delete()
            return JsonResponse({'message': 'success'})
        except Exception as e:
            return JsonResponse({'message': str(e)})


def params_save(request):
    if request.method == 'POST':
        try:
            data = request.POST
            rag_range_temp = data.get('rag_range_temp')
            print(rag_range_temp)
            rag_range_tokens = data.get('rag_range_tokens')
            print(rag_range_tokens)

            # Process the received data (e.g., save to database or further processing)
            obj, _ = Params.objects.get_or_create(id=1)
            obj.temperature = rag_range_temp
            obj.max_tokens = rag_range_tokens
            obj.save()

            # Respond with a success message
            return JsonResponse({'message': 'Successfully saved settings'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def ChatAnalysis():
    """
    Retrieve and concatenate all user and bot messages from the database.
    Returns:
        A string containing user and bot messages in chronological order.
    """
    obj = ChatHistory.objects.all().order_by("timestamp")  # Ensure messages are in order
    chat_context = ""
    for chat in obj:
        chat_context += f"User: {chat.message_user}\nBot: {chat.message_bot}\n"
    return chat_context.strip()


def analysisOfChat(user_chat, message):
    """
    Analyze user messages and generate insights using an AI model.

    Parameters:
    - user_chat: Context or conversation history related to the user's messages (optional).
    - message: A collection of user messages or a specific message that requires analysis.

    Returns:
    - A detailed analysis or insights about the provided user messages, such as:
      - The most frequent type of question or theme.
      - Common patterns in the messages.
      - Suggestions for improvement or trends in the conversation.

    The function uses a smart AI model to provide meaningful insights into the content
    and characteristics of the user's messages.
    """

    # AI-driven analysis using a chat model
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a highly intelligent assistant designed to provide insightful analysis "
                    "of user messages. Your goal is to process a set of user messages and provide "
                    "a detailed summary of insights. These insights should include patterns, trends, "
                    "frequently discussed topics, or unique observations about the messages. "
                    "\n\nKey Instructions:\n"
                    "1. If the user provides multiple messages, identify and describe the main trends, "
                    "frequent themes, or recurring questions.\n"
                    "2. Highlight the most commonly asked type of question or topic, if applicable.\n"
                    "3. Provide a brief summary or suggestions for better engagement if appropriate."
                    f"here are the questions {user_chat}"
                )
            },
            {
                "role": "user",
                "content": f"{message}",
            }
        ],
        model="llama3-8b-8192",
        temperature=0.6,  # Balances creativity and relevance in the response
        max_tokens=1500,  # Allows for a detailed analysis
        top_p=1,  # Determines the likelihood distribution for output
        stop=None,  # No specific stop sequence for the output
        stream=False,  # Disables streaming for a single response
    )

    # Return the AI-generated insights or analysis
    return chat_completion.choices[0].message.content


# user chat


@csrf_exempt
def Assistant_bot(request):
    if request.method == 'POST':
        chat_query = request.POST.get('query', '').strip()
        user_chat = ChatAnalysis()  # Retrieve chat history for analysis

        if not chat_query:
            return JsonResponse({'message': 'Query parameter is required.', 'status': 'error'}, status=400)

        try:
            # Pass user_chat to the analysis function
            response_text = analysisOfChat(user_chat=user_chat, message=chat_query)

            return JsonResponse({'message': response_text, 'status': 'success'})
        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {str(e)}', 'status': 'error'}, status=500)

    return JsonResponse({'message': 'Invalid request method. Please use POST.', 'status': 'error'}, status=405)
