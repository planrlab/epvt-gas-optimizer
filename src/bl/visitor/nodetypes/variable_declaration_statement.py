'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes

from src.bl.visitor.nodetypes.optmodules.expressionimf import ExpressionIMF

class VariableDeclarationStatement(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        
        self.set_cfg_id()
        self.defined_variable_aid = None
        
        self.__ETS_node_info(node_info.get('attributes'))
        self.__operator = "="
        
        self.__imf_repr = {self.__operator: []}
        
        childrens = node_info.get('children')
        child = childrens.pop(0)
        child_node = getattr(ntypes, child.get('name'))(child, self, False)
        self.data_type = child_node.get_data_type()
        
        self.__imf_repr[self.__operator].extend(ExpressionIMF.update_exp_imf(self.__operator, child_node.get_imf()))
        self.dec_def.extend(child_node.dec_def)
        if len(childrens) > 0:
            child = childrens.pop(0)
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
            self.__imf_repr[self.__operator].extend(ExpressionIMF.update_exp_imf(self.__operator, child_node.get_imf()))
            self.used.extend(child_node.used)
        else:
            self.__imf_repr = child_node.get_imf()

        self.construct_cfg_node(None)
        
            
    def get_imf(self):
        return self.__imf_repr
            
    def __ETS_node_info(self, info):
        self.defined_variable_aid = info.get("assignments")
        
    def __str__(self):
        return "\n imf: " + str(self.get_imf()) + \
            "\n used: " + str(self.used) + \
            "\n defined: " + str(self.dec_def) + \
            "\n source code:" + self.get_source_code()
        