import requests

access_token = "access_token"

class HTTPProvider:
    endpoint = None

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def make_request(self, method, path, data):
        url = self.endpoint + '/' + path
        data['access_token'] = access_token
        # print('url = {}, data = {}'.format(url, data))

        if method == 'GET':
            r = requests.get(url = url, params = data)
            return r
        else:
            r = requests.post(url = url, data = data)
            return r
