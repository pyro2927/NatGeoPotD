#!/usr/bin/env python
from PIL import Image
from datetime import date
from datetime import datetime
from re import search
import json
import os
import pathlib
import piexif
import requests

def get_galary_json(year, month):
    year_month = "{}-{}".format(year, month)
    print("Downloading {}".format(year_month))
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
        d = datetime.strptime(photo["publishDate"], "%B %d, %Y")
        folder = d.strftime("%Y/%m")
        dest = d.strftime("%Y/%m/%d.jpg")
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
        # Skip downloading if we already have it
        if not os.path.exists(dest):
            if "uri" in photo["image"]:
                photo_url = photo["image"]["uri"]
                download_potd(dest, photo_url)
        # set exif data
        im = Image.open(dest)
        try:
            exif_dict = piexif.load(im.info["exif"])
        except:
            exif_dict = {"0th": {}}
        exif_dict["0th"][piexif.ImageIFD.XPTitle] = bytearray(photo["image"]["title"], 'utf-8')
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = bytearray(photo["image"]["caption"], 'utf-8')
        try:
            # Being fancy with regex to account for typos on NatGeo's side
            author = search("(?i)Photograp?hy? by (.*)(, Nat|$)", photo["image"]["credit"]).group(1)
            exif_dict["0th"][piexif.ImageIFD.XPAuthor] = bytearray(author, 'utf-16')
        except:
            print("Unable to pull author name from {}".format(photo["image"]["credit"]))
        # write exif back
        try:
            exif_bytes = piexif.dump(exif_dict)
            im.save(dest, "jpeg", exif=exif_bytes)
        except:
            print("Error writing exif data back :(")

if __name__ == '__main__':
    dt = date.today()
    y = dt.year
    m = dt.month
    while True:
        j = get_galary_json(y, m)
        download_the_photos(j)
        m = m - 1
        if m == 0:
            m = 12
            y = y - 1
