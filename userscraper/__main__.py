from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument("username", help="Your Instagram username.")
    parser.add_argument("--password", "-p", help="Your Instagram password. If not provided, it will be asked "
                                                 "interactively.")
    parser.add_argument("--target", "-t", nargs="+", help="One or more usernames to scrape. By default it is set to "
                                                          "your login username.")
    parser.add_argument("--followers", "-r", help="Scrape target's followers", action="store_true")
    parser.add_argument("--followees", "-e", help="Scrape target's followees", action="store_true")
    parser.add_argument("--not-followers", "-n", help="Scrape users not following target back", action="store_true")
    parser.add_argument("--count", "-c", help="Amount of items to scrape", type=int)
    args = parser.parse_args()
