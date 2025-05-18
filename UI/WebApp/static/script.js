let button = document.querySelector("#btn-yes")

$(document).ready(function () {
    $('#btn-send').click(function () {
        const userMessage = $('#user-input').val().trim();
        if (userMessage === "") return;

        // console.log("userMessage: ",userMessage);

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
                // console.log(${data.bot});
                // console.log(data.bot);
                $('#typing').remove();
                $('#chat-body').append(`<div class="message bot-message" style="white-space: pre-line">${data.bot}</div>`);
                $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
            }
        });

        // Check for tools needed
        $.ajax({
            url: '/checkToolsRequiredFile',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: "na" }),
            success: function (data) {
                if(data.bot != "na"){
                    $('#typing').remove();
                    $('#chat-body').append(`<div class="message bot-message">${data.bot}</div>`);
                    $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
                }
            }
        });
    });
    
    $('#user-input').keypress(function (e) {
        if (e.which === 13) {
            // console.log("Enter button pressed");
            $('#btn-send').click();
        }
    });

    // Yes and no buttons
    $('#btn-yes').click(function () {
        const userMessage = "y";
        // alert("hey there");
        console.log(button)
        button.disabled = true;
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
        const userMessage = "n";
        
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

