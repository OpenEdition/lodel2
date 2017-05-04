# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from werkzeug.wrappers import Response
from lodel.context import LodelContext

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
    
    ##@brief Log exception with lodel logger
    def log(self):
        LodelContext.expose_modules(globals(), {'lodel.logger': 'logger'})
        msg = "Webui HTTP exception : %s" % self
        if self.status_code / 100 == 4:
            logger.security(msg)
        elif self.status_code / 100 == 5:
            logger.error(msg)
        else:
            logger.warning(msg)
    
    def __str__(self):
        return "HTTP:%d '%s'" % (self.status_code, self.custom)

    def render(self, request):
        self.log()
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


##@brief Render multiple errors
class HttpErrors(HttpException):
    
    def __init__(self, errors, title = None, status_code = 400):
        super().__init__(status_code = status_code, tpl = 'errors.html',
            custom = title)
        self.errors = errors

    def __str__(self):
        ret = super().__str__()
        ret += ', '.join([ '%s: %s' % val for val in self.errors.items()])
        return ret

    def render(self, request):
        self.log()
        from .interface.template.loader import TemplateLoader
        loader = TemplateLoader()
        tpl_vars = {
            'status_code': self.status_code,
            'errors': self.errors,
            'title': self.custom }
        response = Response(
            loader.render_to_response(self.tpl, template_vars = tpl_vars),
            mimetype = 'text/html')
        response.status_code = self.status_code
        return response

        
