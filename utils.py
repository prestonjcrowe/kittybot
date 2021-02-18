import email.utils
import smtplib
import os
import requests
import shutil

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT


def download_image(url, name):
    if url == None:
        return None

    name = name.replace("/", "|").replace(" ", "_")
    filename = "img/" + name + ".jpeg"
    r = requests.get(url, stream=True)

    if r.status_code == 200:
        r.raw.decode_content = True
        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        return filename
    else:
        return None


def print_log(msg, log_file):
    print(msg)
    with open(log_file, "a") as f:
        f.write(msg)


def write_log(cats, log_file):
    with open(log_file, "a") as f:
        f.writelines(
            list(map(lambda c: f'{c["description"]}\n{c["url"]}\n', cats))
        )
        f.write("\n\n")


def get_dt_str():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def filter_results(cats, log_file):
    with open(log_file, "r") as f:
        oldKitties = f.readlines()
        return list(filter(lambda c: c["url"] + "\n" not in oldKitties, cats))


def send_new_kitty_email(cats, targets):
    fromStr = "KITTY BOT"
    my_email = os.environ["SENDMAIL_USER"]
    password = os.environ["SENDMAIL_PASS"]

    msg = MIMEMultipart()
    msg["Subject"] = f"Kitty Bot - {len(cats)} New Kitties!"
    msg["From"] = email.utils.formataddr((fromStr, my_email))
    msg["To"] = email.utils.formataddr(("Kiity Bot Subscriber", my_email))

    dtStr = get_dt_str()
    content = f"[{dtStr}] New Kitties Posted Today\n\n"
    for cat in cats:
        line = f'{cat["description"]}\n{cat["url"]}\n\n'
        content += line
        if cat["img_path"]:
            img_data = open(cat["img_path"], "rb").read()
            image = MIMEImage(img_data, name=os.path.basename(cat["img_path"]))
            msg.attach(image)

    text = MIMEText(content)
    msg.attach(text)

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(my_email, password)

    # Allow for email handles only or option to provide full address
    for target in targets:
        address = target
        if '@' not in target:
            address = target + "@gmail.com"

        server.sendmail(my_email, address, msg.as_string())
        print_log(f"Sent new kitty update to {address}\n", "kitty_log.txt")
        server.quit()
