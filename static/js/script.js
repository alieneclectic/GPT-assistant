function sendMessage() {
    var messageInput = document.getElementById('messageInput');
    var sendButton = document.querySelector('button.btn');
    var loadingSpinner = document.getElementById('loading');
    var message = messageInput.value;

    // Show the loading spinner and disable the send button
    loadingSpinner.style.display = 'block';
    sendButton.disabled = true;

    fetch('/send_message', {
        method: 'POST',
        body: new URLSearchParams('message=' + message),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => response.json())
    .then(data => {
        // Display the assistant's response
        var chatbox = document.getElementById('chatbox');
        chatbox.innerHTML += '<div class="chat-message user-message">' + 'You: ' + message + '</div>';
        chatbox.innerHTML += '<div class="chat-message assistant-message">' + 
                               'Assistant: ' + 
                                marked.parse(data.response) + 
                             '</div>';
        messageInput.value = '';  // Clear input
        chatbox.scrollTop = chatbox.scrollHeight; // Scroll to the bottom
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        // Hide the loading spinner and enable the send button
        loadingSpinner.style.display = 'none';
        sendButton.disabled = false;
    });
}
