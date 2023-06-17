'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger
from src.bl.visitor.nodetypes.source_unit import SourceUnit
from src.bl.visitor import nodetypes as ntypes

class NewExpression(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        children = node_info.get('children')
        self.data_type = None
        
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), _is_cfg_node)
            self.data_type = child_node.get_type()
            self.used.extend(child_node.used)
            self.dec_def.extend(child_node.dec_def)
        
        SourceUnit.insert_operands_info(str(self.get_ast_id()), self)
    
    
    def get_imf(self):
        return self.get_ast_id()
    
    
    def get_variable_name(self):
        return "new "+self.data_type
    
    
    def get_type(self):
        return "new"