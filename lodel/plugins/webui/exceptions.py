#-*- coding: utf-8 -*-

from werkzeug.wrappers import Response

class HttpException(Exception):

    STATUS_STR = {
        4:{
            400: 'Bad request',
            401: 'Unauthorized',
            402: 'Payment required',
            403: 'Forbidden',
            404: 'Not found',
            418: 'I\'m a teapot', #RFC 2324
        },
        5:{
            500: 'Internal server error',
            501: 'Not implemented',
        },
    }

    def __init__(self, status_code = 500, tpl = 'error.html', custom = None):
        self.status_code = status_code
        self.tpl = tpl
        self.custom = custom

    def render(self, request):
        from .interface.template.loader import TemplateLoader
        loader = TemplateLoader()
        tpl_vars = {
            'status_code': self.status_code,
            'status_str': self.status_str(self.status_code),
            'custom': self.custom }
        response = Response(
            loader.render_to_response(self.tpl, template_vars = tpl_vars),
            mimetype = 'text/html')
        response.status_code = self.status_code
        return response

    @staticmethod
    def status_str(status_code):
        status_fam = status_code / 100
        if status_fam not in HttpException.STATUS_STR or \
            status_code not in HttpException.STATUS_STR[status_fam]:
            return 'Unknown'
        else:
            return HttpException.STATUS_STR[status_fam][status_code]



        
