import os
import time

import requests
import urllib3
from dotenv import load_dotenv
from loguru import logger

import common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


class Client:

    def __init__(self, session: requests.Session):
        self.session = session

    def login(self, username, password):
        url = 'https://www.hkpl.gov.hk/tc/login.html'
        r = self.session.get(url)
        assert r.status_code == 200

        url = 'https://www.hkpl.gov.hk/iw/login.php'
        data = common.prepare_login_data(username, password)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = self.session.post(url, data=data, allow_redirects=False, headers=headers)
        # ic(dict(r.request.headers))
        # ic(r.request.body)
        # ic(r.url)
        # ic(r.status_code)
        # ic(dict(r.headers))
        logger.debug(dict(self.session.cookies))
        assert r.status_code == 302
        assert 'SMSESSION' in r.cookies

    def read_checkout(self):
        r = self.session.get('https://webcat.hkpl.gov.hk/wicket/bookmarkable/com.vtls.chamo.webapp.component.patron.PatronAccountPage?theme=WEB&locale=zh_TW')
        return r.text

    def renew(self, form_id, action, book_values):
        url = action.replace('../', 'https://webcat.hkpl.gov.hk/wicket/')
        data = common.prepare_renew_data(form_id, book_values)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # ic(dict(self.session.cookies))
        r = self.session.post(url, data=data, allow_redirects=False, headers=headers)
        logger.debug(r.request.body)
        logger.debug(r.status_code)
        logger.debug(r.headers)
        assert r.status_code == 302


def main():
    username = os.environ['HKPL_USERNAME']
    password = os.environ['HKPL_PASSWORD']
    while True:
        session = requests.Session()
        session.verify = False
        client = Client(session)
        client.login(username, password)
        text = client.read_checkout()
        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(text)
        with open('temp.html', 'r', encoding='utf-8') as f:
            text = f.read()
        page = common.parse_check_out(text)
        logger.info(page)
        if page.valid_records:
            logger.info(f'Renew {"|".join(x.name for x in page.valid_records)}')
            client.renew(page.form_id, page.action, [x.value for x in page.valid_records])
        else:
            logger.info('No valid record')
        time.sleep(60)


if __name__ == '__main__':
    main()
