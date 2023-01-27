import requests
import random
from bs4 import BeautifulSoup, SoupStrainer
import os
import logging
from utils import download_img

BASE_URL = 'http://wallpaperswide.com/'
SEARCH_URL = 'http://wallpaperswide.com/search'
PAGE_URL = 'http://wallpaperswide.com/search/page/'
DOWNLOAD_URL = 'http://wallpaperswide.com/download/'


def _extract_num_of_search_pages(keyword=None) -> int:
    if not keyword:
        keyword = ''
    params = {'q': keyword}
    resp = requests.get(SEARCH_URL, params)
    if resp.status_code != 200:
        raise Exception(f'Response info: {resp.status_code}')
    soup_strainer = SoupStrainer('div', class_='pagination')
    soup = BeautifulSoup(resp.text, 'html.parser', parse_only=soup_strainer)
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


def _extract_image_urls(page_num: int, keyword: str) -> list[str]:
    url = os.path.join(PAGE_URL, str(page_num))
    params = {'q': keyword}
    resp = requests.get(url, params=params)
    soup_strainer = SoupStrainer('ul', class_='wallpapers')
    soup = BeautifulSoup(resp.text, 'html.parser', parse_only=soup_strainer)
    thumb_images = soup.find_all('img', class_='thumb_img')
    image_urls = []
    for thumb_image in thumb_images:
        image_urls.append(thumb_image.parent['href'].strip(
            '/').removesuffix('s.html'))
    return image_urls


def _download_wallpaper(image_url: str,
                        aspect_ratio: tuple[int, int] = (2560, 1440)):
    width, height = aspect_ratio
    image_url += '-' + str(width) + 'x' + str(height) + '.jpg'
    url = os.path.join(DOWNLOAD_URL, image_url)
    return download_img(url)


def random_wallpaper(keyword):
    """
    Returns a random wallpaper corresponding to the search term keyword.

    Args:
        keyword: search term (pass None to get any random image).
    """
    # Find the number of pages in the search result
    tries = 0
    max_tries = 10
    num_pages = _extract_num_of_search_pages(keyword)
    logging.info(f'Number of pages: {num_pages}')
    if num_pages > 0:
        while tries < max_tries:  # continue till a wallpaper with proper resolution is found
            # Select a random page number
            random_page_num = random.randint(1, num_pages)
            logging.info(f'Random page number: {random_page_num}')
            # Extract all image urls from the page
            image_urls = _extract_image_urls(random_page_num, keyword)
            # Select a random image url
            random_index = random.randint(0, len(image_urls)-1)
            random_image_url = image_urls[random_index]
            logging.info(f'Random image url {random_image_url}')
            # Download the wallpaper
            wp = _download_wallpaper(random_image_url)
            if wp:
                return wp  # return the path of downloaded wallpaper
            tries += 1
    return None  # no search results found for this keyword
