#-*- coding: utf-8 -*-

from Lodel.utils.mlstring import MlString
import datetime
from django.db import models


##
#
# returns an instance of the corresponding EmFieldType class for a given name
#
# @param name str: name of the field type
# @param kwargs dict: options of the field type
# @return EmFieldType
def get_field_type(name):
    class_name = 'EmField_'+name
    constructor = globals()[class_name]
    instance = constructor()
    return instance


##
#
# Generic Field type
class EmFieldType():

    def __init__(self, **kwargs):
        self.name = kwargs['name'] #TODO gérer le cas où le name n'est pas passé
        self.value = None
        self.options = kwargs

    def from_python(self, value):
        self.value = value


##
#
# Integer field type
class EmField_integer(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_integer, self).__init__(**kwargs)

    def to_django(self):
        return models.IntegerField(**self.options)


##
#
# Boolean field type
class EmField_boolean(EmFieldType):

    def __init__(self):
        super(EmField_boolean, self).__init__(**kwargs)

    def to_django(self):
        if 'nullable' in self.options and self.options['nullable'] == 'true':
            return models.NullBooleanField(**self.options)
        else:
            return models.BooleanField(**self.options)

##
#
# Varchar field type
class EmField_char(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_char, self).__init__(**kwargs)

    def to_django(self):
        return models.CharField(**self.options)


##
#
# Date field type
class EmField_date(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_date, self).__init__(**kwargs)

    def to_django(self):
        return models.DateField(**self.options)


##
#
# Text field type
class EmField_text(EmFieldType):
    def __init__(self, **kwargs):
        super(EmField_text, self).__init__(**kwargs)

    def to_django(self):
        return models.TextField(**self.options)


##
#
# Image field type
class EmField_image(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_image, self).__init__(**kwargs)

    def to_django(self):
        return models.ImageField(**self.options)


##
#
# File field type
class EmField_file(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_file, self).__init__(**kwargs)

    def to_django(self):
        return models.FileField(**self.options)


##
#
# URL field type
class EmField_url(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_url, self).__init__(**kwargs)

    def to_django(self):
        return models.URLField(**self.options)


##
#
# Email field type
class EmField_email(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_email, self).__init__(**kwargs)

    def to_django(self):
        return models.EmailField(**self.options)


##
#
# Datetime field type
class EmField_datetime(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_datetime, self).__init__(**kwargs)

    def to_django(self):
        return models.DateTimeField(**self.options)


##
#
# Time field type
class EmField_time(EmFieldType):

    def __init__(self, **kwargs):
        super(EmField_datetime, self).__init__(**kwargs)

    def to_django(self):
        return models.TimeField(**self.options)


##
#
# mlstring field type
class EmField_mlstring(EmField_char):

    def __init__(self, **kwargs):
        super(EmField_mlstring, self).__init__(**kwargs)

    def to_django(self):
        return models.CharField(**self.options)


##
#
# Icon field type
class EmField_icon(EmField_char):

    def __init__(self, **kwargs):
        super(EmField_icon, self).__init__(**kwargs)

    def to_django(self):
        return models.CharField(**self.options)
