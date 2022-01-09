"""
Script to fetch images to buffer
"""
import logging
import os
import sys
from pathlib import Path

from db import DB
from settings import XSIDE_HOST, XSIDE_USER, XSIDE_PASSWORD, MEDIA_ROOT
from xside_client import XSide

xside = XSide(host=XSIDE_HOST, email=XSIDE_USER, password=XSIDE_PASSWORD)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def download_images(item):
    """Method that downloads images from item to MEDIA_ROOT folder"""
    for path in item['images']:
        image = xside.fetch_image(path)
        path_array = path.split('/')
        Path(os.path.join(MEDIA_ROOT, *path_array[:-1])).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(MEDIA_ROOT, path), 'wb') as f:
            f.write(image.read())


def fetch():
    """Fetch info and images"""
    items = []
    page = 0
    while True:  # fetch info
        buf = xside.get_items(page=page)
        if buf['data']:
            items.extend(buf['data'])
        else:
            break
        page += 1

        for item in buf['data']:  # download images
            download_images(item)

    db = DB()
    db.create_items_table()  # clear old records
    db.add_items(items)  # add all items

    logging.info(f"Imported {len(items)} items")

if __name__ == "__main__":
    fetch()
