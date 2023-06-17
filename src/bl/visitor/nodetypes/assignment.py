'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes

from src.bl.visitor.nodetypes.optmodules.expressionimf import ExpressionIMF

class Assignment(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.__is_constant = None
        self.__is_lvalue = None
        self.__is_pure = None
        self.__l_value_requested = None
        self.__operator = None
        self.__prefix = None   
        self.type = None
        
        self.s_operator = None
        self.__imf_repr = {"=": []}
        self.__s_imf_repr = None
        
        self.__ETS_node_info(node_info.get('attributes'))

        children = node_info.get('children')
        
        if _is_cfg_node:
            self.set_cfg_id()
            self.construct_cfg_node(_is_cfg_node)
        child = children[0]    
        child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
        
        #defined set
        #print(child.get('name'), child_node)
        self.dec_def.extend(child_node.used)
        
        self.defined_variables = child_node.get_imf()
        self.__imf_repr["="].append(self.defined_variables)
        
        """RValue"""
        child = children[1]
        child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
        
        #used set:
        self.used.extend(child_node.used)
        
        
        if not self.s_operator:
            self.__imf_repr["="].append(child_node.get_imf())
        else:
            self.__s_imf_repr = {self.s_operator: [self.defined_variables]}
            self.used.insert(0, self.defined_variables)
            self.__s_imf_repr[self.s_operator].extend(ExpressionIMF.update_exp_imf(self.s_operator, child_node.get_imf()))         
            self.__imf_repr["="].append(self.__s_imf_repr)
        
        
        
        
    def get_imf(self):
        return self.__imf_repr 
    
    
    def __ETS_node_info(self, info):
        self.set_is_constant(info.get('isConstant'))
        self.set_is_lvalue(info.get('isLValue'))
        self.set_is_pure(info.get('isPure'))
        self.set_l_value_requested(info.get('lValueRequested'))
        self.set_operator(info.get('operator'))
        self.set_prefix(info.get('prefix'))
        self.set_type(info.get('type'))
        
        if self.__operator != "=":
            self.s_operator = self.__operator[:-1]
            self.__s_imf_repr = {self.s_operator: []}
            
            
    def get_is_constant(self):
        return self.__is_constant


    def get_is_lvalue(self):
        return self.__is_lvalue


    def get_is_pure(self):
        return self.__is_pure


    def get_l_value_requested(self):
        return self.__l_value_requested


    def get_operator(self):
        return self.__operator


    def get_prefix(self):
        return self.__prefix


    def get_type(self):
        return self.type


    def set_is_constant(self, value):
        self.__is_constant = value


    def set_is_lvalue(self, value):
        self.__is_lvalue = value


    def set_is_pure(self, value):
        self.__is_pure = value


    def set_l_value_requested(self, value):
        self.__l_value_requested = value


    def set_operator(self, value):
        self.__operator = value


    def set_prefix(self, value):
        self.__prefix = value


    def set_type(self, value):
        self.type = value