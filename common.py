from collections import namedtuple
from datetime import datetime, date

from bs4 import BeautifulSoup

Record = namedtuple('Record', ['name', 'due_date', 'times', 'value'])
Page = namedtuple('Page', ['form_id', 'action', 'records', 'valid_records'])


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
            times=cols[5].text.strip().split(' ')[0]
        )

    records = [parse_row(x) for x in rows if len(x.find_all('td')) > 1]
    # TODO handle expired case
    valid_records = [x for x in records if x.value and x.due_date == date.today()]
    return Page(
        form_id=form['id'],
        action=form['action'],
        records=records,
        valid_records=valid_records,
    )
