$(document).ready(function () {
    $('#btn-send').click(function () {
        const userMessage = $('#user-input').val().trim();
        if (userMessage === "") return;

        // Append human message
        $('#chat-body').append(`<div class="message human-message">${userMessage}</div>`);

        // Clear input
        $('#user-input').val('');

        // Typing indicator
        $('#chat-body').append(`
            <div class="typing-indicator" id="typing">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `);

        // Scroll to bottom
        $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);

        // Send to server
        $.ajax({
            url: '/userInputMessage',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: userMessage }),
            success: function (data) {
                $('#typing').remove();
                $('#chat-body').append(`<div class="message bot-message">${data.bot}</div>`);
                $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
            }
        });
    });
    
    $('#user-input').keypress(function (e) {
        if (e.which === 13) {
            $('#send-btn').click();
        }
    });
    // Yes and no buttons
    $('#btn-yes').click(function () {
        const userMessage = "yes";
        
        // Typing indicator
        $('#chat-body').append(`
            <div class="typing-indicator" id="typing">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `);

        // Scroll to bottom
        $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);

        // Send to server
        $.ajax({
            url: '/userInputExtra',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: userMessage }),
            success: function (data) {
                $('#typing').remove();
                $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
            }
        });
    });

    $('#btn-no').click(function () {
        const userMessage = "no";
        
        // Typing indicator
        $('#chat-body').append(`
            <div class="typing-indicator" id="typing">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `);

        // Scroll to bottom
        $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);

        // Send to server
        $.ajax({
            url: '/userInputExtra',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: userMessage }),
            success: function (data) {
                $('#typing').remove();
                $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
            }
        });
    });
    
});
