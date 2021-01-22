import requests
import time

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
            #r = requests.get(url = url, params = data)
            #return r
            with requests.get(url = url, params = data, stream = False) as r:
                if r.status_code != 200 and 'sysdbg' in r.json() and r.json()['sysdbg'] == 'EOF':
                    #print('retry...')
                    time.sleep(3)
                    with requests.get(url = url, params = data, stream = False) as r:
                        return r
            #r = requests.get(url = url, params = data, stream = False)
            #if r.status_code != 200 and 'sysdbg' in r.json() and r.json()['sysdbg'] == 'EOF':
                #print('retry...')
                #r = requests.get(url = url, params = data, stream = False)
                return r
            #return r
        else:
            #r = requests.post(url = url, data = data)
            #return r
            with requests.post(url = url, data = data, stream = False) as r:
                if r.status_code != 200 and 'sysdbg' in r.json() and r.json()['sysdbg'] == 'EOF':
                    #print('retry...')
                    time.sleep(3)
                    with requests.post(url = url, data = data, stream = False) as r:
                        return r
            #r = requests.post(url = url, data = data, stream = False)
            #if r.status_code != 200 and 'sysdbg' in r.json() and r.json()['sysdbg'] == 'EOF':
                #print('retry...')
                #r = requests.post(url = url, data = data, stream = False)
                return r
            #return r

