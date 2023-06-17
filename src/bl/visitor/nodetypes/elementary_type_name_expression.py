'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger

from src.bl.visitor.nodetypes.source_unit import SourceUnit

class ElementaryTypeNameExpression(Node):
    
    def __init__(self, node_info, _previous = None, cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.__type = None
        self.__value = None
        self.__isConstant = None
        self.__isLValue = None
        self.__isPure = None
        self.__lValueRequested = None
        self.id = None
        self.__ETS_node_info(node_info.get('attributes'))
        SourceUnit.insert_operands_info(str(self.id), self)

    def get_is_constant(self):
        return self.__isConstant


    def get_is_lvalue(self):
        return self.__isLValue


    def get_is_pure(self):
        return self.__isPure


    def get_l_value_requested(self):
        return self.__lValueRequested


    def set_is_constant(self, value):
        self.__isConstant = value


    def set_is_lvalue(self, value):
        self.__isLValue = value


    def set_is_pure(self, value):
        self.__isPure = value


    def set_l_value_requested(self, value):
        self.__lValueRequested = value
            
    
    def get_imf(self):
        return self.get_equivalent_elementary_types(self.get_value())
    

    def get_type(self):
        return self.__type


    def get_value(self):
        return self.__value


    def set_type(self, value):
        self.__type = value


    def set_value(self, value):
        self.__value = value
    
    def get_variable_name(self):
        return self.get_value()

    def __ETS_node_info(self, info):
        self.set_type(info.get('type'))
        self.set_value(info.get('value'))
        self.set_is_constant(info.get("isConstant"))
        self.set_is_lvalue(info.get("isLValue"))
        self.set_is_pure(info.get("isPure"))
        self.set_l_value_requested(info.get("lValueRequested"))
        self.id = self.get_ast_id()
        