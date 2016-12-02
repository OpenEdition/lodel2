#-
#-  THE CONTENT OF THIS FILE IS DESIGNED TO BE INCLUDED IN DYNAMICALLY
#-  GENERATED CODE
#-
#- All lines that begins with #- will be deleted from dynamically generated
#- code...

##@brief Return a dynamically generated class given it's name
#@param name str : The dynamic class name
#@return False or a child class of LeObject
def name2class(name):
    if name not in dynclasses_dict:
        return False
    return dynclasses_dict[name]


##@brief Return a dynamically generated class given it's name
#@note Case insensitive version of name2class
#@param name str
#@retrun False or a child class of LeObject
def lowername2class(name):
    name = name.lower()
    new_dict = {k.lower():v for k,v in dynclasses_dict.items()}
    if name not in new_dict:
        return False
    return new_dict[name]

##@brief Return the list of authors of a publication

def get_authors(publication):
    texts = publication.data('linked_texts')
    text_objects = Text.get(("%s in (%s)") % ("lodel_id", str(texts).strip('[]')))
    #authors = [str(text.data('linked_persons')).strip('[]') for text in text_objects]
    authors = list()
    for text in text_objects:
        for lp in text.data('linked_persons'):
            authors.append(lp)
    parts = publication.data('linked_parts')
    part_objects = Part.get(("%s in (%s)") % ("lodel_id", str(parts).strip('[]')))
    for part in part_objects:
        for elem in get_authors(part):
            authors.append(elem)

    authors_list = list()
    [authors_list.append(author) for author in authors if not author in authors_list]
    return authors_list

##@brief Trigger dynclasses datasources initialisation
@LodelHook("lodel2_plugins_loaded")
def lodel2_dyncode_datasources_init(self, caller, payload):
    for cls in dynclasses:
        cls._init_datasources()
    LodelContext.expose_modules(globals(), {'lodel.plugin.hooks': ['LodelHook']})
    LodelHook.call_hook("lodel2_dyncode_loaded", __name__, dynclasses)

