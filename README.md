# Chatter: ChatBox - Your Ultimate Communication Hub

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-blue?style=flat-square&logo=github)](https://github.com/Devpancholi04/Chatter)
[![Default Branch](https://img.shields.io/badge/Branch-main-green?style=flat-square)](https://github.com/Devpancholi04/Chatter)

## Project Description

Chatter, also known as ChatBox, is a versatile chatting application built with Django, Channels, Celery, and Redis. It offers real-time messaging, group chats, community forums, and an AI-powered chat assistant, aiming to be a comprehensive communication solution.

## Features and Functionality

*   **User Authentication and Management:**
    *   Registration and Login: Secure user account creation and authentication.
    *   Account Activation: Email verification via tokens (`email_token`) sent using Celery tasks (`base.emails.account_activation_email`).
    *   Password Reset: Password reset functionality with email confirmation (`forget_token`).
    *   Two-Factor Authentication: Optional OTP-based two-factor authentication for enhanced security.
    *   Profile Management: Users can update personal details, address information, and profile photos.
    *   Account Deactivation: Users can deactivate their accounts after email and password verification.
    *   User Roles: Implements user roles (ADMIN, EMPLOYEE, USER) with corresponding permissions.
    *   Friend Request: Send and accept friends request.
*   **Real-time Chat:**
    *   One-to-One Chat: Real-time direct messaging using Django Channels and WebSockets (`chat.consumers.ChatConsumer`).
    *   Group Chat: Create and manage groups with multiple members (`chat.models.Group`, `chat.consumers.GroupConsumer`).
    *   Message Persistence: Messages are temporarily stored in Redis cache and periodically flushed to the database using Celery tasks (`chat.tasks.flush_all_chats_buffer_to_db`).
    *   Message Status: Indicates message delivery and read status.
    *   Recent Chat List: Display recently chatted users and groups at the left side of chat page.
*   **Community Forums:**
    *   Community Creation: Users can create and join communities (`community.models.Community`).
    *   Community Messaging: Real-time messaging within communities (`community.consumers.CommunityConsumer`).
    *   Community Member Management: Add and remove members from communities.
*   **AI Chat Assistant:**
    *   AI-Powered Chat: Interact with an AI assistant powered by OpenAI models (`ai_chat/consumers.py`).
    *   Streaming Responses: AI responses are streamed to the user in real-time.
    *   Predefined responses - Some message cached and given the predefined responses.

## Technology Stack

*   **Backend:**
    *   Django 5.1.3: Web framework
    *   Django Channels: WebSocket support
    *   Celery: Asynchronous task queue
    *   Redis: Caching and message brokering
    *   MySQL: Database
    *   OpenAI API: For AI Chat Assistant
    *   djangorestframework: Used to handle the REST API's
*   **Frontend:**
    *   HTML, CSS, JavaScript
    *   jQuery
    *   Bootstrap
    *   Font Awesome

## Prerequisites

Before you begin, ensure you have met the following requirements:

*   Python 3.8+ installed
*   pip package installer
*   MySQL database
*   Redis server
*   Celery
*   Node.js and npm (for frontend dependencies)

## Installation Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Devpancholi04/Chatter.git
    cd Chatter
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    *   On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure the database:**

    *   Update the database settings in `chatter/settings.py` with your MySQL credentials:

        ```python
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'chatter_app',
                'USER' : 'root',
                'PASSWORD' : 'YOUR_PASSWORD',
                "HOST" : 'localhost',
                "PORT" : '3306'
            }
        }
        ```

6.  **Apply migrations:**

    ```bash
    python manage.py migrate
    ```

7.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

8.  **Configure Redis and Celery:**

    *   Ensure Redis server is running.

    *   Celery settings are configured in `chatter/settings.py`:

        ```python
        CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
        CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"
        ```

9.  **Set up static files:**

    ```bash
    python manage.py collectstatic
    ```

10. **Start the development server:**

    ```bash
    python manage.py runserver
    ```

11. **Run Celery worker and beat:**

    Open two new terminal windows and activate the virtual environment in each.

    *   In the first terminal, start the Celery worker:

        ```bash
        celery -A chatter worker -l info
        ```

    *   In the second terminal, start Celery beat:

        ```bash
        celery -A chatter beat -l info
        ```

12. **Daphne (ASGI) Server**

    ```bash
    daphne chatter.asgi:application --port 8000 --bind 0.0.0.0
    ```

## Usage Guide

1.  **Access the application:**

    Open your web browser and navigate to `http://127.0.0.1:8000/`.

2.  **Register or log in:**

    Create a new user account or log in with an existing account.

3.  **Explore the features:**

    *   **Chat:** Start direct chats with other users.
    *   **Groups:** Create or join groups for group messaging.
    *   **Community:** Explore and join communities.
    *   **AI Chat:** Interact with the AI chat assistant.
    *   **Profile:** Edit your profile details and settings.

## API Documentation

The application provides REST APIs for various functionalities. Here are some of the key endpoints:

*   **User Management:**
    *   `/accounts/register/`: User registration.
    *   `/accounts/login/`: User login.
    *   `/accounts/ref=<str:user_id>/activate/tk=<str:email_token>/`: Account activation.
    *   `/accounts/login/resetpassword/`: Reset password request.
    *   `/home/api/update/personal/details/<str:uid>/`: Update personal details.
    *   `/home/api/update/address/details/<str:uid>/`: Update address details.
    *   `/home/api/update/profile-photos/<str:uid>/`: Update profile picture.

*   **Chat API:**
    *   `/chats/<str:uid>/ref=<str:username>/`: Access chat page.
    *   `/chats/api/load/one-2-one/chats/history/sid=<str:uid>/sref=<str:username>/rid=<str:rec_uid>/rref=<str:rec_username>/`: Load one-to-one chat history.
    *   `/chats/api/load/group/chats/history/gid=<str:group_id>/ref=<str:uid>/refu=<str:username>/`: Load group chat history.
    *   `/chats/api/recent-messages/<str:uid>/ref=<str:username>/`: Get recent messages.
    *   `/chats/api/mark-as-read/sid=<str:uid>/sref=<str:username>/rid=<str:rec_uid>/rref=<str:rec_username>/`: Mark messages as read.

*   **Community API:**
    *   `/community/chats/<str:uid>/ref=<str:username>/`: Access community page.
    *   `/community/api/recent-messages/<str:uid>/ref=<str:username>/`: Get recent community messages.
    *   `/community/api/load/message/history/cid=<str:cid>/ref=<str:uid>/refu=<str:username>/`: Load community message history.
    *   `/community/api/mark-as-read/messages/cid=<str:cid>/uid=<str:uid>/username=<str:username>/`: Mark community messages as read.
    *   `/community/api/add-user/community/<str:username>/<str:community_id>/`: Join a community.

*   **Search API:**
    *   `/home/api/search/user/?q=<search_query>`: Searches for user profile based on search query.

## Contributing Guidelines

Contributions are welcome! To contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes.
4.  Test your changes thoroughly.
5.  Submit a pull request with a clear description of your changes.

## License Information

This project has no specified license. All rights are reserved by the developers.

## Contact/Support Information

For questions, bug reports, or feature requests, please contact:

*   Dev Pancholi: [https://github.com/Devpancholi04](https://github.com/Devpancholi04)