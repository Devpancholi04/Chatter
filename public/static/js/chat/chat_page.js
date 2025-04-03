$(document).ready(function() {
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;
    // console.log(uuid);
    // console.log(username);
    function fetchRecentChatDetails(uid, username){

        $.ajax({
            url: `/chats/api/recent-messages/${uid}/ref=${username}/`,
            type: "GET",
            datatype: "json",
            success: function(response){
                // console.log("Response : " + response);

                let chats = response.message || [];
                if (Array.isArray(chats)){
                    updateChatSection(chats);
                }
            },
        });
    }


    function updateChatSection(chats){
        const chatContainer = document.getElementById("list-contacts")
        chatContainer.innerHTML = "";

        chats.forEach(chat => {
            const chatElement = document.createElement("li");
            chatElement.classList.add("contact");
            
            chatElement.innerHTML = `
                <div class="chatting" onclick='openChat("${chat.full_name}", "${chat.image_url}","${encodeURIComponent(JSON.stringify(chat))}")'>
                    <div class="chat-item">
                        <div class="user-icon">
                            <img src="${chat.image_url}" alt="user-logo">
                        </div>
    
                        <div class="chat-details">
                            <div class="chat-headers">
                                <span class="chat-name">${chat.full_name}</span>
                                <span class="message-count"> ${chat.unread_count} </span>
                            </div>
                                    
                            <div class="chat-base">
                                <p class="message-preview"> ${chat.last_message} </p>
                                <p class="message-time"> ${chat.last_msg_time} </p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            const createElement1 = document.createElement("hr");
            chatContainer.append(chatElement);
            chatContainer.append(createElement1);
        });
    }

    fetchRecentChatDetails(uuid, username);

    setInterval(function(){
        fetchRecentChatDetails(uuid, username)
    }, 60000);

});

let chatSocket = null;

function openChat(name, image_url, chat){
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = `
        <div class="chat-box">
            <div class="chat-headering">
                <img src="${image_url}" alt="${name}" class="chat-user-icon">
                <span class="chat-user-name">${name}</span>
                <span class="close-btn" onclick="CloseBtn()">
                    <i class="fa-solid fa-xmark"></i>
                </span>
            </div>
            <div class="messages" id="messages">
            
            </div>
            <div class="message-input">
                <input type="text" id="messageInput" placeholder="Type a message...">
                <button onclick="sendMessage()" id="sendBtn">Send</button>
            </div>
        </div>
    `;

    document.querySelector('.chat-box').style.display = 'flex';

    let chat_data = JSON.parse(decodeURIComponent(chat)); 
    
    load_old_messages(chat_data)



    const inputField = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendBtn');

    inputField.focus();

    sendButton.addEventListener('click', sendMessage);

    inputField.addEventListener('keypress', function (event){
        if (event.key === 'Enter'){
            event.preventDefault();
            sendMessage();
        }
    });
}

function sendMessage(){
    const input = document.getElementById('messageInput');

    if (input.value.trim() !== ''){
        input.value = '';
    }
}


function CloseBtn(){
    document.getElementById('chatContainer').innerHTML = '';
}

function load_old_messages(chat){
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;  
    
    if (chat.group_id){
        let groupMessageUrl = `/chats/api/load/group/chats/history/gid=${chat.group_id}/ref=${uuid}/refu=${username}`;
        fetch(groupMessageUrl)
            .then(response => response.json())
            .then(data => {
                let messageArray = Object.values(data.Messages);

                messageArray.forEach(msg => {
                    let isSender = msg.is_send;
                    let datetime = `${msg.date} ${msg.time}`;
                    DisplayGroupMessages(msg.message, msg.sender_name, datetime, isSender);
                });
            })
    } else{

        let directMessageUrl = `/chats/api/load/one-2-one/chats/history/sid=${uuid}/sref=${username}/rid=${chat.uid}/rref=${chat.username}/`
        fetch(directMessageUrl)
            .then(response => response.json())
            .then(data => {
                // console.log('One to one chat Message: ', data.Messages);
                
                let messageArray = Object.values(data.Messages);
                
                messageArray.forEach(msg => {
                    let isSender = msg.is_send;
                    let datetime = `${msg.date} ${msg.time}`;
                    DisplayMessage(msg.message,datetime,isSender);
                });

            })
            .catch(error => console.error('error while fetching data ', error));
    }
}

function DisplayMessage(message,time, isSender){
    const messageContainer = document.getElementById("messages");

    const messageElement = document.createElement("div");
    messageContainer.classList.add('message');

    if (isSender){
        messageElement.classList.add("sent");
    } else {
        messageElement.classList.add("received");
    }

    messageElement.innerHTML = `
        <p class="message-text">${message}</p>
        <span class="message-time">${time}</span>
    `;

    messageContainer.appendChild(messageElement);
    messageContainer.scrollTop = messageContainer.scrollHeight;

}

function DisplayGroupMessages(message, senderName, time, isSender){
    const messageContainer = document.getElementById("messages");

    const messageElement = document.createElement("div");
    messageContainer.classList.add('message');

    if (isSender){
        messageElement.classList.add("sent");
    } else {
        messageElement.classList.add("received");
    }

    messageElement.innerHTML = `
        <p class="sender-name">${senderName}</p>
        <p class="message-text">${message}</p>
        <span class="message-time">${time}</span>
    `;

    messageContainer.appendChild(messageElement);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

