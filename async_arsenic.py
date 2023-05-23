import asyncio
import time

from arsenic import get_session
from arsenic.browsers import Chrome
from arsenic.services import Chromedriver

a = []


async def run(url):
    driver = Chromedriver(binary='./chromedriver')
    browser = Chrome(**{"goog:chromeOptions":{
        'args': ['--headless', '--disable-gpu']
    }})

    async with get_session(driver, browser) as session:
        await session.get(url)
        await session.wait_for_element(5, 'div.list_search_post div.desc span.title')
        elems = await session.get_elements('div.list_search_post div.desc span.title')
        titles = [await i.get_text() for i in elems]
        a.extend(titles)


async def loops():
    url = 'https://section.blog.naver.com/Search/Post.naver'
    keyword = '광안리'
    page = 100
    urls = [url + f'?pageNo={i + 1}&rangeType=ALL&orderBy=sim&keyword={keyword}' for i in range(page)]
    await asyncio.gather(*[run(url=url) for url in urls])


start = time.time()
asyncio.run(loops())
print(time.time() - start)
print(a)
