'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes
from src.bl.visitor.nodetypes.optmodules.expressionimf import ExpressionIMF

class BinaryOperation(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))        
        self.__operator = None
        self.type = None
        self.set_name(_previous)
        
        if _is_cfg_node:
            self.set_cfg_id()
        
        self.__ETS_node_info(node_info.get('attributes'))    
        self.__imf_repr = {self.__operator: []}
        children = node_info.get('children')
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
            self.used.extend(child_node.used)
            self.__imf_repr[self.__operator].extend(ExpressionIMF.update_exp_imf(self.__operator, child_node.get_imf()))
        self.logger.info(str(self.get_imf()))
        
        if _is_cfg_node:
            self.construct_cfg_node(_is_cfg_node)
    
    def get_imf(self):
        return self.__imf_repr 
        
        
    def __ETS_node_info(self, info):
        self.set_operator(info.get('operator'))
        self.set_type(info.get('type'))
        
    
    def get_operator(self):
        return self.__operator


    def get_type(self):
        return self.type


    def set_operator(self, value):
        self.__operator = value


    def set_type(self, value):
        self.type = value


    def __str__(self):
        return "\n imf: " + str(self.get_imf()) + \
            "\n used: " + str(self.used) + \
            "\n defined: " + str(self.dec_def) + \
            "\n source code:" + self.get_source_code()

    

    