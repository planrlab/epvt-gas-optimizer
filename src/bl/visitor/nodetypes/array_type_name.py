'''
Created on Dec 12, 2020

@author: ACER
'''
from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes

class ArrayTypeName(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)    
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.type = None
        self.length = None
        
        self.__ETS_node_info(node_info.get('attributes')) 
        children = node_info.get('children')
        child = children.pop(0)
        child_node = getattr(ntypes, child.get('name'))(child, self, False)
        dt_name = child_node.get_type()
        #TODO need to process to extract user declared type
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self, False)
        self.set_data_type(dt_name)
        
        
    def __ETS_node_info(self, info):
        self.set_length(info.get('length'))
        self.set_type(info.get('type'))    
        
    
    def set_data_type(self, dt_name):
        self.data_type = dt_name
    
    
    def get_data_type(self):
        return self.data_type
    
        
    def get_type(self):
        return self.type


    def get_length(self):
        return self.__length


    def set_type(self, value):
        self.type = value


    def set_length(self, value):
        self.__length = value


