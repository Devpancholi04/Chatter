$(document).ready(function () {
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;

    fetchRecentCommunitiesDetails(uuid, username);

    // setInterval(function (){
    //     fetchRecentCommunitiesDetails(uuid, username)
    // }, 60000);
});


function updateCommunitySection(messages){
    const communityConatiner = document.getElementById("list-contacts");
    communityConatiner.innerHTML = "";

    messages.forEach(chat => {
        const communitiesElement = document.createElement('li');
        communitiesElement.classList.add("contact");

        communitiesElement.innerHTML = `
            <div class="chatting" onclick='openChat("${chat.full_name}", "${chat.image_url}","${encodeURIComponent(JSON.stringify(chat))}")'>
                <div class="chat-item">
                    <div class="user-icon">
                        <img src="${chat.image_url}" alt="user-logo">
                    </div>

                    <div class="chat-details">
                        <div class="chat-headers">
                            <span class="chat-name">${chat.full_name}</span>
                            ${chat.unread_count > 0 ? `<span class="message-count">${chat.unread_count}</span>` : ""}
                        </div>
                                
                        <div class="chat-base">
                            <p class="message-preview"> ${truncateText(chat.last_message)} </p>
                            <p class="message-time"> ${chat.last_msg_time} </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        const starthr = document.createElement("hr");
        communityConatiner.prepend(starthr);
        communityConatiner.prepend(communitiesElement);    
    });
}

function fetchRecentCommunitiesDetails(uid, username){
    $.ajax({
        url : `/community/api/recent-messages/${uid}/ref=${username}`,
        type : "GET",
        datatype : "json",
        success : function (response) {
            let message = response.message || [];
            if (Array.isArray(message)) {
                updateCommunitySection(message);
            }
        },
    });
}

function truncateText(text) {
    if (!text) return '';
    return text.length > 30 ? text.slice(0, 30) + '...' : text;
}


let chatSocket = null;

function openChat(name, image_url, chat){
    const communityContainer = document.getElementById('chatContainer');
    communityContainer.innerHTML = `
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
    // console.log(chat_data);

    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;

    if (chat_data.community_id){
        load_community_old_messages(chat_data);

        let markCommunityReadUrl = `/community/api/mark-as-read/messages/cid=${chat_data.community_id}/uid=${uuid}/username=${username}/`;
        fetch(markCommunityReadUrl)
            .then(response =>{
                return response.json();
            })
            .then(data =>{
                fetchRecentCommunitiesDetails(uuid, username);
            })
    }


    const inputField = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendBtn');

    inputField.focus();

    sendButton.addEventListener('click', sendMessage);

    inputField.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
}

function sendMessage(){
    const input = document.getElementById('messageInput');

    if (input.value.trim() !== '' && chatSocket) {
        const messageData = JSON.stringify({
            'message': input.value,
        });

        // chat socket send function will be called here
        chatSocket.send(messageData);
        input.value = '';
    }
}

function CloseBtn(){
    if (chatSocket) {
        chatSocket.close();
        chatSocket = null;
    }

    document.getElementById('chatContainer').innerHTML = '';
}

function load_community_old_messages(chat){
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;
    // console.log(chat.community_id);
    // console.log(chat.full_name);

    if (chat.community_id){
        let communityMessageUrl = `/community/api/load/message/history/cid=${chat.community_id}/ref=${uuid}/refu=${username}/`;
        // console.log(communityMessageUrl);
        fetch(communityMessageUrl)
            .then(response => response.json())
            .then(data => {
                // console.log(data);
                let messageArray = Object.values(data.message);
                // console.log(data.message);
                messageArray.forEach(msg => {   
                    let isSender = msg.is_send;
                    let datetime = `${msg.date} ${msg.time}`;
                    DisplayCommunityMessages(msg.message, msg.sender_name, datetime, isSender);
                });
            })
        
            const community_name = `${chat.full_name}`.toLowerCase().replace(/\s+/g, '-');
            console.log(`ws://${window.location.host}/ws/community/chats/${chat.community_id}/${community_name}/`);
            chatSocket = new WebSocket(`ws://${window.location.host}/ws/community/chats/${chat.community_id}/${community_name}/`);

            chatSocket.onopen = function () {
                console.log("✅ community WebSocket Connected connection opened.")
            }

            chatSocket.onclose = function () {
                console.warn("⚠️ WebSocket connection closed.");
            };

            chatSocket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                let datetime = `${data.date} ${data.time}`;
    
                DisplayCommunityMessages(data.message, data.sender_name, datetime, data.is_send);
                fetchRecentCommunitiesDetails(uuid, username);
            };

            chatSocket.onerror = function (e) {
                console.error("❌ WebSocket error:", e);
            };
    }       
}

function DisplayCommunityMessages(message, senderName, time, isSender){
    const messageContainer = document.getElementById("messages");

    const messageElement = document.createElement("div");
    messageContainer.classList.add('message');

    if (isSender) {
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