'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node

class Break(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, False)
        self.set_name("Break")
        self.set_cfg_id("Break")
        b_node, _ = self.get_break_continue()
        self.entry_node = b_node
        self.exit_node = None
        
    def get_imf(self):
        return None, self.get_name()