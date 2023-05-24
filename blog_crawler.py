import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import requests


class NaverBlog:
    def __init__(self, keyword, start_page, end_page, start_date, end_date):
        self.keyword = keyword
        self.start_page = start_page
        self.end_page = end_page
        self.start_date = start_date
        self.end_date = end_date

        self.data = {}

    def parsing(self, data):
        """
        Html Parser
        :param data:
        :return: [(title, url, description, date), (title, url, description, date), ..]
        """
        soup = BeautifulSoup(data.replace("\\", ""), "html.parser")
        title_and_url_elems = soup.find_all("a", {"class": "api_txt_lines"})
        desc_elems = soup.find_all("div", {"class": "api_txt_lines"})
        date_elems = soup.find_all("span", {"class": "sub_time"})

        return [(title_and_url_elems[i].text, title_and_url_elems[i]['href'], desc_elems[i].text, date_elems[i].text)
                for i in range(len(title_and_url_elems))]

    def async_requests(self, url_lst):
        """
        비동기 http 요청
        :param url_lst:
        :return: {'https://naver.com': {'title': 제목, 'desc': 내용, 'date': 날짜}, 'https://naver.com': {'title': 제목, 'de' ..}
        """

        async def get_html(_url):
            async with aiohttp.ClientSession() as session:
                async with session.get(_url, ) as response:
                    text = await response.text()
                    for title, url, desc, date in self.parsing(text):
                        self.data[url] = {'title': title, 'desc': desc, 'date': date}

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            asyncio.gather(*(get_html(url_lst[i]) for i in range(len(url_lst))))
        )

    def get_total_count(self, data):
        """
        해당 기간 총 블로그 개수 조회
        :param data: 전체 html text  (res.text)
        :return:
        """
        data = data.replace('\\', '')
        start_index = data.find('"total":"') + 9
        end_index = data[start_index:start_index + 50].find('"') + start_index
        cnt = int(data[start_index:end_index])

        return cnt

    def sync_request(self):
        """
        동기 http 요청
        :return: 블로그 개수
        """
        url = f'https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&query={self.keyword}&rev=44&start={int(self.start_page) * 30}&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so:dd,p:from{self.end_date}to{self.start_date}&nlu_query={{"r_category":"29+27"}}&dkey=0&source_query=&nx_search_query={self.keyword}&spq=0&_callback=viewMoreContents'
        res = requests.get(url)
        cnt = self.get_total_count(res.text)
        return cnt

    def run(self):
        """
        블로그 정보 조회 실행 함수
        :return:
        """
        urls = [
            f'https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&query={self.keyword}&rev=44&start={i * 30}&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so:dd,p:from{self.end_date}to{self.start_date}&nlu_query={{"r_category":"29+27"}}&dkey=0&source_query=&nx_search_query={self.keyword}&spq=0&_callback=viewMoreContents'
            for i in range(self.start_page, self.end_page)
        ]
        self.async_requests(urls)
        return self.data


if __name__ == '__main__':
    naver = NaverBlog(keyword='광안리', start_page=1, end_page=10, start_date=20230520, end_date=20230521)
    data = naver.run()
