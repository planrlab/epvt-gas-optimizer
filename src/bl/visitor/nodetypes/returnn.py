'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes

class Return(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        
        children = node_info.get('children')
        
        self.set_cfg_id()
        
        self.set_name("Return")
        
        self.__imf_repr = None
        
        child = children.pop(0)
        child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
        self.used.extend(child_node.used)
        self.entry_node, self.exit_node = child_node.get_entry_exit_nodes()
        
        self.__imf_repr = child_node.get_imf()
        self.data_type = "return"
        self.construct_cfg_node(_is_cfg_node)

    def get_imf(self):
        return self.__imf_repr
    