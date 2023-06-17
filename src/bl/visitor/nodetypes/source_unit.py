'''
Created on Dec 21, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes


class SourceUnit(Node):
    
    token_info = dict()
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__)
        self.__contracts = []
        self.set_cfg_id("Source Code")
        self.__class__.token_info = dict()
        self.current_cfg_node = self.construct_cfg_node(None)
        
        children = node_info.get('children')
        
        for child in children[1:]:
            child_node = getattr(ntypes, child.get('name'))(child, _previous, self.current_cfg_node)
            self.__contracts.append(child_node)
        
        
    def get_dgraph(self):
        return self.current_cfg_node
    
    
    def get_contracts(self):
        return self.__contracts
            
            
    @staticmethod       
    def insert_operands_info(_id, obj):
        if _id in SourceUnit.token_info:
            if type(_id) is str:
                return SourceUnit.token_info.get(_id)
        else:
            SourceUnit.token_info[_id] = obj
            
            
    def get_token_info(self):
        return SourceUnit.token_info
    