import json
import requests
from functools import partial
import time
from exceptions import *
import pickle
from typing import Generator


class Instagram:
    def __init__(self, request_timeout: float = 10.0):
        self.request_timeout = request_timeout
        self.session = self.default_session()
        self._two_factor_data = None

    def default_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459'
        })
        session.request = partial(session.request, timeout=self.request_timeout)
        return session

    def login(self, username: str, password: str) -> None:
        resp = self.session.get("https://www.instagram.com/")
        self.session.headers.update({'X-CSRFToken': resp.cookies['csrftoken']})

        payload = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
            'username': username
        }
        resp = self.session.post("https://www.instagram.com/accounts/login/ajax/", data=payload)
        resp_json = resp.json()

        if resp_json.get('two_factor_required'):
            two_factor_id = resp_json['two_factor_info']['two_factor_identifier']
            self._two_factor_data = (two_factor_id, username)
            raise TwoFactorAuthRequiredError(f"2FA is required for {username}")
        if resp_json['status'] != 'ok':
            if 'message' in resp_json and len(resp_json['message']) > 0:
                raise AuthenticationError(f"Unable to log in. Instagram's message was: {resp_json['message']}")
            else:
                raise AuthenticationError(f"Unable to log in. Instagram's JSON was: {resp_json}")
        if not resp_json['authenticated']:
            if resp_json['user']:
                raise AuthenticationError(f"Unable to log in. Incorrect password for {username}")
            else:
                raise AuthenticationError(f"Unable to log in. Username {username} doesn't exist.")
        self.session.get("https://www.instagram.com/")

    def verify_two_factor(self, two_factor_code: str) -> None:
        if self._two_factor_data is None:
            raise NoTwoFactorAuthPendingError("No 2FA is pending.")

        two_factor_id, username = self._two_factor_data
        payload = {
            'identifier': two_factor_id,
            'username': username,
            'verificationCode': two_factor_code
        }
        resp = self.session.post("https://www.instagram.com/accounts/login/ajax/two_factor/", data=payload)
        resp_json = resp.json()
        if resp_json['status'] != 'ok':
            if resp_json.get('error_type') and resp_json['error_type'].find("code_invalid") != -1:
                raise AuthenticationError("Incorrect 2FA code.")
        self._two_factor_data = None

    def save_session(self, session_file: str) -> None:
        with open(session_file, 'wb') as file:
            file.write(pickle.dumps(self.session.cookies))

    def load_session(self, session_file: str) -> None:
        with open(session_file, 'rb') as file:
            self.session.cookies = pickle.loads(file.read())
        self.session.headers.update({'X-CSRFToken': self.session.cookies['csrftoken']})

    def get_user_info(self, username: str) -> dict:
        self.session.headers.update({"Host": "i.instagram.com", "User-Agent": "Instagram 219.0.0.12.117 Android"})
        resp = self.session.get(f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}")
        if resp.status_code == 404:
            raise UserNotFoundError(f"Unable to get user info. Username {username} was not found.")
        self.session.headers.update({"Host": "www.instagram.com", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; "
                                                                                "x64; rv:100.0) Gecko/20100101 "
                                                                                "Firefox/100.0"})
        data = resp.json()['data']['user']
        user_info = {
            'biography': data['biography'],
            'followees_count': data['edge_follow']['count'],
            'followers_count': data['edge_followed_by']['count'],
            'post_count': data['edge_owner_to_timeline_media']['count'],
            'external_url': data['external_url'],
            'facebook_id': data['fbid'],
            'full_name': data['full_name'],
            'id': data['id'],
            'is_business_account': data['is_business_account'],
            'has_joined_recently': data['is_joined_recently'],
            'is_private': data['is_private'],
            'is_professional_account': data['is_professional_account'],
            'is_verified': data['is_verified'],
            'profile_pic_url': data['profile_pic_url'],
            'profile_pic_url_hd': data['profile_pic_url_hd'],
            'username': data['username']
        }
        return user_info

    def query_nodes(self, query_id: str, variables: dict, edge_extractor: str) -> Generator[dict, None, None]:
        variables['first'] = 50

        def _query():
            variables_json = json.dumps(variables)
            resp = self.session.get("https://www.instagram.com/graphql/query/", params={'query_id': query_id,
                                                                                        'variables': variables_json})
            return resp.json()['data']['user'][edge_extractor]

        data = _query()
        if not data['edges']:
            raise AccessToDataDeniedError("Unable to query nodes since you don't have access to this information.")

        for edge in data['edges']:
            yield edge['node']
        while data['page_info']['has_next_page']:
            variables['after'] = data['page_info']['end_cursor']
            data = _query()
            for edge in data['edges']:
                yield edge['node']

    def get_followers(self, user_id: str, max_count: int = None) -> Generator[dict, None, None]:
        query_id = '17851374694183129'
        followers_gen = self.query_nodes(query_id, {'id': user_id}, 'edge_followed_by')
        for count, follower in enumerate(followers_gen):
            if max_count and max_count == count:
                break
            yield follower

    def get_followees(self, user_id: str, max_count: int = None) -> Generator[dict, None, None]:
        query_id = '17874545323001329'
        followees_gen = self.query_nodes(query_id, {'id': user_id}, 'edge_follow')
        for count, followee in enumerate(followees_gen):
            if max_count and count > max_count:
                break
            yield followee

    def is_logged_in(self) -> bool:
        resp = self.session.get("https://www.instagram.com/")
        if resp.text.find("not-logged-in") == -1:
            return True
        return False
