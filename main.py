import os
from collections import namedtuple
from datetime import datetime

import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from icecream import ic

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

Record = namedtuple('Record', ['name', 'due_date', 'times', 'value'])
Page = namedtuple('Page', ['form_id', 'action', 'records'])


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False

    def login(self, username, password):
        url = 'https://www.hkpl.gov.hk/tc/login.html'
        r = self.session.get(url)

        url = 'https://www.hkpl.gov.hk/iw/login.php'
        data = dict(
            USER=username,
            PASSWORD=password,
            traget='/auth/login?target=/',
            lang='tc',
            chamo='',
            entryPage='/tc/login.php',
            queryString='',
            pwExpiryAction='',
            noPwExpiryAlert='',
        )
        data = f'USER={username}&PASSWORD={password}&target=%2Fauth%2Flogin%3Ftarget%3D%2F&lang=tc&chamo=&entryPage=%2Ftc%2Flogin.php&queryString=&pwExpiryAction=&noPwExpiryAlert='
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        r = self.session.post(url, data=data, allow_redirects=False, headers=headers)
        # ic(dict(r.request.headers))
        # ic(r.request.body)
        # ic(r.url)
        # ic(r.status_code)
        # ic(dict(r.headers))
        ic(dict(self.session.cookies))

        # self.session.get('https://www.hkpl.gov.hk/auth/login?target=/', verify=False, allow_redirects=False)
        #
        # self.session.get('https://www.hkpl.gov.hk/', verify=False)

    def read_checkout(self):
        # self.session.get('https://www.hkpl.gov.hk/tc/index.html', verify=False)
        r = self.session.get('https://webcat.hkpl.gov.hk/wicket/bookmarkable/com.vtls.chamo.webapp.component.patron.PatronAccountPage?theme=WEB&locale=zh_TW')
        return r.text

    def renew(self, form_id, action, book_value):
        url = action.replace('../', 'https://webcat.hkpl.gov.hk/wicket/')
        data = {
            f'{form_id}_hf_0': '',
            'renewalCheckboxGroup:checkoutsTable:topToolbars:toolbars:1:span:pageSize:sizeChoice': 0,
            'renewalCheckboxGroup:checkoutsTable:bottomToolbars:toolbars:2:span:pageSize:sizeChoice': 0,
            'renewalCheckboxGroup': book_value,
        }
        data = f'{form_id}_hf_0=&renewalCheckboxGroup%3AcheckoutsTable%3AtopToolbars%3Atoolbars%3A1%3Aspan%3ApageSize%3AsizeChoice=0&renewalCheckboxGroup%3AcheckoutsTable%3AbottomToolbars%3Atoolbars%3A2%3Aspan%3ApageSize%3AsizeChoice=0&renewalCheckboxGroup={book_value}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        ic(dict(self.session.cookies))
        r = self.session.post(url, data=data, allow_redirects=False, headers=headers)
        ic(dict(r.request.headers))
        ic(r.request.body)
        ic(r.status_code)
        ic(r.url)
        ic(dict(r.headers))


def analyze(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', {'id': 'checkout'})
    form = table.find_parent('form')
    t_body = table.find('tbody')
    rows = t_body.find_all('tr')

    def parse_row(row):
        cols = row.find_all('td')
        ic(cols)
        renew_input = cols[0].find('input')
        if renew_input:
            value = renew_input['value']
        else:
            value = None
        return Record(
            name=cols[1].text.strip(),
            due_date=datetime.strptime(cols[4].text.strip(), '%Y-%m-%d').date(),
            value=value,
            times=cols[5].text.strip().split(' ')[0]
        )

    records = [parse_row(x) for x in rows if len(x.find_all('td')) > 1]
    return Page(
        form_id=form['id'],
        action=form['action'],
        records=records,
    )


def main():
    client = Client()
    username = os.environ['HKPL_USERNAME']
    password = os.environ['HKPL_PASSWORD']
    client.login(username, password)
    text = client.read_checkout()
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(text)
    with open('temp.html', 'r', encoding='utf-8') as f:
        text = f.read()
    page = analyze(text)
    ic(page)
    valid_records = [x for x in page.records if x.value]
    if valid_records:
        client.renew(page.form_id, page.action, valid_records[0].value)


if __name__ == '__main__':
    main()
