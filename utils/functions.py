import requests
import os
import shutil
import logging


def download_img(url, dest=None, file_name=None):
    """
    Downloads an image from the given url.
    Args:
        url (str): url of the image.
        dest (str): path where the image should be saved.
        file_name (str): name with which the image should be saved.
    """
    # Set a default dest if it is empty
    if not dest:
        dest = os.path.expanduser('~/Pictures/wallpapers')
    # Create dest if it doesn't exist
    if not os.path.exists(dest):
        os.makedirs(dest)
    # Extract file_name from url if empty
    if not file_name:
        file_name = url.rsplit('/', maxsplit=1)[-1]
    file_path = os.path.join(dest, file_name)
    r = requests.get(url, stream=True)
    # If url returns OK and is indeed an image then download it
    if r.status_code == 200 and r.headers['Content-Type'] == 'image/jpeg':
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        return file_path
    else:
        logging.info(f'Resolution not found: {url}')
        return None
