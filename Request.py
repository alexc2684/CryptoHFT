from requests import get, post


class Request:
    def __init__(self, headers, url):
        self.headers = headers
        self.url = url

    def get_request(self):
        return get(self.url, headers=self.headers)

    def post_request(self):
        return post(self.url, headers=self.headers)
