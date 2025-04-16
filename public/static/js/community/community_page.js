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

    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;

    // load_community_old_messages(chat_data);

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

    if (input.value.trim() !== '') { //&& chatSocket
        const messageData = JSON.stringify({
            'message': input.value,
        });

        // chat socket send function will be called here
        input.value = '';
    }
}

function CloseBtn(){
    // if (chatSocket) {
    //     chatSocket.close();
    //     chatSocket = null;
    // }

    document.getElementById('chatContainer').innerHTML = '';
}

function load_community_old_messages(message){
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;
}