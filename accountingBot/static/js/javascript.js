
  const textarea = document.querySelector('.chat-input');
  const initialHeight = '48px';

  function resetTextarea() {
    textarea.style.height = initialHeight;
    textarea.value = '';
  }

  textarea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
  });

  // Handle Enter key
  textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (this.value.trim().length > 0) {
        $('#chat-form').submit();
      }
    }
  });

  const sendButton = document.getElementById('send-button');
  const chatInput = document.getElementById('chat-input');

  chatInput.addEventListener('input', function () {
    if (chatInput.value.trim().length > 0) {
      sendButton.classList.add('active');
    } else {
      sendButton.classList.remove('active');
    }
  });


function appendMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'} clearfix`;

    if (!isUser) {
        const botIcon = document.createElement('div');
        botIcon.className = 'bot-icon';
        botIcon.innerHTML = '<i class="fas fa-robot"></i>';
        messageDiv.appendChild(botIcon);
    }

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    // Add copy button for both user and bot messages
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-button';
    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
    copyButton.onclick = function() {
        navigator.clipboard.writeText(content).then(() => {
            copyButton.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    };

    // Parse content by lines
    const lines = content.split('\n');
    lines.forEach(line => {
        line = line.trim();

        if (line.startsWith('###')) {
            // Main heading
            const heading = document.createElement('h3');
            heading.textContent = line.replace(/^###\s*/, '');  // Remove ### marker
            messageContent.appendChild(heading);

        } else if (line.startsWith('**') && line.endsWith('**')) {
            // Subheading
            const subheading = document.createElement('h4');
            subheading.textContent = line.replace(/^\*\*|\*\*$/g, '');  // Remove ** markers
            messageContent.appendChild(subheading);

        } else if (/^\d+\./.test(line)) {
            // Numbered step (ordered list)
            let list;
            if (!messageContent.lastElementChild || messageContent.lastElementChild.tagName !== 'OL') {
                list = document.createElement('ol');
                messageContent.appendChild(list);
            } else {
                list = messageContent.lastElementChild;
            }

            const listItem = document.createElement('li');
            listItem.textContent = line.replace(/^\d+\.\s*/, '');  // Remove number marker
            list.appendChild(listItem);

        } else if (line.startsWith('- ')) {
            // Bullet point (unordered list)
            let list;
            if (!messageContent.lastElementChild || messageContent.lastElementChild.tagName !== 'UL') {
                list = document.createElement('ul');
                messageContent.appendChild(list);
            } else {
                list = messageContent.lastElementChild;
            }

            const listItem = document.createElement('li');
            listItem.textContent = line.replace(/^- /, '');  // Remove bullet marker
            list.appendChild(listItem);

        } else {
            // Plain paragraph
            const paragraph = document.createElement('p');
            paragraph.textContent = line;
            messageContent.appendChild(paragraph);
        }
    });



    // Append the copy button at the end
    messageContent.appendChild(copyButton);
    messageDiv.appendChild(messageContent);

    const chatMessages = document.getElementById('chat-messages');
    chatMessages.appendChild(messageDiv);

    // Auto-scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add event listener for Enter key on both input fields
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['chat-input', 'chat-input-initial'];

    inputs.forEach(inputId => {
        const textarea = document.getElementById(inputId);
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (this.value.trim().length > 0) {
                    const form = this.closest('form');
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    });
});



// Ensure scrolling on overflow
const chatMessages = document.getElementById('chat-messages');
const observer = new MutationObserver(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

observer.observe(chatMessages, {
    childList: true,
    subtree: true
});
 function switchToRegularChat() {
  document.getElementById('initialState').style.display = 'none';
  document.getElementById('chat-messages').classList.remove('messages-hidden');
  document.getElementById('regularChatInput').classList.remove('messages-hidden');
}

  function showLoadingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message clearfix';
    messageDiv.id = 'loadingMessage';

    const botIcon = document.createElement('div');
    botIcon.className = 'bot-icon loading';
    botIcon.innerHTML = '<i class="fas fa-robot"></i>';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = 'Thinking...';

    messageDiv.appendChild(botIcon);
    messageDiv.appendChild(messageContent);
    document.getElementById('chat-messages').appendChild(messageDiv);

    // Scroll to bottom
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function removeLoadingIndicator() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
      loadingMessage.remove();
    }
  }

$(document).ready(function() {
    // Variable to hold session_id, which may change when switching chats
    let session_id = '{{ session_id|default_if_none:"" }}';

    // Check for session ID in URL on page load
    const urlSessionId = getSessionIdFromUrl();
    let currentSessionId = urlSessionId;

    if (urlSessionId) {
        loadChatHistory(urlSessionId);
    }

    function handleSubmit(event, formId) {
    event.preventDefault();

    const isInitialForm = formId === 'chat-form-initial';
    const inputId = isInitialForm ? 'chat-input-initial' : 'chat-input';
    const userQuery = $(`#${inputId}`).val().trim();

    if (userQuery.length === 0) {
        return;
    }

    if (isInitialForm) {
        switchToRegularChat();
    }

    // Display user message and clear input
    appendMessage(userQuery, true);
    $(`#${inputId}`).val('');
    showLoadingIndicator();

    // Determine URL based on session_id
    let url = session_id ? `/chat/${session_id}/` : `{% url "index" %}`;

    // Send AJAX request for chat submission
    $.ajax({
        url: url,
        method: 'POST',
        data: {
            'query': userQuery,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(response) {
            removeLoadingIndicator();

            // If a new session_id is created, update session_id and add chat to sidebar
            if (response.new_session_id && !session_id) {
                session_id = response.new_session_id;

                // Add new chat to sidebar
                const newChatItem = `
                    <div class="chat-item" data-session-id="${session_id}">
                        <i class="fas fa-comments"></i>
                        <span>${userQuery}</span>
                    </div>`;
                $('.chat-history').prepend(newChatItem);

                // Update URL to reflect the new session
                const newUrl = `${window.location.origin}/chat/${session_id}/`;
                history.replaceState(null, null, newUrl);

                // Add event listener to the new chat item
                $(`.chat-item[data-session-id="${session_id}"]`).on('click', function() {
                    fetchChatHistory(session_id);
                });
            }

            // Display bot response
            appendMessage(response.message, false);
        },
        error: function(error) {
            removeLoadingIndicator();
            console.error("Error:", error);
            appendMessage("Sorry, there was an error processing your request.", false);
        }
    });
}

function getSessionIdFromUrl() {
    const urlParts = window.location.pathname.split('/');
    return urlParts[2] || '';  // Assuming URL structure /chat/{session_id}/
}

    $('#chat-form').on('submit', function(event) {
        handleSubmit(event, 'chat-form');
    });

    $('#chat-form-initial').on('submit', function(event) {
        handleSubmit(event, 'chat-form-initial');
    });
    });
$(document).ready(function() {
    // Sidebar toggle functionality
    $('#sidebarToggle').on('click', function() {
        $('#sidebar').toggleClass('collapsed');
        $('#mainContent').toggleClass('expanded');
        $(this).toggleClass('shifted');
    });
});

// Add this event listener to the chat-item elements
$('.chat-item').on('click', function() {
    const sessionId = $(this).data('session-id');
    console.log(sessionId)
    fetchChatHistory(sessionId);
});


function fetchChatHistory(sessionId) {
        session_id = sessionId;  // Update the current session_id to the selected chat

        $.ajax({
            url: `/chat/${session_id}/history/`,
            method: 'GET',
            success: function(response) {
                // Clear existing chat messages
                $('#chat-messages').html('');

                // Switch to the regular chat interface
                switchToRegularChat();

                // Append retrieved chat messages
                response.forEach(message => {

                    appendMessage(message.message_user, true);
                    appendMessage(message.message_bot, false);
                });

                // Update the URL to reflect the selected session
                const newUrl = `${window.location.origin}/chat/${session_id}/`;
                history.replaceState(null, null, newUrl);
            },
            error: function(error) {
                console.error("Error:", error);
                appendMessage("Sorry, there was an error fetching the chat history.", false);
            }
        });
    }

    // Event listener for chat history items
    $('.chat-item').on('click', function() {
        const selectedSessionId = $(this).data('session-id');
        fetchChatHistory(selectedSessionId);
    });
// Function to handle starting a new chat
// Start a new chat session with error handling
    function startNewChat(event) {
      event.preventDefault();
      $.ajax({
        url: '{% url "new_session" %}',
        method: 'POST',
        data: {
          'csrfmiddlewaretoken': '{{ csrf_token }}'
        },

      });
    }

// Function to load chat history
function loadChatHistory(sessionId) {
    if (!sessionId) return;

    $.ajax({
        url: `/chat/${sessionId}/history/`,
        method: 'GET',
        success: function(response) {
            // Clear existing messages
            $('#chat-messages').html('');

            // Switch to regular chat interface
            switchToRegularChat();

            // Display each message pair
            response.forEach(message => {
                appendMessage(message.message_user, true);
                appendMessage(message.message_bot, false);
            });
        },
        error: function(error) {
            console.error("Error loading chat history:", error);
            appendMessage("Sorry, there was an error loading the chat history.", false);
        }
    });
}
document.addEventListener("DOMContentLoaded", function () {
    // Typing Effect for Initial State Text
    const textElement = document.querySelector(".initial-state h2");
    const text = "How can I help you today?";
    let index = 0;

    function type() {
        if (index < text.length) {
            textElement.textContent += text.charAt(index);
            index++;
            setTimeout(type, 30); // Adjust typing speed here
        }
    }

    // Clear the initial text and start the typing effect
    textElement.textContent = "";
    type();
});