document.getElementById('sendButton').addEventListener('click', function() {
    const input = document.getElementById('messageInput');
    const messageText = input.value;

    if (messageText.trim() !== '') {
        displayMessage(messageText, 'sent');
        input.value = '';

        // Simulate receiving a response
        setTimeout(() => {
            displayMessage('This is a response', 'received');
        }, 1000);
    }
});

function displayMessage(text, type) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
}