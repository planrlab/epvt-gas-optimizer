'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor.nodetypes.source_unit import SourceUnit
from src.bl.visitor import nodetypes as ntypes

class ModifierDefinition(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.mod_name = None
        self.visibility = None
        self.id = None        
        self.__ETS_node_info(node_info.get('attributes'))

    def get_imf(self):
        return None, self.mod_name
    
    
    def get_start_node(self):
        return self.entry_node
    
    
    def __ETS_node_info(self, info):
        self.mod_name = info.get('name')
        self.visibility = info.get('visibility')
        self.id = self.get_ast_id()


    def get_visibility(self):
        return self.visibility
    
    def get_mod_name(self):
        return self.mod_name


   


       