'''
Created on Nov 30, 2020

@author: ACER
'''

import src.bl.visitor.node_processor as ntypes
from src.bl.visitor.node_processor import Node

class PragmaDirective(Node):
    
    def __init__(self, node_info, _previous, cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        