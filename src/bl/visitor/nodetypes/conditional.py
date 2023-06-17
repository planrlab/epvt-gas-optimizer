'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes


class Conditional(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))

        self.__argument_types = None
        self.__is_constant = None
        self.__is__lValue = None
        self.__is_pure = None
        self.__is_lValue_requested = None
        self.__type = None
        
        self.__imf_repr = []
        
        if _is_cfg_node:
            self.set_cfg_id()
                
                
        self.__ETS_node_info(node_info.get('attributes'))
        
        children = node_info.get("children")
        
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self, False)
            self.__imf_repr.append(child_node.get_imf())
            
    
    def get_imf(self):
        return tuple(self.__imf_repr)


    def __ETS_node_info(self, info):
        self.set_argument_types(info.get('argumentTypes'))
        self.set_is_constant(info.get('isConstant'))
        self.set_is__l_value(info.get('isLValue'))
        self.set_is_pure(info.get('isPure'))
        self.set_is_l_value_requested(info.get('lValueRequested'))
        self.set_type(info.get('type'))
        
        
    def get_argument_types(self):
        return self.__argument_types


    def get_is_constant(self):
        return self.__is_constant


    def get_is__l_value(self):
        return self.__is__lValue


    def get_is_pure(self):
        return self.__is_pure


    def get_is_l_value_requested(self):
        return self.__is_lValue_requested


    def get_type(self):
        return self.__type


    def set_argument_types(self, value):
        self.__argument_types = value


    def set_is_constant(self, value):
        self.__is_constant = value


    def set_is__l_value(self, value):
        self.__is__lValue = value


    def set_is_pure(self, value):
        self.__is_pure = value


    def set_is_l_value_requested(self, value):
        self.__is_lValue_requested = value


    def set_type(self, value):
        self.__type = value
        
    