import asyncio
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from selenium import webdriver

options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--log-level=3')
options.add_argument('--headless')
options.add_argument('--disable-logging')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')


url = 'https://section.blog.naver.com/Search/Post.naver'
keyword = '광안리'
page = 20
urls = [url + f'?pageNo={i + 1}&rangeType=ALL&orderBy=sim&keyword={keyword}' for i in range(page)]

data = []


async def scrape(url, *, loop):
    await loop.run_in_executor(None, scraper, url)


def scraper(url):
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)
    driver.get(url)

    # elems = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_search_post div.desc [href]')))
    # urls = list(set(elem.get_attribute('href') for elem in elems))
    elems = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_search_post div.desc span.title')))
    titles = [i.text for i in elems]

    # _data = {urls[idx]: titles[idx] for idx in range(len(titles))}

    data.extend(titles)
    driver.close()



start = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*[scrape(url, loop=loop) for url in urls ]))
print(data)
print(time.time() - start)