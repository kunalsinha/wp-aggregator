from abc import ABC, abstractmethod
import random
import logging


class WallpaperBase(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def _extract_num_of_search_pages(self, keyword: str) -> int:
        pass

    @abstractmethod
    def _extract_image_urls(self, page_num: int, keyword: str) -> list[str]:
        pass

    @abstractmethod
    def _download_wallpaper(self, image_url: str, aspect_ratio: tuple[int, int] = (2560, 1440)):
        pass

    def random_wallpaper(self, keyword):
        """
        Returns a random wallpaper corresponding to the search term keyword.

        Args:
            keyword: search term (pass None to get any random image).
        """
        # Find the number of pages in the search result
        tries = 0
        max_tries = 10
        num_pages = self._extract_num_of_search_pages(keyword)
        logging.info(f'Number of pages: {num_pages}')
        if num_pages > 0:
            while tries < max_tries:  # continue till a wallpaper with proper resolution is found
                logging.info('TRIES: ' + str(tries))
                # Select a random page number
                random_page_num = random.randint(1, num_pages)
                logging.info(f'Random page number: {random_page_num}')
                # Extract all image urls from the page
                image_urls = self._extract_image_urls(random_page_num, keyword)
                logging.info(image_urls)
                # Select a random image url
                random_index = random.randint(0, len(image_urls)-1)
                random_image_url = image_urls[random_index]
                logging.info(f'Random image url {random_image_url}')
                # Download the wallpaper
                wp = self._download_wallpaper(random_image_url)
                if wp:
                    return wp  # return the path of downloaded wallpaper
                tries += 1
        return None  # no search results found for this keyword
