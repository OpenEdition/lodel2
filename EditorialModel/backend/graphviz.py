# -*- coding: utf-8 -*-

import datetime
from EditorialModel.classtypes import EmClassType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.types import EmType
from Lodel.utils.mlstring import MlString

class EmBackendGraphviz(object):

    ## @brief Constructor
    # @param dot_fname str : The filename where we want to save the dot repr of the EM
    def __init__(self, dot_fname):
        self.edges = ""
        self.dot_fname = dot_fname
        #with open(dot_file, 'w+') as dot_fp:
    
    ## @brief Not implementend
    # @warning Not implemented
    def load(self):
        raise NotImplementedError(self.__class__.__name__+' cannot load an EM')

    ## @brief Save an EM in a dot file
    # @param em model : The EM to save
    # @warning hardcoded classtype
    def save(self, em):
        self.edges = ""
        with open(self.dot_fname, 'w') as dotfp:
            dotfp.write("digraph G {\n\trankdir = BT\n")
            
            dotfp.write('subgraph cluster_classtype {\nstyle="invis"\n')
            for ct in [ 'entity', 'entry', 'person' ]:
                dotfp.write('\n\nct%s [ label="classtype %s" shape="tripleoctagon" ]\n'%(ct, ct))
            dotfp.write("}\n")

            
            dotfp.write('subgraph cluster_class {\nstyle="invis"\n')
            for c in em.classes():

                dotfp.write(self._component_node(c, em))
                cn = c.__class__.__name__
                cid = self._component_id(c)
                self.edges += cid+' -> ct%s [ style="dashed" ]\n'%c.classtype
            dotfp.write("}\n")

            #dotfp.write('subgraph cluster_fieldgroup {\nstyle="invis"\n')
            for c in em.components(EmFieldGroup):
                dotfp.write(self._component_node(c, em))
                cn = c.__class__.__name__
                cid = self._component_id(c)
                self.edges += cid+' -> '+self._component_id(c.em_class)+' [ style="dashed" ]\n'
            #dotfp.write("}\n")


            #dotfp.write('subgraph cluster_type {\nstyle="invis"\n')
            for c in em.components(EmType):
                dotfp.write(self._component_node(c, em))
                cn = c.__class__.__name__
                cid = self._component_id(c)
                self.edges += cid+' -> '+self._component_id(c.em_class)+' [ style="dotted" ]\n'
                for fg in c.fieldgroups():
                    self.edges += cid+' -> '+self._component_id(fg)+' [ style="dashed" ]\n'
                for nat in c.superiors():
                    self.edges += cid+' -> '+self._component_id(c.superiors()[nat])+' [ label="%s" color="green" ]'%nat
            #dotfp.write("}\n")

            dotfp.write(self.edges)

            dotfp.write("\n}")
        pass

    @staticmethod
    def _component_id(c):
        return 'emcomp%d'%c.uid

    def _component_node(self, c, em):
        #ret = 'emcomp%d '%c.uid
        ret = "\t"+EmBackendGraphviz._component_id(c)
        cn = c.__class__.__name__
        rel_field = ""
        if cn == 'EmClass':
            ret += '[ label="%s", shape="%s" ]'%(c.name, 'doubleoctagon')
        elif cn == 'EmType' or cn == 'EmFieldGroup':
            ret += '[ label="%s %s '%(cn, c.name)

            cntref = 0
            first = True
            for f in c.fields():
                if ((cn == 'EmType' and f.optional) or (cn == 'EmFieldGroup' and not f.optional)) and f.rel_field_id is None:
                    
                    if not (f.rel_to_type_id is None):
                        rel_node_id = '%s%s'%(EmBackendGraphviz._component_id(c), EmBackendGraphviz._component_id(em.component(f.rel_to_type_id)))

                        rel_node = '\t%s [ label="rel_to_type'%rel_node_id

                        if len(f.rel_to_type_fields()) > 0:
                            #rel_node += '| {'
                            first = True
                            for rf in f.rel_to_type_fields():
                                rel_node += ' | '
                                if first:
                                    rel_node += '{ '
                                    first = False
                                rel_node += rf.name
                        rel_node += '}" shape="record" style="dashed"]\n'

                        rel_field += rel_node

                        ref_node = EmBackendGraphviz._component_id(em.component(f.rel_to_type_id))
                        self.edges += '%s:f%d -> %s [ color="purple" ]\n'%(EmBackendGraphviz._component_id(c), cntref, rel_node_id)
                        self.edges += '%s -> %s [color="purple"]\n'%(rel_node_id, ref_node)

                    ret += '|'
                    if first:
                        ret += ' { '
                        first = False
                    if not (f.rel_to_type_id is None):
                        ret += '<f%d> '%cntref
                        cntref += 1
                    ret += f.name
            ret += '}" shape="record" color="%s" ]'%('blue' if cn == 'EmType' else 'red')
        else:
            return ""
        ret +="\n"+rel_field
        return ret
            
