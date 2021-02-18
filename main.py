import requests
import argparse
import random
import time
import os
import shutil
import utils

from bs4 import BeautifulSoup
from selenium import webdriver


def main():
    # Parse args
    parser = argparse.ArgumentParser(
        description="Kitty bot - New Pet Notifier",
    )
    parser.add_argument(
        "-t",
        "--targets",
        nargs="+",
        help="Gmail addresses to notify (identifier only)",
        required=True,
    )
    args = parser.parse_args()

    # Config
    DISTANCE = 50
    LOG_FILE = "kitty_log.txt"
    URL = (
        "https://www.petfinder.com/search/cats-for-adoption/us/wa/seattle/"
        + "?age%5B0%5D=Baby&age%5B1%5D=Young&distance="
        + str(DISTANCE)
        + "&sort%5B0%5D=recently_added"
    )

    # Print log header with timestamp for this run
    dtStr = utils.get_dt_str()
    utils.print_log(
        f"[{dtStr}] Kittybot is looking for new kitties\n", LOG_FILE
    )

    # Instantiate web driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=options)

    # Parse page source
    driver.get(URL)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("pfdc-pet-card", {"class": "petCard"})
    driver.quit()
    cats = []

    # Iterate through listings and collect data
    for card in cards:
        bodyInfo = card.find_all("span")
        img = card.find_all("pfdc-lazy-load", {"class": "petCard-media"})
        link = card.find("a", {"class": "petCard-link"})
        img_url = img[0]["src"] if len(img) > 0 else None
        url = link["href"]
        name = bodyInfo[0].text
        description = bodyInfo[1].text
        image_path = utils.download_image(img_url, name)

        cat = {
            "name": name,
            "description": description,
            "img": img_url,
            "img_path": image_path,
            "url": url,
        }
        if "Adoption Pending" not in name:
            cats.append(cat)

    # Filter results to previously unseen cats and send email
    new_cats = utils.filter_results(cats, LOG_FILE)
    if len(new_cats):
        utils.print_log(f"Found {len(new_cats)} new kitties\n", LOG_FILE)
        utils.send_new_kitty_email(new_cats, args.targets)
        utils.write_log(new_cats, LOG_FILE)

    else:
        utils.print_log("No new kitties found\n", LOG_FILE)


if __name__ == "__main__":
    main()
