# Kitty Bot
This bot scrapes Petfinder for newly posted kittens and sends
an email to each of the specified targets for every new batch.
I run this bot on a cron job from my RBP every 30 minutes.

`0,30 * * * * python home/pi/kittybot/run.sh`

### Requirements
- chromedriver must be installed and available on your $PATH
- bs4, requests, selenium (see requirements.txt)

### Run
`python main.py -t example1@gmail.com example2@gmail.com`

If you want to run this as a cron job, I recommend creating
your own `run.sh` that exports the following environment
variables and runs the script:

```bash
#!/bin/bash
export SENDMAIL_USER='your_email@gmail.com'
export SENDMAIL_PASS='gmail_app_specific_pass'

# Run main.py
cd /home/pi/kittybot
/home/pi/.pyenv/versions/kittybot/bin/python3.8 /home/pi/kittybot/main.py
```

