from dataclasses import dataclass
from typing import Union

from fake_useragent import UserAgent
from requests_html import HTML
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


def get_user_agent() -> UserAgent:
    return UserAgent(verify_ssl=False).random


@dataclass
class Scraper:
    url: str = ''
    endless_scroll: bool = False
    endless_scroll_time: int = 5
    driver: Union[WebDriver, None] = None

    def get_driver(self):
        if not self.driver:
            options = webdriver.ChromeOptions()
            user_agent = get_user_agent()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument(f'user-agent={user_agent}')
            driver = webdriver.Chrome(
                executable_path='/Users/rafaelzaripov/Downloads/chromedriver',
                options=options
                )
            self.driver = driver
        return self.driver

    def perform_endless_scroll(self, driver=None):
        """функция для прокрутки сайта"""

        if not driver:
            return
        
        if self.endless_scroll:
            current_height = driver.execute_script('return document.body.scrollHeight')

            while True:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                driver.implicitly_wait(self.endless_scroll_time)
                iter_hight = driver.execute_script('return document.body.scrollHeight')

                if current_height == iter_hight:
                    break

                current_height = iter_hight
            
            with open('index.html', 'w') as f:
                f.write(driver.page_source)
        return

    def get_page_source(self):
        """Получаем данные со страницы"""
        driver = self.get_driver()
        try:
            driver.get(self.url)
            self.perform_endless_scroll(driver)
            return driver.page_source
        except Exception as err:
            print(err)
        finally:
            driver.close()


@dataclass
class HtmlParser:
    
    urls_patterns: tuple = ()
    html_string: Union[str, None] = None
    url_prefix: str = 'https://zakupki.gov.ru/'

    def __extract_links(self) -> list:
        """Вытаскиваем url на страницы с каждой закупкой из результата поиска"""
        if not self.html_string:
            raise AttributeError("Empty html_string")

        html_obj = HTML(html=self.html_string)
        links_set = html_obj.absolute_links

        result_links = []

        for link in links_set:
            for template in self.urls_patterns:
                if link.find(template) > -1:
                    result_links.append(link.replace('https://example.org/', self.url_prefix))

        return result_links


    def create_data(self) -> dict:
        """Данные после парсинга каждой страницы. С пасингом пока проблемы.
        Не понимаю как добраться до данных"""

        return {
            "data": {
                "purchase_number": 331011102021,
                "start_price": 123222,
                "date_start": "11.10.2022",
                "last_update": "13.10.2022",
                "documet": "Some text" 
                }
            }


# url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=Дате+размещения&pageNumber=1&sortDirection=false&recordsPerPage=_20&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&ca=on&pc=on&pa=on&currencyIdGeneral=-1'
# url = 'https://zakupki.gov.ru//epz/order/notice/notice223/documents.html?noticeInfoId=14487011'
# driver = Scraper(url=url, endless_scroll=True)

# html_string = driver.get_page_source()


# html_obj = HTML(html=html_string)

# element = html_obj.html

# print(re.findall(r'([№]{1}[\W][0-9]{4,12})',element))

# print(re.findall(r'\d*[ ]*\d*[ ]*\d*[ ]*,\d{2}[ ]₽',element))

# print(re.findall(r'((<div class="data-block__title">Размещено</div>)[\n]*[\t]*(<div class="data-block__value">)[\n][\t]*\d{2}.\d{2}.\d{4}</div>)', element))
