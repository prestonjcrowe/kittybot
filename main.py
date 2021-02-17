from emailer import Emailer
from bs4 import BeautifulSoup
import requests
import random
from selenium import webdriver
import time
import os
import shutil # to save it locally

LOG_FILE = 'kitty_log.txt'
EMAIL = os.environ['SENDMAIL_USER']
PASSWORD = os.environ['SENDMAIL_PASS']
EMAILER = Emailer(EMAIL, PASSWORD, 'KITTY BOT')

def download_image(url, name):

    if url == None:
        return None

    ## Set up the image URL and filename
    filename = 'img/' + name + '.jpeg'

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(url, stream = True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        
        # Open a local file with wb ( write binary ) permission.
        with open(filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)
            
        print('Image sucessfully Downloaded: ',filename)
        return filename
    else:
        print('Image Couldn\'t be retreived')
        return None

def write_log(cats):
    with open(LOG_FILE, 'a') as f:
        f.writelines(list(map(lambda c: c['url'] + '\n', cats)))

def filter_results(cats):
    with open(LOG_FILE, 'r') as f:
        oldKitties = f.readlines()
        return list(filter(lambda c: c['url'] + '\n' not in oldKitties, cats))

distance = 50
url = f'https://www.petfinder.com/search/cats-for-adoption/us/wa/seattle/?age%5B0%5D=Baby&age%5B1%5D=Young&days_on_petfinder=1&distance={distance}'

options = webdriver.ChromeOptions()
options.add_argument('headless')

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(2)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
cards = soup.find_all('pfdc-pet-card', {'class' : 'petCard'})
images = soup.find_all('img', {'class' : 'petCard-media-img'})
driver.close()
cats = []

for card in cards:
    body = card.find('div', {'class' : 'petCard-body'})
    bodyInfo = card.find_all('span')
    img = card.find_all('pfdc-lazy-load', {'class' : 'petCard-media'})
    link = card.find('a', {'class': 'petCard-link'})
    img_url = img[0]['src'] if len(img) > 0 else None
    url = link['href']
    name = bodyInfo[0].text
    description = bodyInfo[1].text
    image_path = download_image(img_url, name)

    cat = {
        'name' : name,
        'description': description,
        'img': img_url,
        'img_path': image_path,
        'url': url
    }
    cats.append(cat)

new_cats = filter_results(cats)


if (len(new_cats) > 0):
    print(f'Found {len(new_cats)} new kitties')
    EMAILER.new_kitties(new_cats)
    write_log(new_cats)

else:
    print('No new kitties found')
