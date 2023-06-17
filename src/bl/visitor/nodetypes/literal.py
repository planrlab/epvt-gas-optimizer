'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node
from src.bl.visitor.nodetypes.source_unit import SourceUnit

class Literal(Node):
    
    def __init__(self, node_info,  _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.value = node_info.get('attributes').get('value')
        self.type = node_info.get('attributes').get('token')
        self.id = self.get_ast_id()
        if _is_cfg_node:
            self.set_cfg_id()
            self.set_name(_previous)
            self.construct_cfg_node(_is_cfg_node)
        
        SourceUnit.insert_operands_info(self.id, self)
        
        
    def get_imf(self):
        return self.value if self.type in["number", "bool"] else '"'+self.value +'"'
    

    def get_value(self):
        return self.value


    def get_type(self):
        return self.type


    def set_value(self, value):
        self.value = value


    def set_type(self, value):
        self.type = value

