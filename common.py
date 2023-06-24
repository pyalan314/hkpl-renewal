from datetime import datetime, date
from typing import NamedTuple
from typing import Union

import requests
from aiohttp import ClientResponse
from bs4 import BeautifulSoup
from loguru import logger


class Record(NamedTuple):
    name: str
    due_date: date
    times: int
    value: str

    def is_valid(self):
        return self.value and self.due_date == date.today() and self.times <= 5

    def short(self):
        return f'{self.due_date.strftime("%m/%d")} | {self.name:.15}'


class Page(NamedTuple):
    form_id: str
    action: str
    records: list[Record]

    @property
    def valid_records(self) -> list[Record]:
        # TODO handle expired case
        return [x for x in self.records if x.is_valid()]


def prepare_login_data(username, password):
    assert username
    assert password
    data = {
        'USER': username,
        'PASSWORD': password,
        'target': '/auth/login?target=/',
        'lang': 'tc',
        'chamo': '',
        'entryPage': '/tc/login.php',
        'queryString': '',
        'pwExpiryAction': '',
        'noPwExpiryAlert': ''
    }
    return '&'.join(f'{k}={v}' for k, v in data.items())


def prepare_renew_data(form_id, book_values):
    assert form_id
    assert book_values
    data = {
        f'{form_id}_hf_0': '',
        'renewalCheckboxGroup:checkoutsTable:topToolbars:toolbars:1:span:pageSize:sizeChoice': 0,
        'renewalCheckboxGroup:checkoutsTable:bottomToolbars:toolbars:2:span:pageSize:sizeChoice': 0,
    }
    part_1 = '&'.join(f'{k}={v}' for k, v in data.items())
    part_2 = '&'.join(f'renewalCheckboxGroup={value}' for value in book_values)
    return '&'.join((part_1, part_2))


def parse_check_out(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', {'id': 'checkout'})
    form = table.find_parent('form')
    t_body = table.find('tbody')
    rows = t_body.find_all('tr')

    def parse_row(row):
        cols = row.find_all('td')
        renew_input = cols[0].find('input')
        if renew_input:
            value = renew_input['value']
        else:
            value = None
        return Record(
            name=cols[1].text.strip()[:20],
            due_date=datetime.strptime(cols[4].text.strip(), '%Y-%m-%d').date(),
            value=value,
            times=int(cols[5].text.strip().split(' ')[0])
        )

    records = [parse_row(x) for x in rows if len(x.find_all('td')) > 1]
    return Page(
        form_id=form['id'],
        action=form['action'],
        records=records,
    )


def handle_aiohttp_response(r: Union[requests.Response, ClientResponse]):
    if isinstance(r, ClientResponse):
        r.status_code = r.status


def validate_home_resp(r: Union[requests.Response, ClientResponse]):
    handle_aiohttp_response(r)
    if r.status_code != 200:
        raise ValueError(f'home status == {r.status_code}')


def validate_login_resp(r: Union[requests.Response, ClientResponse]):
    handle_aiohttp_response(r)
    # ic(dict(r.request.headers))
    # ic(r.request.body)
    # ic(r.url)
    # ic(r.status_code)
    # ic(dict(r.headers))
    logger.debug(dict(r.cookies))
    if r.status_code != 302:
        raise ValueError(f'login status == {r.status_code}')
    if 'SMSESSION' not in r.cookies:
        raise ValueError(f'No SMSESSION in login cookies')


def validate_renew_resp(r: Union[requests.Response, ClientResponse]):
    handle_aiohttp_response(r)
    if isinstance(r, requests.Response):
        logger.debug(r.request.body)
    logger.debug(r.status_code)
    logger.debug(r.headers)
    if r.status_code != 302:
        raise ValueError(f'renew status == {r.status_code}')
