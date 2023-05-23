import asyncio
import time
from concurrent.futures.thread import ThreadPoolExecutor
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
page = 30
urls = [url + f'?pageNo={i + 1}&rangeType=ALL&orderBy=sim&keyword={keyword}' for i in range(page)]

data = []

executor = ThreadPoolExecutor(page)


def scrape(url, *, loop):
    loop.run_in_executor(executor, scraper, url)


def scraper(url):
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)
    driver.get(url)

    elems = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_search_post div.desc [href]')))
    urls = list(set(elem.get_attribute('href') for elem in elems))
    elems = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_search_post div.desc span.title')))
    titles = [i.text for i in elems]

    _data = {urls[idx]: titles[idx] for idx in range(len(titles))}

    # Kafka producer
    pass


loop = asyncio.get_event_loop()

for url in urls:
    scrape(url, loop=loop)

start = time.time()
loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))
print(time.time() - start)
