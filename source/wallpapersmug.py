import os
import requests
from bs4 import BeautifulSoup, SoupStrainer
import random
import logging
from .base import WallpaperBase
from utils import download_img


class WallpapersMug(WallpaperBase):

    BASE_URL = 'http://wallpapersmug.com/'
    SEARCH_URL = 'https://wallpapersmug.com/w/wallpaper'
    PAGE_URL = 'https://wallpapersmug.com/w/wallpaper/latest/page/'
    DOWNLOAD_URL = 'https://wallpapersmug.com/w/download/'

    def __init__(self):
        super().__init__()

    def _extract_num_of_search_pages(self, keyword):
        if not keyword:
            keyword = ''
        params = {'search': keyword}
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(self.SEARCH_URL, params=params, headers=headers)
        if resp.status_code != 200:
            raise Exception(f'Response info: {resp.status_code}')
        soup_strainer = SoupStrainer('nav', class_='pagy-nav pagination')
        soup = BeautifulSoup(resp.text, 'html.parser',
                             parse_only=soup_strainer)
        try:
            return int(soup.nav.find_all('span')[-2].string)
        except Exception:
            return 0

    def _extract_image_urls(self, page_num: int, keyword: str) -> list[str]:
        url = os.path.join(self.PAGE_URL, str(page_num))
        headers = {'User-Agent': 'Mozilla/5.0'}
        params = {'search': keyword}
        resp = requests.get(url, params=params, headers=headers)
        logging.info(f'URL: {resp.url}')
        soup_strainer = SoupStrainer('div', class_='item_img')
        soup = BeautifulSoup(resp.text, 'html.parser',
                             parse_only=soup_strainer)
        thumb_images = soup.find_all('a')
        image_urls = []
        for thumb_image in thumb_images:
            image_urls.append(thumb_image['href'].strip('/'))
        return image_urls

    def _download_wallpaper(self, image_url: str,
                            aspect_ratio: tuple[int, int] = (2560, 1440)):
        width, height = aspect_ratio
        resolution = str(width) + 'x' + str(height)
        url = os.path.join(self.DOWNLOAD_URL, resolution,
                           image_url.rsplit('/')[-1])
        logging.info(url)
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers)
        soup_strainer = SoupStrainer('a', class_='btn btn-primary')
        soup = BeautifulSoup(resp.text, 'html.parser',
                             parse_only=soup_strainer)
        image_url = soup.a['href']
        return download_img(image_url)
