import requests
import json
import time




class AllegroAuth:
    """Allegro API Auth Device Flow
    Allows get access token
    """
    CODE_URL = "https://allegro.pl/auth/oauth/device"
    TOKEN_URL = "https://allegro.pl/auth/oauth/token"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_code(self):
        """
        get device code and verificaion link for user
        :return:
        """
        try:
            payload = {'client_id': self.client_id}
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            api_call_response = requests.post(self.CODE_URL, auth=(self.client_id, self.client_secret), headers=headers, data=payload, verify=False)

            return api_call_response.json()
        except requests.exceptions.HTTPError as err:
            print(f"code error {err}")
            return None

    def get_access_token(self, device_code):
        """"""
        try:
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            data = {'grant_type': 'urn:ietf:params:oauth:grant-type:device_code', 'device_code': device_code}
            api_call_response = requests.post(self.TOKEN_URL, auth=(self.client_id, self.client_secret),
                                              headers=headers, data=data, verify=True) #w allegro podane False
            return api_call_response
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    def await_for_access_token(self, interval, device_code):
        while True:
            time.sleep(interval)
            result_access_token = self.get_access_token(device_code)
            token = json.loads(result_access_token.text)
            if result_access_token.status_code == 400:
                if token['error'] == 'slow_down':
                    interval += interval
                if token['error'] == 'access_denied':
                    break
            else:
                return token['access_token']

    def authorize(self):
        code = self.get_code()
        print(f"open in broser: {code['verification_uri_complete']}")
        token = self.await_for_access_token(int(code['interval']), code['device_code'])

    def get_headers(self, token):
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.allegro.public.v1+json"
        }