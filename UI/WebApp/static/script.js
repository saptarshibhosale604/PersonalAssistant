let button = document.querySelector("#btn-yes")

$(document).ready(function () {
    // $('#btn-send').click(function () {
    //     const userMessage = $('#user-input').val().trim();
    //     if (userMessage === "") return;

    //     // console.log("userMessage: ",userMessage);

    //     // Append human message
    //     $('#chat-body').append(`<div class="message human-message">${userMessage}</div>`);

    //     // Clear input
    //     $('#user-input').val('');

    //     // Typing indicator
    //     $('#chat-body').append(`
    //         <div class="typing-indicator" id="typing">
    //             <div class="typing-dot"></div>
    //             <div class="typing-dot"></div>
    //             <div class="typing-dot"></div>
    //         </div>
    //     `);

    //     // Scroll to bottom
    //     $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);

    //     // Send to server
    //     $.ajax({
    //         url: '/userInputMessage',
    //         method: 'POST',
    //         contentType: 'application/json',
    //         data: JSON.stringify({ message: userMessage }),
    //         success: function (data) {
    //             // console.log(${data.bot});
    //             // console.log(data.bot);
    //             $('#typing').remove();
    //             $('#chat-body').append(`<div class="message bot-message" style="white-space: pre-line">${data.bot}</div>`);
    //             $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
    //         }
    //     });

    //     // Check for tools needed
    //     $.ajax({
    //         url: '/checkToolsRequiredFile',
    //         method: 'POST',
    //         contentType: 'application/json',
    //         data: JSON.stringify({ message: "na" }),
    //         success: function (data) {
    //             if(data.bot != "na"){
    //                 $('#typing').remove();
    //                 $('#chat-body').append(`<div class="message bot-message">${data.bot}</div>`);
    //                 $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
    //             }
    //         }
    //     });
    // });
    
    // v01
    // $('#btn-send').click(function () {
    //     const userMessage = $('#user-input').val().trim();
    //     console.log("btn-send pressed")
    //     if (userMessage === "") return;
        
    //     $('#chat-body').append(`<div class="message human-message">${userMessage}</div>`);
    //     $('#user-input').val('');
    
    //     // Typing indicator
    //     $('#chat-body').append(`
    //         <div class="typing-indicator" id="typing">
    //             <div class="typing-dot"></div>
    //             <div class="typing-dot"></div>
    //             <div class="typing-dot"></div>
    //         </div>
    //     `);
    
    //     // Setup stream
    //     const eventSource = new EventSourcePolyfill('/streamUserInputMessage', {
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         payload: JSON.stringify({ message: userMessage })
    //     });
    
    //     let botMessage = '';
    //     eventSource.onmessage = function (e) {
    //         const content = e.data;
    //         botMessage += content;
    //         console.log("Received chunk: ", content);
    //         $('#typing').remove();
    //         $('#chat-body').append(`<div class="message bot-message">${content}</div>`);
    //         $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
    //     };
    
    //     eventSource.onerror = function () {
    //         eventSource.close();
    //     };
    // });

    // V02
    $('#btn-send').click(function () {
        const userMessage = $('#user-input').val().trim();
        if (userMessage === "") return;
    
        $('#chat-body').append(`<div class="message human-message">${userMessage}</div>`);
        $('#user-input').val('');
    
        $('#chat-body').append(`
            <div class="typing-indicator" id="typing">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `);
    
        const threadId = "1";
        const modeLLM = "local";
        const modeContext = "yes";
    
        const url = `/streamUserInputMessage?message=${encodeURIComponent(userMessage)}&threadId=${threadId}&modeLLM=${modeLLM}&modeContext=${modeContext}`;
        const eventSource = new EventSource(url);
    
        let botMessage = '';
        const botMessageId = `bot-msg-${Date.now()}`; // unique id
        $('#chat-body').append(`<div id="${botMessageId}" class="message bot-message"></div>`);
        
        // V03
        eventSource.onmessage = function (e) {
            const content = e.data;
            // $('#chat-body').append(`<div class="message bot-message">Message:</div>`);
            if (content === "[[END]]") {
                eventSource.close();
                // console.log("Streaming complete.");
                return;
            }
            // V03
            // console.log("Received chunk: ", content); 

            // div01.innerHTML += content;
            document.getElementById(botMessageId).innerHTML += content;

            botMessage += content;
            
            // $('#typing').remove();
            // $('#chat-body').append(`<div class="message bot-message">${content}</div>`);
            // $('#chat-body')
            $('#typing').remove();
            // $('#chat-body').append(`<div class="message bot-message">${content}</div>`);
            $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
        };
    
        eventSource.onerror = function () {
            eventSource.close();
        };
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

