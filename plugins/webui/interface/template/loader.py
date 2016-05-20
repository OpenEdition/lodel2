# -*- coding: utf-8 -*-
import jinja2
import os

import settings
from .api import api_lodel_templates
from .exceptions.not_allowed_custom_api_key_error import NotAllowedCustomAPIKeyError

from ...main import PLUGIN_PATH
TEMPLATE_PATH = os.path.realpath(os.path.join(PLUGIN_PATH, 'templates/'))

class TemplateLoader(object):

    _reserved_template_keys = ['lodel']

    ## @brief Initializes a template loader
    #
    # @param search_path str : the base path from which the templates are searched. To use absolute paths, you can set
    # it to the root "/". By default, it will be the root of the project, defined in the settings of the application.
    # @param follow_links bool : indicates whether or not to follow the symbolic links (default: True)
    # @param is_cache_active bool : indicates whether or not the cache should be activated or not (default: True)
    # @todo connect this to the new settings system
    def __init__(self, search_path=TEMPLATE_PATH, follow_links=True, is_cache_active=True):
        self.search_path = search_path
        self.follow_links = follow_links
        self.is_cache_active = is_cache_active

    ## @brief Renders a HTML content of a template
    #
    # @see template.loader.TemplateLoader.render_to_response
    #
    # @return str. String containing the HTML output of the processed templated
    def render_to_html(self, template_file, template_vars={}, template_extra=None):
        loader = jinja2.FileSystemLoader(searchpath=self.search_path)
        environment = jinja2.Environment(loader=loader) if self.is_cache_active else jinja2.Environment(loader=loader,
                                                                                                        cache_size=0)
        template = environment.get_template(template_file)

        # lodel2 default api is loaded
        # TODO change this if needed
        template.globals['lodel'] = api_lodel_templates

        # Extra modules are loaded
        if template_extra is not None:
            for extra in template_extra:
                if not self._is_allowed_template_key(extra[0]):
                    raise NotAllowedCustomAPIKeyError("The name '%s' is a reserved one for the loaded APIs in "
                                                      "templates" % extra[0])
                template.globals[extra[0]] = extra[1]

        return template.render(template_vars)

    ## @brief Renders a template into an encoded form ready to be sent to a wsgi response
    #
    # @param template_file str : path to the template file (starting from the base path used to instanciate the
    # TemplateLoader)
    # @param template_vars dict : parameters to be used in the template
    # @param template_extra list : list of tuples indicating the custom modules to import in the template
    # (default: None).
    #
    # The modules are given as tuples with the format : ('name_to_use_in_the_template', module)
    #
    # @return str
    def render_to_response(self, template_file, template_vars={}, template_extra=None):
        return self.render_to_html(template_file=template_file, template_vars=template_vars,
                                   template_extra=template_extra).encode()

    ## @brief Checks if the key used for the template is allowed
    #
    # @param key str
    # @return bool
    def _is_allowed_template_key(self, key):
        return False if key in self.__class__.__reserved_template_keys else True
