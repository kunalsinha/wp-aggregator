import requests
import random
from bs4 import BeautifulSoup, SoupStrainer
import os
import logging
from .base import WallpaperBase
from utils import download_img


class WallpapersWide(WallpaperBase):

    BASE_URL = 'http://wallpaperswide.com/'
    SEARCH_URL = 'http://wallpaperswide.com/search'
    PAGE_URL = 'http://wallpaperswide.com/search/page/'
    DOWNLOAD_URL = 'http://wallpaperswide.com/download/'

    def __init__(self):
        super().__init__()

    def _extract_num_of_search_pages(self, keyword=None) -> int:
        if not keyword:
            keyword = ''
        params = {'q': keyword}
        resp = requests.get(self.SEARCH_URL, params)
        if resp.status_code != 200:
            raise Exception(f'Response info: {resp.status_code}')
        soup_strainer = SoupStrainer('div', class_='pagination')
        soup = BeautifulSoup(resp.text, 'html.parser',
                             parse_only=soup_strainer)
        page_links = soup.find_all('a')
        if page_links:
            num_pages = int(page_links[-2].string)
        else:
            selected = soup.find(class_='selected')
            if selected:
                num_pages = 1
            else:
                num_pages = 0
        return num_pages

    def _extract_image_urls(self, page_num: int, keyword: str) -> list[str]:
        url = os.path.join(self.PAGE_URL, str(page_num))
        params = {'q': keyword}
        resp = requests.get(url, params=params)
        soup_strainer = SoupStrainer('ul', class_='wallpapers')
        soup = BeautifulSoup(resp.text, 'html.parser',
                             parse_only=soup_strainer)
        thumb_images = soup.find_all('img', class_='thumb_img')
        image_urls = []
        for thumb_image in thumb_images:
            image_urls.append(thumb_image.parent['href'].strip(
                '/').removesuffix('s.html'))
        return image_urls

    def _download_wallpaper(self, image_url: str,
                            aspect_ratio: tuple[int, int] = (2560, 1440)):
        width, height = aspect_ratio
        image_url += '-' + str(width) + 'x' + str(height) + '.jpg'
        url = os.path.join(self.DOWNLOAD_URL, image_url)
        return download_img(url)
