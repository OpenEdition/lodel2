#-*- coding: utf-8 -*-

import jinja2
from .api import api_lodel_templates

import settings
from .exceptions import NotAllowedCustomAPIKeyError


class TemplateLoader(object):

    __reserved_template_keys = ['lodel']

    ## @brief Initializes a template loader
    #
    # @param search_path str : the base path from which the templates are searched. To use absolute paths, you can set
    #                          it to the root "/". By default, it will be the root of the project, defined in the
    #                          settings of the application
    # @param follow_links bool : indicates whether or not to follow the symbolic links (default: True)
    def __init__(self, search_path=settings.base_path, follow_links=True):
        self.search_path = search_path
        self.follow_links = follow_links

    ## @brief Renders a HTML content of a template
    #
    # @param template_file str : path to the template file (starting from the base path used to instanciate the
    #                            TemplateLoader)
    # @param template_vars dict : parameters to be used in the template
    # @param template_extra list : list of tuples indicating the custom modules to import in the template (default: None).
    #                              The modules are given as tuples with the format : ('name_to_use_in_the_template', module)
    #
    # @return str. String containing the HTML output of the processed templated
    def render_to_html(self, template_file, template_vars={}, template_extra=None):

        loader = jinja2.FileSystemLoader(searchpath=self.search_path, followlinks=self.follow_links)
        environment = jinja2.Environment(loader=loader)
        template = environment.get_template(template_file)

        # Lodel2 default api is loaded
        template.globals['lodel'] = api_lodel_templates

        # Extra modules are loaded
        if template_extra is not None:
            for extra in template_extra:
                if not self.__is_allowed_template_key(extra[0]):
                    raise NotAllowedCustomAPIKeyError("The name 'lodel' is a reserved one for the loaded APIs in templates")
                template.globals[extra[0]] = extra[1]

        return template.render(template_vars)

    ## @brief Checks if the key used for the template is allowed
    #
    # @param key str
    # @return bool
    def __is_allowed_template_key(self, key):
        return False if key in self.__class__.__reserved_template_keys else True