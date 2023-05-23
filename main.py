import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import multiprocessing

import logging
log = logging.getLogger(__name__)


class Naver:
    def __init__(self):
        self.driver = None
        self.url = 'https://section.blog.naver.com/Search/Post.naver'
        self.page_num = 10

    def initialize_driver(self):
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--log-level=3')
        options.add_argument('--headless')
        options.add_argument('--disable-logging')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path='chromedriver2', options=options)

    def get_blog_num(self, keyword):
        query = f'?pageNo=1&rangeType=ALL&orderBy=sim&keyword={keyword}'
        uri = self.url + query
        self.driver.get(uri)
        text = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#content > section > div.category_search > div.search_information > span > span > em'))).text
        blog_num = int(text.replace('건', '').replace(',', ''))
        return blog_num

    def get_blogs_url(self, keyword, page):
        data = []

        def _get_blogs_url(url):
            self.driver.get(url)
            elems = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_search_post div.desc [href]')))
            urls = list(set(elem.get_attribute('href') for elem in elems))
            elems = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_search_post div.desc span.title')))
            titles = [i.text for i in elems]

            _data = {urls[idx]: titles[idx] for idx in range(len(titles))}
            data.append(_data)

        urls = [self.url + f'?pageNo={i+1}&rangeType=ALL&orderBy=sim&keyword={keyword}' for i in range(page)]
        for url in urls:
            _get_blogs_url(url)

        return data

    def preprocessing(self, sentence):
        sentence = sentence.strip()
        sentence = re.sub(r"[^0-9가-힣a-zA-Z#:?.!,¿]+", " ", sentence)  # \n도 공백으로 대체해줌
        sentence = sentence.strip()

        return sentence

    def get_blog_content(self, url):
        content = ""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            iframe = soup.find('iframe', id='mainFrame')
            url = f'https://blog.naver.com{iframe["src"]}'
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            contents = soup.find_all('div', {'class': "se-main-container"})

            for p_or_span in contents:
                for text in p_or_span.find_all(['span']):
                    text = text.get_text()
                    if len(text) != 1:
                        content += f' {self.preprocessing(text)}'
        except Exception as e:
            log.info(str(e) + str(": 오류"))
            pass
        return content

    def run(self, keyword, is_close=None):
        num = self.get_blog_num(keyword)
        page = num / 10

        if num % 10 > 1:
            page += 1

        if page > 10:
            page = 10

        data = self.get_blogs_url(keyword, page)
        if is_close:
            self.driver.close()

        return data

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    naver = Naver()
    naver.initialize_driver()
    data = naver.run('광안리')
    print(naver.get_blog_content(list(data[0].keys())[2]))