'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes

class UserDefinedTypeName(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.__contract_scope = None
        self.__name = None
        self.__referenced_declaration = None
        self.__type  = None


    def get_contract_scope(self):
        return self.__contract_scope


    def get_name(self):
        return self.__name


    def get_referenced_declaration(self):
        return self.__referenced_declaration


    def get_type(self):
        return self.__type


    def set_contract_scope(self, value):
        self.__contract_scope = value


    def set_name(self, value):
        self.__name = value


    def set_referenced_declaration(self, value):
        self.__referenced_declaration = value


    def set_type(self, value):
        self.__type = value


    def __ETS_node_info(self, info):
        pass
