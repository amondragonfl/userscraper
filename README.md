# userscraper
Scrape a user's Instagram followers, followees, and users who don't follow the user back. 

## Installation
```console
$ git clone https://github.com/amondragonfl/userscraper.git
$ cd userscraper
$ python3 -m pip install -r requirements.txt
```

## Usage
```
positional arguments:
  username              Your Instagram username.

options:
  -h, --help            show this help message and exit
  --password PASSWORD, -p PASSWORD
                        Your Instagram password. If not provided, it will be asked interactively.
  --target TARGET [TARGET ...], -t TARGET [TARGET ...]
                        One or more usernames to scrape. By default it is set to your login username.
  --followers, -r       Scrape target's followers
  --followees, -e       Scrape target's followees
  --not-followers, -n   Scrape users not following the target back
  --count COUNT, -c COUNT
                        Maximum amount of items to scrape
  --profile-pic, -P     Download target's profile picture
  --save, -s            Save scraped data to current working directory
```
To scrape your followers: 
```console
$ python3 userscraper <your username> -r
```
To scrape some else's followers:
```console
$ python3 userscraper <your username> -t <target username> -r
```
To scrape the users who don't follow you back: 
```console
$ python3 userscraper <your username> -n
```
