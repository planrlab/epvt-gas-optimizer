'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node

class Continue(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, False)
        self.set_name("Continue")
        self.set_cfg_id("Continue")
        _, c_node = self.get_break_continue()
        self.entry_node = c_node
        self.exit_node = None
    
    def get_imf(self):
        return None, self.get_name()