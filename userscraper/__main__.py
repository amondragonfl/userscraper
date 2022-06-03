from exceptions import TwoFactorAuthRequiredError, AuthenticationError
from instagram import InstagramScraper
from argparse import ArgumentParser
from getpass import getpass


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
    parser.add_argument("--count", "-c", help="Maximum amount of items to scrape", type=int)
    args = parser.parse_args()

    if args.not_followers and args.count:
        raise SystemExit("--not-followers and --count cannot be used together, since it would throw inaccurate results.")

    scraper = InstagramScraper()
    try:
        scraper.load_session(f"{args.username}-session.dat")
        if not scraper.is_logged_in():
            print("Previous session expired.")
            raise EOFError
    except (FileNotFoundError, EOFError):
        if not args.password:
            args.password = getpass(f"Enter password for {args.username}: ")
            try:
                try:
                    scraper.login(args.username, args.password)
                except TwoFactorAuthRequiredError:
                    code = input("Enter 2FA code: ")
                    scraper.verify_two_factor(code)
            except AuthenticationError as err:
                raise SystemExit(err)
            scraper.save_session(f"{args.username}-session.dat")


if __name__ == "__main__":
    main()
