const avatarUpload = document.getElementById("avatarUpload");
const avatarPreview = document.getElementById("avatarPreview");


const tabButtons = document.querySelectorAll(".tab");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(btn => {
    btn.addEventListener("click", function () {
        const tabId = this.getAttribute("data-tab");

        tabContents.forEach(tab => tab.style.display = "none");
        document.getElementById(tabId).style.display = "block";

        tabButtons.forEach(b => b.classList.remove("active"));
        this.classList.add("active");
    });
});

function showSetting(option) {
    const content = document.getElementById("setting-content");

    if (option === 'deactivate') {
        content.innerHTML = `
        <div class="setting-box">
            <h4 class="setting-title">Deactivate Account</h4>
            <form action="" method="get">
                <div class="form-group">
                    <label>Email ID:</label>
                    <input type="email" class="form-input" placeholder="Enter your email">
                </div>
                <div class="form-group">
                    <label>Mobile No:</label>
                    <input type="text" class="form-input" placeholder="Enter your mobile">
                </div>
                <button type="submit" class="btn-primary" onclick="alert('Deactivation request sent')">Proceed</button>
            </form>
        </div>
      `;
    } else if (option === 'password') {
        content.innerHTML = `
        <div class="setting-box">
            <h4 class="setting-title">Change Password</h4>
            <form action="" method="get">

                <div class="form-group">
                    <label>Old Password:</label>
                    <input type="password" class="form-input">
                </div>
                <div class="form-group">
                    <label>New Password:</label>
                    <input type="password" class="form-input">
                </div>
                <div class="form-group">
                    <label>Confirm Password:</label>
                    <input type="password" class="form-input">
                </div>

                <button type="submit" class="btn-primary" onclick="alert('Password changed successfully')">Update</button>
            </form>
        </div>
      `;
    } else if (option === '2fa') {
        content.innerHTML = `
        <div class="setting-box">
            <h4 class="setting-title">Two-Factor Authentication</h4>
            <form action="" method="post">
          
                <label class="switch">
                    <input type="checkbox">
                    <span class="slider round"></span>
                </label>
                <p id="2fa-status">Two Factor Authentication is <strong>Disabled</strong></p>

            </form>
        </div>
      `;
    }
}

// function toggle2FA(checkbox) {
//     const statusText = document.getElementById("2fa-status");
//     if (checkbox.checked) {
//         alert('Two Factor Authentication Enabled');
//         statusText.innerHTML = 'Two factor Authentication is <strong>Enabled</strong>';
//     } else {
//         alert('Two Factor Authentication Disabled');
//         statusText.innerHTML = 'Two Factor Authentication is <strong>Disabled</strong>';
//     }
// }