'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes


class InheritanceSpecifier(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
   
        self.__ETS_node_info(node_info.get('attributes'))
        
        children = node_info.get("children")

        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self, False)
            
    def __ETS_node_info(self, info):
        pass
    