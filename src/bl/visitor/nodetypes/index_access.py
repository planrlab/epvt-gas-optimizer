'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes


class IndexAccess(Node):
    
    def __init__(self, node_info, _previous=None, cfg_node=False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing ' + self.__class__.__name__ + str(self.get_ast_id()))
        
        self.argumentTypes = None
        self.is_constant = False
        self.is_lvalue = True
        self.is_pure = False
        self.lvalue_requested = False
        self.type = None
        self.__ETS_node_info(node_info.get('attributes'))
        
        children = node_info.get('children')
        
        self.__imf_repr = []
        
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self, False)
            x = child_node.get_imf()
            if isinstance(x, tuple) and len(self.__imf_repr) == 0:
                self.__imf_repr.extend(list(x))
            else: 
                self.__imf_repr.append(child_node.get_imf())
            self.used.extend(child_node.used)
            self.dec_def.extend(child_node.dec_def)
        
    def get_imf(self):
        return tuple(self.__imf_repr)
        
    def get_argument_types(self):
        return self.argumentTypes

    def get_is_constant(self):
        return self.is_constant

    def get_is_lvalue(self):
        return self.is_lvalue

    def get_is_pure(self):
        return self.is_pure

    def get_lvalue_requested(self):
        return self.lvalue_requested

    def get_type(self):
        return self.type

    def set_argument_types(self, value):
        self.argumentTypes = value

    def set_is_constant(self, value):
        self.is_constant = value

    def set_is_lvalue(self, value):
        self.is_lvalue = value

    def set_is_pure(self, value):
        self.is_pure = value

    def set_lvalue_requested(self, value):
        self.lvalue_requested = value

    def set_type(self, value):
        self.type = value

    def __ETS_node_info(self, info):
        self.set_argument_types(info.get('argumentTypes'))
        self.set_is_constant(info.get('isConstant'))
        self.set_is_lvalue(info.get('isLValue'))
        self.set_is_pure(info.get('isPure'))
        self.set_lvalue_requested(info.get('lValueRequested'))
        self.set_type(info.get('type'))
        
