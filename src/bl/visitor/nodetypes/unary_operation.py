'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes

class UnaryOperation(Node):
    
    def __init__(self, node_info, _previous = None, cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__)

        self.is_constant = None
        self.is_lvalue = None
        self.is_pure = None
        self.l_value_requested = None
        self.operator = None
        self.prefix = None   
        self.type = None
        
        self.__ETS_node_info(node_info.get('attributes'))
        
        self.value = None        
        
        children = node_info.get('children')

        if len(children)==1:
            child = children[0]
            child_node = getattr(ntypes, child.get('name'))(child, _previous)
            
            identifier =  None if len(child_node.used) < 1 else child_node.used[0]
            if identifier:
                self.used.append(identifier)
            
            if self.operator in ['++', '--']:
                self.dec_def.append(identifier)
            
            self.value = child_node.get_imf()
        else:
            raise Exception("Need to handle Special Condition")
        
    
        
    def get_imf(self):
        if self.operator == "--":
            return {"=": [self.value, {'-':[self.value, '1']}]}
        elif self.operator == "++":
            return {"=": [self.value, {'+':[self.value, '1']}]}
    
        elif self.operator == '-':
            return {'u-': [self.value]}
        
        elif self.operator == '+':
            return self.value
        
        elif self.operator == '!':
            return {'!': [self.value]}
        
        elif self.operator == '~':
            return {'~': [self.value]}
        
        else:
            raise Exception("Need to handle " + self.operator)
        
    
        
    def __ETS_node_info(self, info):
        self.set_is_constant(info.get('isConstant'))
        self.set_is_lvalue(info.get('isLValue'))
        self.set_is_pure(info.get('isPure'))
        self.set_l_value_requested(info.get('lValueRequested'))
        self.set_operator(info.get('operator'))
        self.set_prefix(info.get('prefix'))
        self.set_type(info.get('type'))
    
    
    
    def get_is_constant(self):
        return self.is_constant


    def get_is_lvalue(self):
        return self.is_lvalue


    def get_is_pure(self):
        return self.is_pure


    def get_l_value_requested(self):
        return self.l_value_requested


    def get_operator(self):
        return self.operator


    def get_prefix(self):
        return self.prefix


    def get_type(self):
        return self.type


    def set_is_constant(self, value):
        self.is_constant = value


    def set_is_lvalue(self, value):
        self.is_lvalue = value


    def set_is_pure(self, value):
        self.is_pure = value


    def set_l_value_requested(self, value):
        self.l_value_requested = value


    def set_operator(self, value):
        self.operator = value


    def set_prefix(self, value):
        self.prefix = value


    def set_type(self, value):
        self.type = value

