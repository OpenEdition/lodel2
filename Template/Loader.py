#-*- coding: utf-8 -*-

import jinja2
import settings


class TemplateLoader(object):

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
        if template_extra is not None:
            for extra in template_extra:
                template.globals[extra[0]] = extra[1]
        return template.render(template_vars)
