import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json


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


def lambda_handler(event, context):
    keyword = event["queryStringParameters"].get('keyword')
    start_page = event["queryStringParameters"].get('start_page')
    end_page = event["queryStringParameters"].get('end_page')
    start_date = event["queryStringParameters"].get('start_date')
    end_date = event["queryStringParameters"].get('end_date')

    if not (keyword and start_page and end_page and start_date and end_date):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Not exist required query params'})
        }

    start = time.time()
    naver = NaverBlog(keyword=keyword, start_page=int(start_page), end_page=int(end_page), start_date=start_date,
                      end_date=end_date)
    data = naver.run()

    result = {
        'resultCode': 200,
        'resultMessage': None,
        'result': {'time': time.time() - start, 'data': data}
    }

    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False)
    }
