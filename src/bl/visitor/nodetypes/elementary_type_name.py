'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes

class ElementaryTypeName(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.__name = None
        self.__type = None
        self.__ETS_node_info(node_info.get('attributes'))


    def __ETS_node_info(self, info):
        self.set_type(info.get('type'))
        self.set_name(info.get('name'))


    def get_name(self):
        return self.__name

    
    def get_type(self):
        return self.__type
    

    def set_type(self, value):
        self.__type = value

    
    def set_name(self, name):
        self.__name = name
    