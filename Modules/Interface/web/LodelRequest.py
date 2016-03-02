from werkzeug.wrappers import Request
from werkzeug.urls import url_decode


class LodelRequest(Request):

    def __init__(self, environ):
        super().__init__(environ)
        self.PATH = self.path.lstrip('/')
        self.FILES = self.files.to_dict(flat=False)
        self.GET = url_decode(self.query_string).to_dict(flat=False)
        self.POST = self.form.to_dict(flat=False)
