import os

from dotenv import load_dotenv
from notifiers import get_notifier

from common import Record

load_dotenv()

CHAT_ID = os.environ['HKPL_CHAT_ID']
BOT_TOKEN = os.environ['HKPL_BOT_TOKEN']
service = get_notifier('telegram')


def notify(msg, formatted=False):
    if formatted:
        msg = f"`{msg}`"
    response = service.notify(
        message=msg,
        chat_id=CHAT_ID,
        token=BOT_TOKEN,
        parse_mode='markdown'
    )


def send_no_action(records: list[Record]):
    msg = [
        'No due items',
        '-' * 10,
        *(x.short() for x in records),
    ]
    notify('\n'.join(msg))


def send_renew_action(records: list[Record]):
    msg = [
        'Renew items',
        '-' * 10,
        *(x.short() for x in records),
    ]
    notify('\n'.join(msg))


def send_fail(e):
    msg = [
        'Unhandled error. Program will be closed',
        '-' * 10,
        str(e)
    ]
    notify('\n'.join(msg))

