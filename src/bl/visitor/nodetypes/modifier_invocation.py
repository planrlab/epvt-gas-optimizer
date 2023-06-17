'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger

class ModifierInvocation(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
