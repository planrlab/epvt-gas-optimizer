'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger, SourceUnit

from src.bl.visitor import nodetypes as ntypes

class StructDefinition(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        
        self.__canonical_name = None
        self.__name = None
        self.__id = None
        self.__scope = None
        self.__visibility = None       
        self.__type_declaration_only = False
        self.__ETS_node_info(node_info.get('attributes'))
        
        self.construct_cfg_node(None)
        
        if self.__name == "":
            self.type_declaration_only = True
        else:
            self.dec_def.append(self.__id)
              
        if _is_cfg_node:
            self.set_cfg_id()
            self.entry_node = self
            self.exit_node = self
              
        children = node_info.get('children')
        
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
            self.update_used_dec_def(child_node)
            
        SourceUnit.insert_operands_info(str(self.__id), self)

    
    def get_type(self):
        return "function"

    
    def get_variable_name(self):
        return self.get_name()
    
    
    def get_canonical_name(self):
        return self.__canonical_name


    def get_scope(self):
        return self.__scope

    
    def get_visibility(self):
        return self.__visibility


    def get_type_declaration_only(self):
        return self.__type_declaration_only


    def set_canonical_name(self, value):
        self.__canonical_name = value


    def set_scope(self, value):
        self.__scope = value


    def set_visibility(self, value):
        self.__visibility = value


    def set_type_declaration_only(self, value):
        self.__type_declaration_only = value
     
        
    def __ETS_node_info(self, info):
        self.__canonical_name = self.set_canonical_name(info.get("canonicalName"))
        #print("InfoAKS:", info.get("name"), "ID: ", self.get_ast_id())
        self.__name = self.set_name(info.get("name"))
        self.__id = self.get_ast_id()
        self.__scope = self.set_scope(info.get("scope"))
        self.__visibility = self.set_visibility(info.get("visibility"))
          
    
