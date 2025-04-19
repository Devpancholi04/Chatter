let uuid = document.getElementById('uid').innerText;
let username = document.getElementById('username').innerText;

$(document).ready(function () {
    fetchRecentChatDetails(uuid, username);
    fetchRecentCommunitiesDetails(uuid, username);

});


function fetchRecentChatDetails(uid, username){
    $.ajax({
        url: `/chats/api/recent-messages/${uid}/ref=${username}/`,
        type: "GET",
        datatype: "json",
        success: function (response) {

            let chats = response.message || [];
            if (Array.isArray(chats)) {
                updateChatSection(chats);
            }
        },
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

function updateChatSection(chats){

    const chatContainer = document.getElementById("sub-sections");
    chatContainer.innerHTML = `
    <p class='heading'>Recents Messages...</p>
    <hr>
    `;

    chats.forEach(chat => {
        const chatElement = document.createElement("div");
        chatElement.classList.add("chatSection");

        chatElement.innerHTML = `
            <a href="/chats/${uuid}/ref=${username}/#${chat.full_name}" class="chatting">
                <div class="chat-item">
                    <div class="user-icon">
                        <img src="${chat.image_url}" alt="User">
                    </div>
                    <div class="chat-details">
                        <div class="chat-header">
                            <span class="chat-name">${chat.full_name}</span>
                            ${chat.unread_count > 0 ? `<span class="message-count">${chat.unread_count}</span>` : ""}
                        </div>
                        <p class="message-preview">${truncateText(chat.last_message)}</p>
                    </div>
                </div>                  
            </a>
        `;
        chatContainer.appendChild(chatElement);
    });
}

function updateCommunitySection(message){
    const communityConatiner = document.getElementById("community-section");
    communityConatiner.innerHTML = "";

    message.forEach(chat => {
        const chatElement = document.createElement("div");
        chatElement.classList.add("chatSection");

        chatElement.innerHTML = `
            <a href="/chats/${uuid}/ref=${username}/#${chat.full_name}" class="chatting">
                <div class="chat-item">
                    <div class="user-icon">
                        <img src="${chat.image_url}" alt="User">
                    </div>
                    <div class="chat-details">
                        <div class="chat-header">
                            <span class="chat-name">${chat.full_name}</span>
                            ${chat.unread_count > 0 ? `<span class="message-count">${chat.unread_count}</span>` : ""}
                        </div>
                        <p class="message-preview">${truncateText(chat.last_message)}</p>
                    </div>
                </div>                  
            </a>
        `;
        communityConatiner.appendChild(chatElement);
    });
}



function truncateText(text) {
    if (!text) return '';
    return text.length > 30 ? text.slice(0, 30) + '...' : text;
}