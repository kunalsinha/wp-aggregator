import os
import requests
from bs4 import BeautifulSoup, SoupStrainer
import random
import logging
from utils import download_img

BASE_URL = 'http://wallpapersmug.com/'
SEARCH_URL = 'https://wallpapersmug.com/w/wallpaper'
PAGE_URL = 'https://wallpapersmug.com/w/wallpaper/latest/page/'
DOWNLOAD_URL = 'https://wallpapersmug.com/w/download/'


def _extract_num_of_search_pages(keyword):
    if not keyword:
        keyword = ''
    params = {'search': keyword}
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(SEARCH_URL, params=params, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Response info: {resp.status_code}')
    soup_strainer = SoupStrainer('nav', class_='pagy-nav pagination')
    soup = BeautifulSoup(resp.text, 'html.parser', parse_only=soup_strainer)
    try:
        return int(soup.nav.find_all('span')[-2].string)
    except Exception:
        return 0


def _extract_image_urls(page_num: int, keyword: str) -> list[str]:
    url = os.path.join(PAGE_URL, str(page_num))
    headers = {'User-Agent': 'Mozilla/5.0'}
    params = {'search': keyword}
    resp = requests.get(url, params=params, headers=headers)
    logging.info(f'URL: {resp.url}')
    soup_strainer = SoupStrainer('div', class_='item_img')
    soup = BeautifulSoup(resp.text, 'html.parser', parse_only=soup_strainer)
    thumb_images = soup.find_all('a')
    image_urls = []
    for thumb_image in thumb_images:
        image_urls.append(thumb_image['href'].strip('/'))
    return image_urls


def _download_wallpaper(image_url: str,
                        aspect_ratio: tuple[int, int] = (2560, 1440)):
    width, height = aspect_ratio
    resolution = str(width) + 'x' + str(height)
    url = os.path.join(DOWNLOAD_URL, resolution, image_url.rsplit('/')[-1])
    logging.info(url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup_strainer = SoupStrainer('a', class_='btn btn-primary')
    soup = BeautifulSoup(resp.text, 'html.parser', parse_only=soup_strainer)
    image_url = soup.a['href']
    logging.info(f'Image URL: {image_url}')
    return download_img(image_url)


def random_wallpaper(keyword):
    """
    Returns a random wallpaper corresponding to the search term keyword.

    Args:
        keyword: search term (pass None to get any random image).
    """
    # Find the number of pages in the search result
    tries = 0
    max_tries = 1
    num_pages = _extract_num_of_search_pages(keyword)
    logging.info(f'Number of pages: {num_pages}')
    if num_pages > 0:
        while tries < max_tries:  # continue till a wallpaper with proper resolution is found
            logging.info('TRIES: ' + str(tries))
            # Select a random page number
            random_page_num = random.randint(1, num_pages)
            logging.info(f'Random page number: {random_page_num}')
            # Extract all image urls from the page
            image_urls = _extract_image_urls(random_page_num, keyword)
            logging.info(image_urls)
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
