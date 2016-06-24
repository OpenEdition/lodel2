#-*- coding: utf-8 -*-

import functools
from lodel.editorial_model.components import *
from lodel.leapi.leobject import LeObject
from lodel.leapi.datahandlers.base_classes import DataHandler

##@brief Generate python module code from a given model
# @param model lodel.editorial_model.model.EditorialModel
def dyncode_from_em(model):
    
    # Generation of LeObject child classes code
    cls_code, modules, bootstrap_instr = generate_classes(model)

    # Header
    imports = """from lodel.leapi.leobject import LeObject
from lodel.leapi.datahandlers.base_classes import DataField
from lodel.plugin.hooks import LodelHook
"""
    for module in modules:
        imports += "import %s\n" % module
    
    class_list = [ LeObject.name2objname(cls.uid) for cls in get_classes(model) ]

    # formating all components of output
    res_code = """#-*- coding: utf-8 -*-
{imports}
{classes}
{bootstrap_instr}
dynclasses = {class_list}
{init_hook}
""".format(
            imports = imports,
            classes = cls_code,
            bootstrap_instr = bootstrap_instr,
            class_list = '[' + (', '.join([cls for cls in class_list]))+']',
            init_hook = datasource_init_hook(),
    )
    return res_code

##@brief Produce the source code of the LodelHook that initialize datasources
#in dyncode
#@return str
def datasource_init_hook():
    return """
@LodelHook("lodel2_plugins_loaded")
def lodel2_dyncode_datasources_init(self, caller, payload):
    for cls in dynclasses:
        cls._init_datasources()
    from lodel.plugin.hooks import LodelHook
    LodelHook.call_hook("lodel2_dyncode_loaded", __name__, dynclasses)
"""

##@brief return A list of EmClass sorted by dependencies
#
# The first elts in the list depends on nothing, etc.
# @return a list of EmClass instances
def emclass_sorted_by_deps(emclass_list):
    def emclass_deps_cmp(cls_a, cls_b):
        return len(cls_a.parents_recc) - len(cls_b.parents_recc)
    ret = sorted(emclass_list, key = functools.cmp_to_key(emclass_deps_cmp))
    return ret

##@brief Returns a list of EmClass that will be represented as LeObject child classes
def get_classes(model):
    return [ cls for cls in emclass_sorted_by_deps(model.classes()) if not cls.pure_abstract ]

##@brief Given an EmField returns the data_handler constructor suitable for dynamic code
def data_handler_constructor(emfield):
    #dh_module_name = DataHandler.module_name(emfield.data_handler_name)+'.DataHandler'
    get_handler_class_instr = 'DataField.from_name(%s)' % repr(emfield.data_handler_name)
    options = []
    for name, val in emfield.data_handler_options.items():
        if name == 'back_reference' and isinstance(val, tuple):
            options.append('{optname}: ({leo_name}, {fieldname})'.format(
                optname = repr(name),
                leo_name = LeObject.name2objname(val[0]),
                fieldname = repr(val[1]),))
        else:
            options.append(repr(name)+': '+forge_optval(val))

    return '{handler_instr}(**{{ {options} }})'.format(
                                                        handler_instr = get_handler_class_instr,
                                                        options = ', '.join(options))
            
##@brief Return a python repr of option values
def forge_optval(optval):
    if isinstance(optval, dict):
        return '{' + (', '.join( [ '%s: %s' % (repr(name), forge_optval(val)) for name, val in optval.items()])) + '}'

    if isinstance(optval, (set, list, tuple)):
        return '[' + (', '.join([forge_optval(val) for val in optval])) + ']'
        
    if isinstance(optval, EmField):
        return "{leobject}.data_handler({fieldname})".format(
                leobject = LeObject.name2objname(optval._emclass.uid),
                fieldname = repr(optval.uid)
            )
    elif isinstance(optval, EmClass):
        return LeObject.name2objname(optval.uid)
    else:
        return repr(optval)

##@brief Generate dyncode from an EmClass
# @param model EditorialModel : 
# @param emclass EmClass : EmClass instance
# @return a tuple with emclass python code, a set containing modules name to import, and a list of python instruction to bootstrap dynamic code, in this order
def generate_classes(model):
    res = ""
    imports = list()
    bootstrap = ""
    # Generating field list for LeObjects generated from EmClass
    for em_class in get_classes(model):
        uid = list()        # List of fieldnames that are part of the EmClass primary key
        parents = list()    # List of parents EmClass
        # Determine pk
        for field in em_class.fields():
            if field.data_handler_instance.is_primary_key():
                uid.append(field.uid)
        # Determine parent for inheritance
        if len(em_class.parents) > 0:
            for parent in em_class.parents:
               parents.append(LeObject.name2objname(parent.uid))
        else:
            parents.append('LeObject')
        datasource_name = em_class.datasource
        
        # Dynamic code generation for LeObject childs classes
        em_cls_code = """
class {clsname}({parents}):
    _abstract = {abstract}
    _fields = None
    _uid = {uid_list}
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = {datasource_name}
    _child_classes = None

""".format(
    clsname = LeObject.name2objname(em_class.uid),
    parents = ', '.join(parents),
    abstract = 'True' if em_class.abstract else 'False',
    uid_list = repr(uid),
    datasource_name = repr(datasource_name),
)
        res += em_cls_code
        # Dyncode fields bootstrap instructions
        bootstrap += """{classname}._set__fields({fields})
{classname}._child_classes = {child_classes}
""".format(
    classname = LeObject.name2objname(em_class.uid),
    fields = '{' + (', '.join(['\n\t%s: %s' % (repr(emfield.uid),data_handler_constructor(emfield)) for emfield in em_class.fields()])) + '}',
    child_classes = '(' + (', '.join([ LeObject.name2objname(emcls.uid) for emcls in model.get_class_childs(em_class.uid)]))+ ')',
)
    bootstrap += "\n"
    return res, set(imports), bootstrap
    
