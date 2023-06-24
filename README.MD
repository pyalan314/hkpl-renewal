HKPL Renewal
========
Auto-renewal helper for HKPL

Dependencies
--------
Install dependencies by  
`pip install -r requirements.txt`

Configuration
--------
Create a .env file in the same path with the following entries
```dotenv
HKPL_USERNAME=YOUR_USERNAME_IN_HKPL
HKPL_PASSWORD=YOUR_PASSWORD_IN_HKPL
HKPL_CHAT_ID=-TELEGRAM_CHAT_ID
HKPL_BOT_TOKEN=TELEGRAM_CHAT_BOT_TOKEN
```

HKPL_CHAT_ID and HKPL_BOT_TOKEN are optional for notification. If omitted, the program will work without sending notification to user. 

Run
--------
`python main.py`
