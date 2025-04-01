$(document).ready(function() {
    let uuid = document.getElementById('uid').innerText;
    let username = document.getElementById('username').innerText;
    console.log(uuid);
    console.log(username);
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
                <a href="" class="chatting">
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
                </a>
            `;
            const createElement1 = document.createElement("hr");
            chatContainer.append(chatElement);
            chatContainer.append(createElement1);
        });
    }

    fetchRecentChatDetails(uuid, username);

    setInterval(function(){
        fetchRecentChatDetails(uuid, username)
    }, 10000);

});
