const chatBox = document.getElementById('chatBox');
const input = document.getElementById('messageInput');
const sendbtn = document.getElementById('SendBtn');

const socket = new WebSocket(`ws://${window.location.host}/ws/AI/chats/`);

socket.onopen = function () {
    console.log("Connected to AI...");
    DisplayStaticMessage("Welcome to Chatter AI", "bot");
    DisplayStaticMessage("How may I assist you Today?", "bot");
};

socket.onerror = function () {
    console.log("connection error");
    DisplayStaticMessage("Something went wrong! Try Again", "bot");
};

socket.onmessage = function (event) {
    const response = JSON.parse(event.data);
    if (response.message){
        appendStreamingMessage(response.message);
    }
    sendbtn.disabled = false;
};

function sendMessage(){
    const message = input.value.trim(); 
    if (message === "") return;

    if(socket.readyState !== WebSocket.OPEN){
        DisplayStaticMessage("Connection Lost! Trying to Reconnect.....", "bot");

        socket.onopen = function() {
            DisplayStaticMessage("Reconnected!","bot");
            socket.send(JSON.stringify({ message }));
        };

        socket.onerror = function() {
            DisplayStaticMessage("Failed to reconnect. Please try again later.", "bot");
        };

        return;
    }

    DisplayStaticMessage(message, "user");

    socket.send(JSON.stringify({ message }));
    input.value = "";
    sendbtn.disabled = true;

    messageCounter++;
    const botMessageDiv = document.createElement("div");
    botMessageDiv.classList.add("message","bot");
    botMessageDiv.setAttribute("data-id", messageCounter);
    chatBox.appendChild(botMessageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendbtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", function (event){
    if(event.key === "Enter"){
        event.preventDefault();
        sendMessage();
    }
})

function DisplayStaticMessage(text, sender){
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message",sender);
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

let messageCounter = 0;

function appendStreamingMessage(text) {
    const botMessageDiv = document.querySelector(`[data-id="${messageCounter}"]`);
    if (!botMessageDiv) return;

    const formattedHTML = formatMessage(text); // this returns proper HTML
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = formattedHTML;

    const words = [];
    tempDiv.childNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) {
            words.push(...node.textContent.split(/(\s+)/));
        } else {
            words.push(node.outerHTML); // push HTML blocks like <b>word</b>
        }
    });

    botMessageDiv.innerHTML = "";
    let index = 0;

    function typeWord() {
        if (index < words.length) {
            if (words[index].startsWith("<") && words[index].endsWith(">")) {
                botMessageDiv.innerHTML += words[index] + " ";
            } else {
                botMessageDiv.innerHTML += words[index];
            }

            chatBox.scrollTop = chatBox.scrollHeight;
            index++;
            setTimeout(typeWord, 10);
        }
    }

    typeWord();
}


function formatMessage(text) {

    text = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");


    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');


    text = text.replace(/^\d+\.\s(.*)/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)/gs, '<ol>$1</ol>');


    text = text.replace(/^- (.*)/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');


    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    text = text.replace(/\n{2,}/g, '</p><p>'); 
    text = text.replace(/\n/g, '<br>');         
    text = '<p>' + text + '</p>';               

    text = text.replace(/\\boxed{([\s\S]*?)}/g, function(match, p1) {
        return p1.trim().replace(/\n/g, "<br>");
    });

    return text;
}
