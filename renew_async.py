import asyncio
import os

import aiofiles
import aiohttp
from dotenv import load_dotenv
from loguru import logger

import common
import notification

load_dotenv()


class Client:

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def login(self, username, password):
        url = 'https://www.hkpl.gov.hk/tc/login.html'
        async with self.session.get(url) as r:
            common.validate_home_resp(r)

        url = 'https://www.hkpl.gov.hk/iw/login.php'
        data = common.prepare_login_data(username, password)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self.session.post(url, data=data, allow_redirects=False, headers=headers) as r:
            common.validate_login_resp(r)

    async def read_checkout(self):
        url = 'https://webcat.hkpl.gov.hk/wicket/bookmarkable/com.vtls.chamo.webapp.component.patron.PatronAccountPage?theme=WEB&locale=zh_TW'
        async with self.session.get(url) as r:
            return await r.text()

    async def renew(self, form_id, action, book_values):
        url = action.replace('../', 'https://webcat.hkpl.gov.hk/wicket/')
        data = common.prepare_renew_data(form_id, book_values)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # ic(dict(self.session.cookies))
        async with self.session.post(url, data=data, allow_redirects=False, headers=headers) as r:
            common.validate_renew_resp(r)


async def main():
    username = os.environ['HKPL_USERNAME']
    password = os.environ['HKPL_PASSWORD']
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        client = Client(session)
        await client.login(username, password)
        text = await client.read_checkout()
        # async with aiofiles.open('temp2.html', 'w', encoding='utf-8') as f:
        #     await f.write(text)
        # async with aiofiles.open('temp2.html', 'r', encoding='utf-8') as f:
        #     text = await f.read()
        page = common.parse_check_out(text)
        logger.info(page)
        if page.valid_records:
            logger.info(f'Renew {"|".join(x.name for x in page.valid_records)}')
            notification.send_renew_action(page.valid_records)
            await client.renew(page.form_id, page.action, [x.value for x in page.valid_records])
        else:
            logger.info('No valid record')
            notification.send_no_action(page.records)


if __name__ == '__main__':
    asyncio.run(main())
