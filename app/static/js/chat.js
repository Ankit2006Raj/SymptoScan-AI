document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesWrapper = document.getElementById('messages-wrapper');
    const welcomeState = document.getElementById('welcome-state');
    const typingIndicator = document.getElementById('typing-indicator');
    const chatAnchor = document.getElementById('chat-anchor');
    const btnNewChat = document.getElementById('btn-new-chat');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    let sessionId = null;
    let isWaiting = false;

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight < 150 ? this.scrollHeight : 150) + 'px';
        if (this.value.trim() !== '') {
            sendBtn.classList.remove('opacity-50');
        } else {
            sendBtn.classList.add('opacity-50');
        }
    });

    // Enter key to send (Shift+Enter for newline)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isWaiting) chatForm.dispatchEvent(new Event('submit'));
        }
    });

    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.querySelector('.text-xs').textContent;
            chatInput.value = text;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    btnNewChat.addEventListener('click', () => {
        sessionId = null;
        messagesWrapper.innerHTML = '';
        messagesWrapper.classList.add('hidden');
        welcomeState.classList.remove('hidden');
        chatInput.value = '';
        chatInput.style.height = 'auto';
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message || isWaiting) return;

        // Update UI State
        isWaiting = true;
        chatInput.value = '';
        chatInput.style.height = 'auto';
        sendBtn.disabled = true;
        
        welcomeState.classList.add('hidden');
        messagesWrapper.classList.remove('hidden');

        // Add User Message
        appendMessage('user', message);

        // Show typing
        messagesWrapper.appendChild(typingIndicator);
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, session_id: sessionId })
            });

            const data = await response.json();

            if (data.success) {
                sessionId = data.session_id; // Save session
                typingIndicator.classList.add('hidden');
                appendMessage('assistant', data.response);
            } else {
                throw new Error(data.error || 'Failed to get response');
            }
        } catch (error) {
            typingIndicator.classList.add('hidden');
            appendMessage('error', 'Sorry, I encountered an error. Please try again.');
        } finally {
            isWaiting = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    function appendMessage(role, content) {
        const div = document.createElement('div');
        
        // Very basic markdown to HTML for bold and newlines
        const formattedContent = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        if (role === 'user') {
            div.className = 'flex justify-end fade-in';
            div.innerHTML = `
                <div class="bg-primary text-white rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[85%] sm:max-w-[75%] shadow-sm">
                    <p class="text-sm m-0">${formattedContent}</p>
                </div>
            `;
        } else if (role === 'assistant') {
            div.className = 'flex justify-start fade-in';
            div.innerHTML = `
                <div class="flex gap-3 max-w-[90%] sm:max-w-[85%]">
                    <div class="w-8 h-8 rounded-full bg-blue-100 text-primary flex-shrink-0 flex items-center justify-center mt-1">
                        <i class="fa-solid fa-robot text-xs"></i>
                    </div>
                    <div class="bg-slate-100 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm text-slate-700 text-sm leading-relaxed">
                        ${formattedContent}
                    </div>
                </div>
            `;
        } else {
            div.className = 'flex justify-center fade-in w-full my-2';
            div.innerHTML = `
                <div class="bg-red-50 text-red-500 text-xs py-2 px-4 rounded-full border border-red-100 flex items-center gap-2">
                    <i class="fa-solid fa-circle-exclamation"></i> ${content}
                </div>
            `;
        }
        
        messagesWrapper.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatAnchor.scrollIntoView({ behavior: 'smooth' });
    }
});
