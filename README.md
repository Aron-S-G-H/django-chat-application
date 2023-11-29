# Django Chat Application
Async Chat application with Django Channels, Websocket and JS (Ajax) 

## Features
- Authentication - like always :)
  - login
  - register (OTP)
  - Forgot password
  - Authenticate with google account
- Notification system for new messages
- Video call
- Send Image (base64 encode)
- Clear history (only for room creator)
- Delete room (only for room creator)
- Change room icon
- Members list
- Celery (RabbitMQ as broker & Redis as backend)

### ToDo 
- Add Docker

---
### ⚠️ Video call doesn't support Microsoft Edge browser
---

### Usage :
-  For sending a one-time password via email, you should set your email and your email host password in 'EMAIL_HOST_USER' and 'EMAIL_HOST_PASSWORD' in 'settings.py' . Otherwise, sending the one-time password for user registration won't work .
```bash
git clone https://github.com/Aron-S-G-H/django-chat-application.git
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver # and see in localhost:8000
# In another terminal, enter the following command to run celery
celery -A ChatApp worker -l info
# you also need RabbitMQ as broker and Redis as backend
```
### Result
<p align="center">
  <img src="https://github.com/Aron-S-G-H/django-chat-application/blob/main/assets/result.png">
</p>

---
#### any contributions are welcome
