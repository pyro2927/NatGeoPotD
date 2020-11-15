#!/usr/bin/env python
from datetime import datetime
import json
import os
import pathlib
import requests

def get_galary_json(year, month):
    year_month = "{}-{}".format(year, month)
    base_url = 'https://www.nationalgeographic.com'
    json_url = base_url + '/content/photography/en_US/photo-of-the-day/_jcr_content/.gallery.' + year_month + '.json'

    r = requests.get(json_url)
    return r.json()

def download_potd(photo_destination, photo_url):
    r = requests.get(photo_url, allow_redirects=True)
    open(photo_destination, 'wb').write(r.content)

## iterate through photos - and download only ones which are missing
def download_the_photos(natgeo_json_data):
    for photo in natgeo_json_data["items"]:
        if "uri" in photo["image"]:
            d = datetime.strptime(photo["publishDate"], "%B %d, %Y")
            photo_url = photo["image"]["uri"]
            folder = d.strftime("%Y/%m")
            dest = d.strftime("%Y/%m/%d.jpg")
            pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
            download_potd(dest, photo_url)

if __name__ == '__main__':
    j = get_galary_json(2020, 11)
    download_the_photos(j)