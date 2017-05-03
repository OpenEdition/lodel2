#-*- coding: utf-8 -*-
## @package lodel.leapi.lefactory
import os
import os.path
import functools

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.editorial_model.components': ['EmComponent', 'EmClass', 'EmField',
                                         'EmGroup'],
    'lodel.leapi.leobject': ['LeObject'],
    'lodel.leapi.datahandlers.base_classes': ['DataHandler'],
    'lodel.logger': 'logger'})

## @brief Generates python module code from a given model
# @param model lodel.editorial_model.model.EditorialModel


def dyncode_from_em(model):

    # Generation of LeObject child classes code
    cls_code, bootstrap_instr = generate_classes(model)

    # Header
    imports = """from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.leapi.leobject': ['LeObject'],
    'lodel.leapi.datahandlers.base_classes': ['DataField'],
    'lodel.plugin.hooks': ['LodelHook']})
"""
    # generates the list of all classes in the editorial model
    class_list = [LeObject.name2objname(cls.uid) for cls in get_classes(model)]

    # formating all components of output
    res_code = """#-*- coding: utf-8 -*-
{imports}
{classes}
{bootstrap_instr}
#List of dynamically generated classes
dynclasses = {class_list}
#Dict of dynamically generated classes indexed by name
dynclasses_dict = {class_dict}
{common_code}
""".format(
        imports=imports,
        classes=cls_code,
        bootstrap_instr=bootstrap_instr,
        class_list='[' + (', '.join([cls for cls in class_list])) + ']',
        class_dict='{' + (', '.join(["'%s': %s" % (cls, cls)
                                     for cls in class_list])) + '}',
        common_code=common_code(),
    )
    return res_code

## @brief Returns the content of lodel.leapi.lefactory_common
#
# @return a string


def common_code():
    res = ""
    fname = os.path.dirname(__file__)
    fname = os.path.join(fname, 'lefactory_common.py')
    with open(fname, 'r') as cfp:
        for line in cfp:
            if not line.startswith('#-'):
                res += line
    return res


## @brief return A list of EmClass sorted by dependencies
#
# The first elts in the list depend on nothing, etc.
# @param a list of Emclass instances to be sorted
# @return a list of EmClass instances
def emclass_sorted_by_deps(emclass_list):
    def emclass_deps_cmp(cls_a, cls_b):
        return len(cls_a.parents_recc) - len(cls_b.parents_recc)
    ret = sorted(emclass_list, key=functools.cmp_to_key(emclass_deps_cmp))
    return ret

## @brief Returns a list of EmClass instances that will be represented as LeObject child classes
# @param model : an EditorialModel instance
# @return a list of EmClass instances


def get_classes(model):
    return [cls for cls in emclass_sorted_by_deps(model.classes()) if not cls.pure_abstract]

## @brief Given an EmField returns the data_handler constructor suitable for dynamic code
# @param a EmField instance
# @return a string


def data_handler_constructor(emfield):
    #dh_module_name = DataHandler.module_name(emfield.data_handler_name)+'.DataHandler'
    get_handler_class_instr = 'DataField.from_name(%s)' % repr(emfield.data_handler_name)
    options = []
    for name, val in emfield.data_handler_options.items():
        if name == 'back_reference' and isinstance(val, tuple):
            options.append('{optname}: ({leo_name}, {fieldname})'.format(
                optname=repr(name),
                leo_name=LeObject.name2objname(val[0]),
                fieldname=repr(val[1]),))
        else:
            options.append(repr(name) + ': ' + forge_optval(val))

    return '{handler_instr}(**{{ {options} }})'.format(
        handler_instr=get_handler_class_instr,
        options=', '.join(options))

## @brief Return a python repr of option values
# @param A value of any type which represents option
# @return a string


def forge_optval(optval):
    if isinstance(optval, dict):
        return '{' + (', '.join(['%s: %s' % (repr(name), forge_optval(val)) for name, val in optval.items()])) + '}'

    if isinstance(optval, (set, list, tuple)):
        return '[' + (', '.join([forge_optval(val) for val in optval])) + ']'

    if isinstance(optval, EmField):
        return "{leobject}.data_handler({fieldname})".format(
            leobject=LeObject.name2objname(optval._emclass.uid),
            fieldname=repr(optval.uid)
        )
    if isinstance(optval, EmClass):
        return LeObject.name2objname(optval.uid)

    return repr(optval)

## @brief Generate dyncode from an EmClass
# @param model EditorialModel :
# @return a tuple with emclass python code, a set containing modules name to import, and a list of python instruction to bootstrap dynamic code, in this order


def generate_classes(model):
    res = ""

    bootstrap = ""
    # Generating field list for LeObjects generated from EmClass
    for em_class in get_classes(model):
        logger.info("Generating a dynamic class for %s" % em_class.uid)
        uid = list()        # List for fieldnames that are part of the EmClass primary key
        parents = list()    # List for em_class's parents
        # Determines primary key
        for field in em_class.fields():
            if field.data_handler_instance.is_primary_key():
                uid.append(field.uid)
        # Determines parentsfor inheritance
        if len(em_class.parents) > 0:
            for parent in em_class.parents:
                parents.append(LeObject.name2objname(parent.uid))
        else:
            parents.append('LeObject')
        datasource_name = em_class.datasource

        # Dynamic code generation for LeObject child classes
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
            clsname=LeObject.name2objname(em_class.uid),
            parents=', '.join(parents),
            abstract='True' if em_class.abstract else 'False',
            uid_list=repr(uid),
            datasource_name=repr(datasource_name),
        )
        res += em_cls_code
        # Dyncode fields bootstrap instructions
        child_classes = model.get_class_childs(em_class.uid)
        if len(child_classes) == 0:
            child_classes = 'tuple()'
        else:
            child_classes = '(%s,)' % (', '.join(
                [LeObject.name2objname(emcls.uid) for emcls in child_classes]))
        bootstrap += """{classname}._set__fields({fields})
{classname}._child_classes = {child_classes}
""".format(
            classname=LeObject.name2objname(em_class.uid),
            fields='{' + (', '.join(['\n\t%s: %s' % (repr(emfield.uid),
                                                     data_handler_constructor(emfield)) for emfield in em_class.fields()])) + '}',
            child_classes=child_classes,
        )
    bootstrap += "\n"
    return res, bootstrap
