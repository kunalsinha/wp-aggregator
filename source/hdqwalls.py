import requests
import random
from bs4 import BeautifulSoup, SoupStrainer
import os
import math
import logging
from .base import WallpaperBase
from utils import download_img


class HDQWalls(WallpaperBase):

    BASE_URL = 'http://hdqwalls.com/'
    SEARCH_URL = 'http://hdqwalls.com/search'
    PAGE_URL = 'http://hdqwalls.com/search'
    DOWNLOAD_URL = 'https://images.hdqwalls.com/download/'
    AUTOCOMPLETE_URL = 'https://hdqwalls.com/s_a'

    def __init__(self):
        super().__init__()

    def _determine_exact_keyword(self):
        params = {'term': self.keyword}
        r = requests.get(self.AUTOCOMPLETE_URL, params=params)
        if not r.text:
            return None
        suggestions = r.json()
        if self.keyword.lower() in [suggestion.lower() for suggestion in suggestions]:
            return [self.keyword]
        else:
            return suggestions[:3]

    def _extract_total_pages(self):
        resp = requests.get(self.BASE_URL)
        if resp.status_code != 200:
            return 0
        strainer = SoupStrainer('ul', class_='pagination')
        soup = BeautifulSoup(resp.text, 'html.parser', parse_only=strainer)
        return int(soup.find_all('a')[-2].string)

    def _extract_num_of_search_pages(self) -> int:
        if not self.keyword:
            suggestions = None
        else:
            suggestions = self._determine_exact_keyword()
        logging.info('***Suggestions***')
        logging.info(suggestions)
        num_pages = 0
        if not suggestions:
            num_pages = self._extract_total_pages()
        else:
            for suggestion in suggestions:
                params = {'q': suggestion}
                resp = requests.get(self.SEARCH_URL, params)
                if resp.status_code != 200:
                    raise Exception(f'Response info: {resp.status_code}')
                logging.info(resp.url)
                soup_strainer = SoupStrainer(
                    'div', attrs={'class': 'bg-warning text-center center-block text-warning'})
                soup = BeautifulSoup(resp.text, 'html.parser',
                                     parse_only=soup_strainer)
                pages = math.ceil(int(soup.find('strong').text) / 18)
                if pages > num_pages:
                    self.keyword = suggestion
                    num_pages = pages
        return num_pages

    def _extract_image_urls(self, page_num: int) -> list[str]:
        logging.info('***Details***')
        logging.info(self.PAGE_URL)
        logging.info(page_num)
        logging.info(self.keyword)
        if self.keyword:
            params = {'q': self.keyword, 'page': page_num}
            resp = requests.get(self.PAGE_URL, params=params)
        else:
            default_url = os.path.join(
                'https://hdqwalls.com/latest-wallpapers/page/', str(page_num))
            resp = requests.get(default_url)
        logging.info(resp.url)
        soup_strainer = SoupStrainer(
            'div', class_='wall-resp col-lg-4 col-md-4 col-sm-4 col-xs-6 column_padding')
        soup = BeautifulSoup(resp.text, 'html.parser',
                             parse_only=soup_strainer)
        image_links = soup.find_all(
            'a', class_='caption hidden-md hidden-sm hidden-xs')
        image_urls = []
        for image_link in image_links:
            image_urls.append(image_link['href'].strip('/'))
        return image_urls

    def _download_wallpaper(self, image_url: str,
                            aspect_ratio: tuple[int, int] = (2560, 1440)):
        url = os.path.join(self.BASE_URL, image_url)
        logging.info(url)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        image_url = soup.find('a', class_='btn-default-res')['href']
        image_url = image_url.removesuffix('.jpg')
        width, height = aspect_ratio
        resolution = '-' + str(width) + 'x' + str(height) + '.jpg'
        image_url += resolution
        image_url = image_url.replace('wallpapers', 'download')
        logging.info(f'Image URL: {image_url}')
        return download_img(image_url)
