from exceptions import TwoFactorAuthRequiredError, AuthenticationError, UserNotFoundError
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
    parser.add_argument("--profile-pic", "-P", help="Download target's profile picture", action="store_true")
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
                    print("Logging in...")
                    scraper.login(args.username, args.password)
                except TwoFactorAuthRequiredError:
                    code = input("Enter 2FA code: ")
                    scraper.verify_two_factor(code)
            except AuthenticationError as err:
                raise SystemExit(err)
            scraper.save_session(f"{args.username}-session.dat")

    if not args.target:
        args.target = [args.username]

    for target in args.target:
        try:
            target_info = scraper.get_user_info(target)
            target_id = target_info["id"]
        except UserNotFoundError:
            print(f"Target {target} was not found.")
            continue

        if args.followers or args.not_followers:
            print(f"Scraping {target} followers...")
            target_followers = {user["username"] for user in scraper.get_followers(target_id, max_count=args.count)}
        if args.followees or args.not_followers:
            print(f"Scraping {target} followees...")
            target_followees = {user["username"] for user in scraper.get_followees(target_id, max_count=args.count)}

        if args.followers:
            print(f"[{target} followers]")
            with open(f"{target}-followers.txt", "w") as file:
                for follower in target_followers:
                    file.write(follower + "\n")
                    print(f"@{follower}")
            print(f"Total amount of followers scraped: {len(target_followers)}\n")

        if args.followees:
            print(f"[{target} followees]")
            with open(f"{target}-followees.txt", "w") as file:
                for followee in target_followees:
                    file.write(followee + "\n")
                    print(f"@{followee}")
            print(f"Total amount of followees scraped: {len(target_followees)}\n")

        if args.not_followers:
            print(f"[{target} not-followers]")
            count = 0
            with open(f"{target}-not-followers.txt", "w") as file:
                for followee in target_followees:
                    if followee not in target_followers:
                        file.write(followee + "\n")
                        print(f"@{followee}")
                        count += 1
            print(f"Total amount of not-followees scraped: {count}\n")

        if args.profile_pic:
            print(f"Downloading {target} profile picture...")
            scraper.download_image(target_info["profile_pic_url_hd"], f"{target}-pp.jpeg")


if __name__ == "__main__":
    main()
