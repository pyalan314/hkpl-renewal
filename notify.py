import tg
from common import Record


def send_no_action(records: list[Record]):
    msg = [
        'No due items',
        '-' * 10,
        *(f'{x.due_date} | {x.name}' for x in records)
    ]
    tg.send_message('\n'.join(msg))


def send_renew_action(records: list[Record]):
    msg = [
        'Renew items',
        '-' * 10,
        *(f'{x.due_date} | {x.name}' for x in records)
    ]
    tg.send_message('\n'.join(msg))


def send_fail(e):
    msg = [
        'Unhandled error. Program will be closed',
        '-' * 10,
        str(e)
    ]
    tg.send_message('\n'.join(msg))
