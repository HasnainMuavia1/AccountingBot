
    // Slider functionality
    document.querySelectorAll('.slider').forEach(slider => {
    const valueDisplay = slider.parentElement.querySelector('.slider-value');
    slider.addEventListener('input', (e) => {
    valueDisplay.textContent = e.target.value;
    const percent = (e.target.value - e.target.min) / (e.target.max - e.target.min);
    valueDisplay.style.left = `${percent * 100}%`;
});
});

    // Textarea auto-resize
    const textarea = document.querySelector('.chat-input');
    const sendButton = document.getElementById('send-button');

    textarea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    sendButton.classList.toggle('active', this.value.trim().length > 0);
});

    // Chat message handling
    function appendMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    if (isUser) {
    messageDiv.innerHTML = `
                <div class="message-content">${content}</div>
            `;
} else {
    messageDiv.innerHTML = `
                <div class="bot-icon">
                    <i class="fas fa-robot" style="color: white;"></i>
                </div>
                <div class="message-container">
                    <div class="message-content">${content}</div>
                    <div class="message-actions">
                        <button class="action-button copy-btn" onclick="copyToClipboard(this)" data-content="${content}">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                </div>
            `;
}

    const chatMessages = document.getElementById('chat-messages');
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

    // Copy to clipboard
    function copyToClipboard(button) {
    const content = button.getAttribute('data-content');
    navigator.clipboard.writeText(content).then(() => {
    const icon = button.querySelector('i');
    icon.className = 'fas fa-check';
    setTimeout(() => {
    icon.className = 'fas fa-copy';
}, 1000);
});
}

    // Export chat functionality
    document.getElementById('export-chat').addEventListener('click', function() {
    const messages = document.getElementById('chat-messages').children;
    let chatText = '';

    Array.from(messages).forEach(message => {
    const isUser = message.classList.contains('user-message');
    const content = message.querySelector('.message-content').textContent;
    const timestamp = new Date().toISOString();
    chatText += `${isUser ? 'User' : 'Bot'} (${timestamp}): ${content}\n\n`;
});

    const blob = new Blob([chatText], {type: 'text/plain'});
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
});

    // Form submissions
    function sendMainRagData() {
    const formData = {
    rag_range_temp: document.getElementById('range-temp-rag').value,
    rag_range_tokens: document.getElementById('range-tokens-rag').value,
    csrfmiddlewaretoken: '{{ csrf_token }}'
};

    $.ajax({
    url: '{% url "params_save" %}',
    method: 'POST',
    data: formData,
    success: function(response) {
    document.getElementById('Error_rag').innerHTML = '<span class="text-success">Successfully saved settings</span>';
    setTimeout(() => {
    document.getElementById('Error_rag').innerHTML = '';
}, 3000);
},
    error: function(xhr) {
    document.getElementById('Error_rag').innerHTML = `<span class="text-danger">Error: ${xhr.statusText}</span>`;
}
});
}

    document.getElementById('main-rag').addEventListener('submit', function(e) {
    e.preventDefault();
    sendMainRagData();
});

    document.getElementById('chat-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (message) {
    appendMessage(message, true);
    input.value = '';
    input.style.height = 'auto';
    sendButton.classList.remove('active');

    $.ajax({
    url: '{% url "assistant" %}',
    method: 'POST',
    data: {
    query: message,
    csrfmiddlewaretoken: '{{ csrf_token }}'
},
    success: function(response) {
    appendMessage(response.message, false);
},
    error: function(error) {
    appendMessage("Sorry, there was an error processing your request.", false);
}
});
}
});

    // Enter key handling
    textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (this.value.trim()) {
    document.getElementById('chat-form').dispatchEvent(new Event('submit'));
}
}
});