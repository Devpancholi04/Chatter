$(document).ready(function () {
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;


})


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
        chatContainer.prepend(starthr);
        chatContainer.prepend(chatElement);    
    });
}

function fetchRecentCommunitiesDetails(uid, username){
    
}