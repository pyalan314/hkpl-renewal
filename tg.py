import os

from dotenv import load_dotenv
# noinspection PyPackageRequirements
from telegram.bot import Bot

load_dotenv()

CHAT_ID = os.environ['HKPL_CHAT_ID']
BOT_TOKEN = os.environ['HKPL_BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)


def send_message(message, parse_mode=None):
    print(parse_mode)
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=parse_mode)
